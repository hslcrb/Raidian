"""Zero-dependency MCP stdio server for a single, explicitly selected repository.

Messages are newline-delimited UTF-8 JSON-RPC, per the MCP stdio transport.
No logs or banners are ever printed to stdout. All Git writes are opt-in.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import __version__
from .core import GitError, Repository

LEGACY_PROTOCOLS = ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25")
MODERN_PROTOCOL = "2026-07-28"
PROTOCOLS = LEGACY_PROTOCOLS + (MODERN_PROTOCOL,)


def _schema(properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "properties": properties or {}, "required": required or [], "additionalProperties": False}


def _prop(help_text: str, kind: str = "string") -> dict[str, str]:
    return {"type": kind, "description": help_text}


def catalog(allow_write: bool) -> list[dict[str, Any]]:
    tools = [
        ("git_status", "List changed paths, branch and conflict indicators", _schema()),
        ("git_history", "Recent commits with full SHAs", _schema({"limit": _prop("1–200", "integer")})),
        ("git_branches", "List local branches", _schema()),
        ("git_remotes", "List fetch and push remote URLs", _schema()),
        ("git_diff", "Display working-tree or staged diff summary", _schema({"staged": _prop("Staged changes only", "boolean")})),
        ("agent_guide", "Read Raidian operation and safety conventions", _schema()),
    ]
    if allow_write:
        confirm = {"confirm": _prop("Must be true for writes", "boolean")}
        tools.extend([
            ("git_commit", "Stage all changes and commit; empty message creates a Korean Conventional Commit",
             _schema({**confirm, "message": _prop("Optional commit message")}, ["confirm"])),
            ("git_branch_create", "Create a nested chatgpt-extrahigh/feature/detail branch from current branch",
             _schema({**confirm, "feature": _prop("Feature grouping"), "detail": _prop("Short task label")}, ["confirm", "feature", "detail"])),
            ("git_switch", "Switch branch only when working tree is clean",
             _schema({**confirm, "name": _prop("Target local branch")}, ["confirm", "name"])),
            ("git_merge", "Merge branch with --no-ff --no-edit",
             _schema({**confirm, "source": _prop("Branch to merge into active branch")}, ["confirm", "source"])),
            ("git_copy_commit", "Cherry-pick commit into current branch",
             _schema({**confirm, "sha": _prop("Commit SHA")}, ["confirm", "sha"])),
            ("git_revert", "Safely revert one commit with a new commit",
             _schema({**confirm, "sha": _prop("Commit SHA")}, ["confirm", "sha"])),
            ("git_remote_add", "Add an additional Git remote",
             _schema({**confirm, "name": _prop("Remote name"), "url": _prop("Remote URL")}, ["confirm", "name", "url"])),
            ("git_fetch", "Fetch remote refs", _schema(confirm, ["confirm"])),
            ("git_push", "Push active branch, setting upstream if necessary",
             _schema({**confirm, "remote": _prop("Remote name, default origin")}, ["confirm"])),
        ])
    return [{"name": name, "description": desc, "inputSchema": schema} for name, desc, schema in tools]


class Server:
    def __init__(self, repo: Repository, allow_write: bool = False):
        self.repo, self.allow_write = repo, allow_write

    def call(self, name: str, args: dict[str, Any] | None = None) -> Any:
        a = args or {}
        entries = {item["name"]: item for item in catalog(self.allow_write)}
        if name not in entries:
            raise GitError("이 서버에서 허용되지 않은 도구입니다.")
        schema = entries[name]["inputSchema"]
        if set(a) - set(schema["properties"]):
            raise GitError("허용되지 않은 입력 필드가 있습니다.")
        if any(key not in a for key in schema["required"]):
            raise GitError("필수 입력 필드가 없습니다.")
        for key, value in a.items():
            expected = schema["properties"][key]["type"]
            valid = (type(value) is bool if expected == "boolean" else
                     type(value) is int if expected == "integer" else
                     isinstance(value, str))
            if not valid:
                raise GitError(f"{key}: {expected} 값을 입력하세요.")
        if name.startswith("git_") and name not in ("git_status", "git_history", "git_branches", "git_remotes", "git_diff"):
            if a.get("confirm") is not True:
                raise GitError("쓰기 작업은 confirm:true가 필요합니다.")
        operations = {
            "git_status": lambda: {"branch": self.repo.branch(), "files": self.repo.status()},
            "git_history": lambda: self.repo.history(a.get("limit", 25)),
            "git_branches": lambda: {"active": self.repo.branch(), "branches": self.repo.branches()},
            "git_remotes": self.repo.remotes,
            "git_diff": lambda: self.repo.git("diff", *(["--cached"] if a.get("staged") else []), "--stat"),
            "agent_guide": self._guide,
            "git_commit": lambda: self.repo.commit(a.get("message", "")),
            "git_branch_create": lambda: self.repo.nested_branch(a["feature"], a["detail"]),
            "git_switch": lambda: self.repo.switch(a["name"]),
            "git_merge": lambda: self.repo.merge(a["source"]),
            "git_copy_commit": lambda: self.repo.cherry_pick(a["sha"]),
            "git_revert": lambda: self.repo.revert(a["sha"]),
            "git_remote_add": lambda: self.repo.remote_add(a["name"], a["url"]),
            "git_fetch": self.repo.fetch,
            "git_push": lambda: self.repo.push(a.get("remote", "origin")),
        }
        return operations[name]()

    @staticmethod
    def _guide() -> dict[str, Any]:
        from .cli import agent_guide
        return agent_guide()

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        if "id" not in message:  # notifications receive no response
            return None
        request_id = message["id"]
        try:
            method = message.get("method")
            params = message.get("params") or {}
            if not isinstance(params, dict):
                raise ValueError("params must be an object")
            meta = params.get("_meta", {})
            if not isinstance(meta, dict):
                raise ValueError("params._meta must be an object")
            version = meta.get("io.modelcontextprotocol/protocolVersion")
            modern = version is not None or method == "server/discover"
            if modern and version != MODERN_PROTOCOL:
                return {"jsonrpc": "2.0", "id": request_id,
                        "error": {"code": -32022, "message": "Unsupported protocol version",
                                  "data": {"supported": list(PROTOCOLS), "requested": version}}}
            if method == "server/discover":
                data = {"resultType": "complete", "supportedVersions": list(PROTOCOLS),
                        "capabilities": {"tools": {"listChanged": False}},
                        "_meta": {"io.modelcontextprotocol/serverInfo": {
                            "name": "raidian", "version": __version__}},
                        "instructions": "Git tools for one local repository; writes require --allow-write and confirm:true.",
                        "ttlMs": 60000, "cacheScope": "private"}
            elif method == "initialize":
                wanted = params.get("protocolVersion", LEGACY_PROTOCOLS[-1])
                data = {"protocolVersion": wanted if wanted in LEGACY_PROTOCOLS else LEGACY_PROTOCOLS[-1],
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": {"name": "raidian", "version": __version__},
                        "instructions": "Read-only by default. Use --allow-write and confirm:true to modify Git history."}
            elif method == "ping" and not modern:
                data = {}
            elif method == "tools/list":
                data = {"tools": catalog(self.allow_write)}
            elif method == "tools/call":
                name = params.get("name")
                try:
                    payload = self.call(name, params.get("arguments"))
                    value = {"ok": True, "data": payload,
                             "agent_hint": "Check git_status after writes; inspect conflicts before retrying."}
                    data = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}],
                            "structuredContent": value, "isError": False}
                except (GitError, ValueError, OSError) as error:
                    value = {"ok": False, "error": str(error),
                             "agent_hint": "Read git_status; Git conflicts require deliberate manual resolution."}
                    data = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}],
                            "structuredContent": value, "isError": True}
            else:
                return {"jsonrpc": "2.0", "id": request_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}}
            if modern and method != "server/discover":
                data["resultType"] = "complete"
                data["_meta"] = {"io.modelcontextprotocol/serverInfo": {
                    "name": "raidian", "version": __version__}}
            return {"jsonrpc": "2.0", "id": request_id, "result": data}
        except (TypeError, AttributeError, KeyError, ValueError) as error:
            return {"jsonrpc": "2.0", "id": request_id,
                    "error": {"code": -32602, "message": f"Invalid params: {error}"}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Raidian MCP stdio server")
    parser.add_argument("--repo", required=True, help="Only this Git repository will be accessible")
    parser.add_argument("--allow-write", action="store_true", help="Expose mutation tools, each requires confirm:true")
    args = parser.parse_args(argv)
    try:
        server = Server(Repository(args.repo), args.allow_write)
    except GitError as error:
        print(f"Raidian MCP: {error}", file=sys.stderr)
        return 1
    for raw in sys.stdin.buffer:
        try:
            message = json.loads(raw.decode("utf-8"))
            if not isinstance(message, dict):
                continue
            answer = server.handle(message)
            if answer is not None:
                sys.stdout.buffer.write((json.dumps(answer, ensure_ascii=False) + "\n").encode("utf-8"))
                sys.stdout.buffer.flush()
        except (UnicodeError, ValueError, TypeError) as error:
            print(f"Raidian MCP: bad input: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
