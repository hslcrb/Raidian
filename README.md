# Raidian · 레이디안

> **The little Git workbench.** 작은 도구로, 더 명료하게. Git이 누구에게나 편안해지는 순간.

**Raidian** is a minimal, Korean-friendly Git desktop app built with **Python + Tkinter**. Burgundy and vivid red are its visual signature: a soft pill-shaped interface, readable filenames, practical keyboard shortcuts and a common backend for humans and AI agents.

![Git](https://img.shields.io/badge/Git-2.x-551128?logo=git&logoColor=white) ![Python](https://img.shields.io/badge/Python-3.10%2B-A72146?logo=python&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-551128)

## Features

| Human-friendly GUI | Agent-friendly automation |
| --- | --- |
| UTF-8 + Korean CP949 fallback | JSON-formatted CLI (`--json`) |
| File changes and commit history | Interactive `raidian shell` |
| Commit with automatic fallback message | MCP stdio server with default read-only mode |
| Fast push/fetch, GitHub PR viewing with `gh` | Explicit `--allow-write` and `confirm:true` for mutations |
| Named branch creation and switching | Safe `cherry-pick`/`revert`, no forced rewriting |
| Merge preserving history with `--no-ff` | Multi-remote management and consistent error messages |

### Quick start

```sh
python -m raidian gui
python -m raidian --repo . --json status
python -m raidian --repo . commit
python -m raidian --repo . branch-child feature better-korean
python -m raidian --repo . merge feature-branch --yes
python -m raidian --repo . gh-prs
python -m raidian shell
python -m raidian.mcp --repo .
```

Or install from GitHub:

```sh
git clone --depth 1 https://github.com/hslcrb/Raidian.git
cd Raidian
python -m pip install -e .
raidian gui
raidian --json doctor
```

> **Requirements:** Python 3.10+, Git on PATH; `gh` is optional for GitHub pull requests. Packaging Python into `Raidian.exe` does not package `git.exe` or `gh.exe`. Windows users can install Git for Windows and GitHub CLI separately.

### Windows portable build

On a **Windows** development machine, run `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`. The script runs tests and packages `dist/Raidian.exe` with PyInstaller. Use `gh release create v0.1.0 dist/Raidian.exe --title 'Raidian v0.1.0'` once the binary is tested. No GitHub Actions run: the included workflow is fully commented out.

### Brand & design

- Burgundy `#551128` (identity), crimson `#A72146` (action), warm pink `#FCECEF` (affordance), paper `#FFFFFF`, background `#F8F5F5`.
- One primary commit CTA, explicitly labeled secondary actions, soft rounded pill controls, and no hidden destructive history deletion.
- Shortcut examples: **Ctrl+O** open repo, **Ctrl+Enter** commit, **Ctrl+Shift+Enter** commit and push, **F5** refresh, **Alt+B** create branch, **Alt+P** push.
- The font attachment was not visible in this session. `assets/fonts` is available for legally redistributable `.ttf` files; default rendering falls back to Korean-capable system fonts. Font size and spacing prioritize legibility.

### Agent guide

See [agent and MCP contract](docs/ARCHITECTURE.md). Automation can use `raidian --json agent-guide`; every UI action has a visible label, and the MCP server provides machine-readable errors and tool descriptions. Git history rewrites and automatic force pushes are deliberately unsupported. The text of an empty commit message is generated from the change type, never an LLM hallucination.

### Development

```sh
python -m unittest discover -s tests -v
python -m compileall -q raidian
```

### Community

MIT licensed. PRs, accessibility feedback, Korean Windows encoding bug reports and UX proposals are welcome. See [contributing](CONTRIBUTING.md) and [security policy](SECURITY.md).
