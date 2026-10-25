# Raidian architecture & agent contract

- `raidian/core.py`: single Git execution layer; `subprocess` arguments, no shell; UTF-8 plus CP949 fallback.
- `raidian/gui.py`: Tkinter/ttk UI, accessible text labels, keyboard actions, pill buttons, width-aware layout, background Git worker.
- `raidian/cli.py`: argparse + interactive shell, Korean messages and JSON output.
- `raidian/mcp.py`: lightweight MCP JSON-RPC over UTF-8 stdio, restricted to a chosen local repository. Exposes read-only tools unless explicitly launched with `--allow-write`; each mutation then requires `confirm:true`.

## Safety, semantics and limitations

- Merge is `git merge --no-ff --no-edit`; CLI requires `--yes`, GUI requires confirmation.
- A `chatgpt-extrahigh/group/detail` name is a *namespace*, not an actual parent-child pointer. Git prohibits simultaneous refs `a` and `a/b` and does not encode parent branches in names. Raidian branches from the current (or specified) commit and records ancestry in Git commits.
- `copy-commit` is `cherry-pick`, adding an equivalent commit on the destination branch rather than rewriting history.
- `revert` creates a new inverse commit; individual historical commits are not deleted. Deleting one past commit requires rebasing history and may invalidate published signatures and collaborators' refs; intentionally omitted.
- Working tree must be clean before checkout, merge, cherry-pick, revert and pull. Do not auto-resolve conflicts without inspecting them.
- Git and optional `gh` are external dependencies even with a standalone Python EXE. Authentication remains with Git Credential Manager / gh.
- `--json` is intended for automation. MCP sends only JSON-RPC messages on stdout.
- The CLI is not an unrestricted shell runner. The MCP only permits cataloged operations; do not expose to untrusted clients with write mode.

## Agent interface sample

```sh
raidian --repo 'C:/path/to/repo' --json status
raidian --repo 'C:/path/to/repo' --json agent-guide
raidian --repo 'C:/path/to/repo' --json branch-child feature korean-paths
raidian-mcp --repo 'C:/path/to/repo'
```

MCP client config (read-only):

```json
{"mcpServers":{"raidian":{"command":"raidian-mcp","args":["--repo","C:/path/to/repo"]}}}
```

To allow writes, add `--allow-write` and require a human confirmation before every `confirm:true` call. There is no arbitrary command execution tool.

## Release policy

Workflow YAML is fully commented out. Make Windows EXEs on Windows, verify them on Windows, then upload via GitHub release UI or `gh release create v0.1.0 dist/Raidian.exe --title 'Raidian v0.1.0'`. Linux cannot produce a validated native Windows PyInstaller binary using PyInstaller alone.
