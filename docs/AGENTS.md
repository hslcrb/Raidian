# Raidian AI Agent / Computer Use / MCP reference

> **Principle:** GUI and CLI are first-class, the Git engine is singular, and agent write access is a **privilege**, not a default.

## Interfaces

| Interface | Entry point | Designed for |
| --- | --- | --- |
| Tkinter GUI | `python -m raidian gui` or `Raidian.exe` | Computer Use and humans, accessible visible actions |
| CLI | `raidian --repo PATH --json status` | Deterministic tool invocations and logging |
| Interactive CLI | `raidian shell` | Human-in-the-loop command discovery |
| MCP stdio | `python -m raidian.mcp --repo PATH` | JSON-RPC tools within ONE selected repository |
| Portable console | `Raidian-CLI.exe [arguments]`, `Raidian-CLI.exe mcp --repo PATH` | No Python install needed on Windows |

## CLI guidance

1. Begin with `--json doctor` and `--json agent-guide`. Both commands are available without an open repository.
2. Prefer `--json status` to inspect modifications and the active branch.
3. For changes, explicitly choose message and target branch. `commit` stages **all** changes by default.
4. `merge`, `copy-commit`, `revert`, `remote-remove` and `gh-pr-create` require `--yes` as action acknowledgment.
5. A blank commit message results in a deterministic Korean conventional-commit message. This **does not** summarize diff content via a model.
6. Output uses UTF-8 JSON with `ensure_ascii=False`; nonzero exit codes signal Git errors. Process timeouts prevent endless hanging in the engine.

Example:

```powershell
Raidian-CLI.exe --json doctor
Raidian-CLI.exe --repo 'C:\work\내 프로젝트' --json status
Raidian-CLI.exe --repo 'C:\work\내 프로젝트' --json log --limit 5
Raidian-CLI.exe --repo 'C:\work\내 프로젝트' --json branch-child docs readme-refresh
Raidian-CLI.exe --repo 'C:\work\내 프로젝트' --json merge main --yes
```

## MCP stdio

A line-delimited JSON-RPC server via UTF-8 stdin/stdout; diagnostics go to stderr only. Example client configuration:

```json
{
  "mcpServers": {
    "raidian": {
      "command": "C:\\Apps\\Raidian\\Raidian-CLI.exe",
      "args": ["mcp", "--repo", "C:\\work\\내 프로젝트"]
    }
  }
}
```

- MCP handshake era (`initialize`) supports 2024-11-05 through **2025-11-25**; modern **2026-07-28** stateless era adds `server/discover`, per-request `_meta`, `resultType`, and version mismatch handling. The minimal stdio implementation does not offer optional transport extensions.
- Both eras share `tools/list` and `tools/call`; only legacy mode supports `ping`. Protocol support follows the server's `PROTOCOLS` list.
- Without `--allow-write`, mutation tools are not advertised and are rejected if called.
- With `--allow-write`, each mutating call must contain a literal JSON Boolean `"confirm": true`; strings like `"true"` must not count as approval.
- **Do not imply that a model's `confirm:true` proves a human approved a write.** Trust boundaries are controlled by the MCP client and launcher. Grant access only to trusted agents, local repositories, and OS-level permissions.
- This is *not* a general-purpose terminal and cannot arbitrarily run `git` arguments.

The server is pinned to the repository specified at startup. The `--repo` argument is an OS path, not a URI; do not accept repository path input supplied by untrusted prompts.

## Computer Use conventions

- Locate controls by visible labels (`폴더 열기`, `커밋`, `푸시`, `병합 · no-ff`) and inspect the status bar before subsequent actions.
- The buttons can be focused by Tab and activated with Enter/Space. Native entry and tree widgets expose standard focus/selection concepts.
- On narrow windows the controls wrap and change position; do not hard-code screen coordinates.
- Confirm destructive-sounding operations via the GUI dialog; never automatically dismiss errors and retry merges.
- Read actual changes before commit. Raidian deliberately does not issue arbitrary LLM prompts, download models, or silently submit repository text to external services.

## Human-readable machine hints

`--json agent-guide` enumerates safe defaults and command examples. The GUI status line similarly explains the state and meaning of history actions. No internet connection is needed for local Git operations.

## Limits

- MCP is intentionally minimal rather than a complete implementation of all GitHub or Git internals.
- GitHub PR integration delegates to externally installed `gh` and its authentication.
- Writing requires explicit trust; not a sandbox, not an OS security boundary.
- No force-push, arbitrary deletion of published commits, broad filesystem scan, arbitrary shell, or automatically resolved conflicts.
