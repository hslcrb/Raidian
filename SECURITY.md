# Security policy

Report vulnerabilities privately via the repository's GitHub security advisory feature when available, rather than opening a public exploit issue. Raidian invokes installed `git`/`gh` with `shell=False`; read-only MCP is the default and Git history rewriting is omitted. Git and GitHub CLI credentials should be managed by their official helpers. Never post credentials in logs, screenshots or issues. The app is experimental; use test repositories when evaluating new release builds.
