"""Single portable console entrypoint for Raidian CLI and MCP.

Examples:
  Raidian-CLI.exe --json doctor
  Raidian-CLI.exe --repo C:\\repo --json status
  Raidian-CLI.exe mcp --repo C:\\repo
"""
from __future__ import annotations

import sys

from raidian.cli import main as cli_main
from raidian.mcp import main as mcp_main


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "mcp":
        return mcp_main(argv[1:])
    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
