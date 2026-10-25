# Raidian v0.1.0 · 첫 장밋빛 Git 작업실 🌷

> **Release candidate notes, not proof of a published release.** Publish only after actual Windows build and QA.

### New

- Minimal Python 3.10+ / Tkinter Git GUI with burgundy/cherry identity and keyboard controls.
- Deterministic UTF-8/CP949-safe Korean status and commit messages.
- Default history-preserving no-ff merges, branch naming, cherry-pick, revert, multiple remotes.
- CLI, interactive prompt, structured JSON API, `gh`-delegated GitHub integration.
- Minimal MCP stdio server: reads by default; opt-in writes with explicit per-call confirmation.
- Hand-drawn Ruby mascot, brand SVGs and reproducible Windows `.ico` generator.
- Windows portable dual-binary build scripts (PyInstaller + optional Nuitka/MinGW), SHA256 manifests and release gate checklist.

### Security & compatibility

- Git for Windows is a **required external** application; `gh` is optional and authenticated separately.
- No automatic force-push, history deletion, credential capture or untrusted shell execution.
- No bundled custom font until the original font and redistribution rights are verified.
- Release should be treated as **pre-release** until Windows execution and accessibility checks pass.

### Thanks

Tiny Git. Clear history. Happy commits. ♥
