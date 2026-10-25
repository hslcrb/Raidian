"""Shared, dependency-free Git engine for GUI, CLI and MCP.

All commands are argument arrays (never shell=True). Destructive history rewriting
is intentionally excluded; reverting is the safe, auditable alternative.
"""
from __future__ import annotations

import json
import locale
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any


class GitError(RuntimeError):
    """A meaningful Git error that can be shown to a human or an agent."""

    def __init__(self, message: str, code: int = 1):
        super().__init__(message.strip() or "Git 명령을 완료할 수 없습니다.")
        self.code = code


def decode(raw: bytes) -> str:
    """Decode Git's UTF-8 output, with a Windows Korean-console fallback."""
    for encoding in dict.fromkeys(("utf-8-sig", "cp949", locale.getpreferredencoding(False))):
        try:
            return raw.decode(encoding)
        except (UnicodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def _execute(binary: str, args: list[str], cwd: Path, timeout: int = 90) -> str:
    if shutil.which(binary) is None:
        raise GitError(f"{binary} 실행 파일이 없습니다. PATH 설정을 확인하세요.")
    environment = os.environ.copy()
    environment.update({"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"})
    if os.name == "nt":
        environment["PYTHONUTF8"] = "1"
    try:
        result = subprocess.run(
            [binary, *args], cwd=str(cwd), env=environment,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False, shell=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise GitError(f"{binary} 실행 오류: {error}") from error
    output = decode(result.stdout)
    if result.returncode:
        detail = decode(result.stderr).strip() or output.strip()
        raise GitError(detail or f"{binary} 종료 코드: {result.returncode}", result.returncode)
    return output.strip("\n")


class Repository:
    def __init__(self, path: str | Path = "."):
        requested = Path(path).expanduser().resolve()
        if not requested.exists():
            raise GitError(f"폴더를 찾을 수 없습니다: {requested}")
        root = _execute("git", ["rev-parse", "--show-toplevel"], requested).strip()
        self.path = Path(root).resolve()

    @classmethod
    def init(cls, path: str | Path) -> "Repository":
        root = Path(path).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        _execute("git", ["init", "-b", "main"], root)
        return cls(root)

    def git(self, *args: str, timeout: int = 90) -> str:
        return _execute("git", ["-c", "core.quotepath=false", "-c", "i18n.logOutputEncoding=utf-8", *args], self.path, timeout)

    def gh(self, *args: str) -> str:
        return _execute("gh", list(args), self.path)

    def branch(self) -> str:
        return self.git("branch", "--show-current").strip() or "(detached HEAD)"

    def branches(self) -> list[str]:
        return [s for s in self.git("branch", "--format=%(refname:short)").splitlines() if s]

    def status(self) -> list[dict[str, str]]:
        # -z protects spaces, literal quotes, Korean paths and filenames with newlines.
        raw = self.git("status", "--porcelain=v1", "-z", "--untracked-files=normal")
        items = raw.split("\0")
        result: list[dict[str, str]] = []
        index = 0
        while index < len(items):
            item = items[index]
            index += 1
            if not item:
                continue
            if len(item) < 4 or item[2] != " ":
                raise GitError("Git 상태 결과를 해석할 수 없습니다.")
            xy, path = item[:2], item[3:]
            entry = {"state": xy, "path": path}
            if "R" in xy or "C" in xy:
                if index < len(items):
                    entry["from"] = items[index]
                    index += 1
            result.append(entry)
        return result

    def history(self, limit: int = 25) -> list[dict[str, str]]:
        if not 1 <= limit <= 200:
            raise GitError("기록 조회 개수는 1~200이어야 합니다.")
        try:
            raw = self.git("log", f"-{limit}", "--date=short", "--format=%H%x1f%an%x1f%ad%x1f%s%x1e")
        except GitError as error:
            if "does not have any commits yet" in str(error) or "your current branch" in str(error).lower():
                return []
            raise
        records = []
        for line in raw.split("\x1e"):
            parts = line.strip().split("\x1f")
            if len(parts) == 4:
                records.append(dict(zip(("sha", "author", "date", "message"), parts)))
        return records

    def remotes(self) -> list[dict[str, str]]:
        entries = []
        for line in self.git("remote", "-v").splitlines():
            match = re.match(r"^(\S+)\s+(.+?)\s+\((fetch|push)\)$", line)
            if match:
                entries.append({"name": match[1], "url": match[2], "kind": match[3]})
        return entries

    def snapshot(self) -> dict[str, Any]:
        return {"repository": str(self.path), "branch": self.branch(),
                "files": self.status(), "history": self.history(), "remotes": self.remotes()}

    def ensure_clean(self) -> None:
        if self.status():
            raise GitError("먼저 변경 사항을 커밋하거나 보관하세요. 작업 트리를 덮어쓰지 않습니다.")

    def automatic_message(self) -> str:
        files = self.status()
        if not files:
            raise GitError("커밋할 변경 사항이 없습니다.")
        codes = [f["state"] for f in files]
        if all("D" in code for code in codes):
            return "chore: 삭제된 파일 정리"
        if all(Path(f["path"]).suffix.lower() in {".md", ".rst"} for f in files):
            return "docs: 문서 업데이트"
        if all(code == "??" or "A" in code for code in codes):
            return "feat: 새 파일 추가"
        if all("R" in code for code in codes):
            return "refactor: 파일 구조 정리"
        return "chore: 변경 사항 업데이트"

    def commit(self, message: str = "", stage_all: bool = True) -> str:
        if not self.status():
            raise GitError("변경 사항이 없어 커밋하지 않았습니다.")
        message = message.strip() or self.automatic_message()
        if not message or "\0" in message:
            raise GitError("커밋 메시지를 확인하세요.")
        if stage_all:
            self.git("add", "--all")
        return self.git("commit", "-m", message)

    def create_branch(self, name: str, start: str | None = None, switch: bool = True) -> str:
        name = name.strip()
        if not name or "\n" in name:
            raise GitError("올바른 브랜치 이름을 입력하세요.")
        self.git("check-ref-format", "--branch", name)
        if switch:
            self.ensure_clean()
        if switch:
            return self.git("switch", "-c", name, *([start] if start else []))
        return self.git("branch", name, *([start] if start else []))

    def nested_branch(self, feature: str, detail: str, base: str | None = None) -> str:
        # The named levels describe lineage; Git cannot have both 'a' and 'a/b' refs.
        def segment(value: str) -> str:
            token = re.sub(r"[^\w.\-]+", "-", value.strip(), flags=re.UNICODE).strip(".-")
            if not token or token in {".", ".."}:
                raise GitError("브랜치 단계의 이름을 확인하세요.")
            return token
        name = f"chatgpt-extrahigh/{segment(feature)}/{segment(detail)}"
        self.create_branch(name, start=base)
        return name

    def switch(self, name: str) -> str:
        self.ensure_clean()
        if not name or name.startswith("-"):
            raise GitError("유효한 브랜치 이름을 입력하세요.")
        return self.git("switch", "--", name)

    def merge(self, source: str) -> str:
        self.ensure_clean()
        if not source or source.startswith("-"):
            raise GitError("병합할 브랜치를 확인하세요.")
        if source == self.branch():
            raise GitError("현재 브랜치를 자기 자신과 병합할 수 없습니다.")
        return self.git("merge", "--no-ff", "--no-edit", "--", source)

    def _commit_reference(self, sha: str) -> str:
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha):
            raise GitError("7~40자의 커밋 SHA가 필요합니다.")
        return sha

    def cherry_pick(self, sha: str) -> str:
        self.ensure_clean()
        return self.git("cherry-pick", "--no-edit", self._commit_reference(sha))

    def revert(self, sha: str) -> str:
        self.ensure_clean()
        return self.git("revert", "--no-edit", self._commit_reference(sha))

    def remote_add(self, name: str, url: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) or not url or any(c in url for c in "\r\n\0") or url.startswith("-"):
            raise GitError("원격 이름과 주소를 확인하세요.")
        return self.git("remote", "add", name, url)

    def remote_remove(self, name: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
            raise GitError("원격 이름을 확인하세요.")
        return self.git("remote", "remove", name)

    @staticmethod
    def _remote_name(remote: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", remote):
            raise GitError("원격 이름이 올바르지 않습니다.")
        return remote

    def fetch(self, remote: str = "--all") -> str:
        if remote == "--all":
            return self.git("fetch", "--all", "--prune", timeout=180)
        return self.git("fetch", "--prune", self._remote_name(remote), timeout=180)

    def push(self, remote: str = "origin") -> str:
        remote = self._remote_name(remote)
        branch = self.branch()
        if branch.startswith("("):
            raise GitError("분리된 HEAD에서는 자동 푸시하지 않습니다.")
        upstream = self.git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}") if self.has_upstream() else ""
        if upstream and upstream.split("/", 1)[0] == remote:
            return self.git("push", remote, timeout=180)
        return self.git("push", "--set-upstream", remote, branch, timeout=180)

    def has_upstream(self) -> bool:
        try:
            self.git("rev-parse", "--abbrev-ref", "@{upstream}")
            return True
        except GitError:
            return False

    def pull(self, remote: str = "origin") -> str:
        self.ensure_clean()
        return self.git("pull", "--no-rebase", "--no-ff", self._remote_name(remote), timeout=180)

    def github_prs(self) -> list[dict[str, Any]]:
        raw = self.gh("pr", "list", "--json", "number,title,headRefName,url", "--limit", "25")
        return json.loads(raw)

    def github_pr_create(self, base: str = "main") -> str:
        return self.gh("pr", "create", "--fill", "--base", base)
