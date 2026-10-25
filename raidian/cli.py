"""Command-line and interactive interface to the same engine used by the GUI."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
from typing import Any

from . import __version__
from .core import GitError, Repository


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="raidian", description="Raidian · 가볍고 쉬운 Git 작업실")
    p.add_argument("--repo", default=".", help="저장소 경로 (기본: 현재 디렉터리)")
    p.add_argument("--json", action="store_true", help="자동화용 UTF-8 JSON 출력")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="action")
    sub.add_parser("gui", help="GUI 열기")
    init = sub.add_parser("init", help="Git 저장소 시작")
    init.add_argument("path")
    sub.add_parser("status", help="변경 파일 보기")
    log = sub.add_parser("log", help="커밋 이력")
    log.add_argument("--limit", type=int, default=25)
    sub.add_parser("branches", help="브랜치 목록")
    create = sub.add_parser("branch-create", help="새 브랜치")
    create.add_argument("name")
    create.add_argument("--from", dest="base")
    create.add_argument("--no-switch", action="store_true")
    child = sub.add_parser("branch-child", help="규칙에 맞는 계층형 브랜치")
    child.add_argument("feature")
    child.add_argument("detail")
    child.add_argument("--from", dest="base")
    switch = sub.add_parser("switch", help="브랜치 이동")
    switch.add_argument("name")
    commit = sub.add_parser("commit", help="변경 사항 커밋 (메시지 없으면 자동 제안)")
    commit.add_argument("-m", "--message", default="")
    commit.add_argument("--no-stage", action="store_true", help="현재 staged 파일만 커밋")
    push = sub.add_parser("push", help="현재 브랜치 푸시")
    push.add_argument("--remote", default="origin")
    fetch = sub.add_parser("fetch", help="원격에서 가져오기")
    fetch.add_argument("--remote", default="--all")
    pull = sub.add_parser("pull", help="--no-ff 기반 원격 병합")
    pull.add_argument("--remote", default="origin")
    for name, help_text in (("merge", "기본 --no-ff 병합"),
                            ("copy-commit", "이전 커밋을 새 커밋으로 복사(cherry-pick)"),
                            ("revert", "특정 커밋의 변경만 되돌리는 새 커밋")):
        c = sub.add_parser(name, help=help_text)
        c.add_argument("value", help="브랜치 이름 또는 커밋 SHA")
        c.add_argument("--yes", action="store_true", help="작업 내용을 확인함")
    sub.add_parser("remote-list", help="원격 목록")
    remote = sub.add_parser("remote-add", help="원격 추가")
    remote.add_argument("name")
    remote.add_argument("url")
    remove = sub.add_parser("remote-remove", help="원격 제거")
    remove.add_argument("name")
    remove.add_argument("--yes", action="store_true")
    sub.add_parser("gh-prs", help="GitHub PR 목록 (gh 설치 필요)")
    pr = sub.add_parser("gh-pr-create", help="현재 브랜치의 PR 만들기")
    pr.add_argument("--base", default="main")
    pr.add_argument("--yes", action="store_true")
    sub.add_parser("doctor", help="Git, gh 및 환경 점검")
    sub.add_parser("agent-guide", help="AI 에이전트를 위한 기계 판독 가이드")
    sub.add_parser("shell", help="대화형 명령 프롬프트")
    return p


def agent_guide() -> dict[str, Any]:
    return {
        "application": "Raidian", "version": __version__, "encoding": "UTF-8",
        "interfaces": {"gui": "raidian gui", "cli": "raidian --repo PATH --json status",
                       "interactive": "raidian shell", "mcp": "raidian-mcp --repo PATH"},
        "defaults": {"merge": "--no-ff --no-edit", "empty_message": "auto generated Korean Conventional Commit",
                     "history_delete": "safe revert, no force push", "mcp_writes": "disabled without --allow-write"},
        "hints": ["--repo is a global flag placed before a subcommand", "Use --json for machine output",
                  "Risky CLI operations need --yes", "MCP tools/call writes need confirm:true",
                  "Never assume a branch name with / represents a Git parent relationship",
                  "Prefer status before committing and inspect errors before retrying"],
    }


def doctor() -> dict[str, Any]:
    import tkinter
    return {"git": shutil.which("git"), "gh": shutil.which("gh"),
            "tk": str(tkinter.TkVersion), "python": sys.version.split()[0],
            "portable": "Git and (optionally) gh must exist on PATH"}


def dispatch(a: argparse.Namespace) -> Any:
    if a.action in (None, "gui"):
        from .gui import main as gui_main
        gui_main(initial_repo=a.repo)
        return "GUI started"
    if a.action == "shell":
        interactive(a.repo)
        return "종료했습니다."
    if a.action == "agent-guide":
        return agent_guide()
    if a.action == "doctor":
        return doctor()
    if a.action == "init":
        return {"repository": str(Repository.init(a.path).path)}
    repo = Repository(a.repo)
    match a.action:
        case "status": return {"branch": repo.branch(), "files": repo.status()}
        case "log": return repo.history(a.limit)
        case "branches": return {"active": repo.branch(), "branches": repo.branches()}
        case "branch-create": return repo.create_branch(a.name, a.base, not a.no_switch)
        case "branch-child": return repo.nested_branch(a.feature, a.detail, a.base)
        case "switch": return repo.switch(a.name)
        case "commit": return repo.commit(a.message, not a.no_stage)
        case "push": return repo.push(a.remote)
        case "fetch": return repo.fetch(a.remote)
        case "pull": return repo.pull(a.remote)
        case "remote-list": return repo.remotes()
        case "remote-add": return repo.remote_add(a.name, a.url)
        case "remote-remove":
            confirm(a.yes)
            return repo.remote_remove(a.name)
        case "merge":
            confirm(a.yes)
            return repo.merge(a.value)
        case "copy-commit":
            confirm(a.yes)
            return repo.cherry_pick(a.value)
        case "revert":
            confirm(a.yes)
            return repo.revert(a.value)
        case "gh-prs": return repo.github_prs()
        case "gh-pr-create":
            confirm(a.yes)
            return repo.github_pr_create(a.base)
    raise GitError(f"알 수 없는 명령: {a.action}")


def confirm(yes: bool) -> None:
    if not yes:
        raise GitError("이 작업은 이력에 영향을 줍니다. 확인했다면 --yes를 추가하세요.")


def interactive(path: str = ".") -> None:
    current = path
    print("Raidian 명령 셸. 도움말: help / 종료: exit")
    while True:
        try:
            line = input("raidian> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line in ("exit", "quit"):
            break
        if line in ("help", "?"):
            parser().print_help()
            continue
        try:
            argv = shlex.split(line, posix=os.name != "nt")
            if os.name == "nt":
                argv = [item[1:-1] if item.startswith('"') and item.endswith('"') else item for item in argv]
            if argv and argv[0] == "cd" and len(argv) == 2:
                current = str(Path(argv[1]).expanduser().resolve())
                print(current)
                continue
            opts = parser().parse_args(["--repo", current, *argv])
            print(json.dumps(dispatch(opts), ensure_ascii=False, indent=2))
        except (GitError, ValueError, SystemExit) as error:
            print(f"오류: {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    a = parser().parse_args(argv)
    try:
        value = dispatch(a)
        if value != "GUI started":
            if a.json or not isinstance(value, str):
                print(json.dumps({"ok": True, "data": value}, ensure_ascii=False, indent=2))
            else:
                print(value)
        return 0
    except (GitError, OSError, ValueError) as error:
        if a.json:
            print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        else:
            print(f"오류: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
