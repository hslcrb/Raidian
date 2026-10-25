# Manual release playbook

Raidian intentionally keeps GitHub Actions **fully commented out**. Publishing is an explicit, manual maintainer operation, never a side effect of a commit. No credentials, font binaries or hidden build artifacts belong in Git.

## Release gates

- [ ] All intended PRs merged into `main` with merge commits (GitHub merge method `merge`; not squash/rebase).
- [ ] Unit tests and compile checks passing on source tree.
- [ ] Windows portable ZIP built with Windows Python using `scripts/build_windows.ps1`.
- [ ] TWO Windows AMD64 PE executables tested (`Raidian.exe`, `Raidian-CLI.exe`).
- [ ] GUI manually opened on **real Windows** and text including Hangul verified.
- [ ] CLI/MCP smoke tests and read-only/confirmation behaviors validated.
- [ ] Included fonts independently checked for embedding/redistribution permission.
- [ ] `BUILD-INFO.json` records exact reviewed `main` SHA and Windows build tool.
- [ ] `python -m scripts.validate_release` passes (both EXEs, ZIP, SHA256SUMS, source SHA).
- [ ] SHA256SUMS matches all artifacts and is included in release assets.
- [ ] LICENSE and README-PORTABLE.txt included in ZIP.
- [ ] Release notes reviewed for accuracy; experimental features/limitations disclosed.
- [ ] Tag points at the reviewed `main` commit.

## Publishing from trusted Windows PowerShell

```powershell
git switch main
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
powershell -ExecutionPolicy Bypass -File scripts/publish_release.ps1 -Tag v0.1.0 -Prerelease -WindowsQaPassed
```

The publisher checks auth, clean `main` status, Git SHA provenance, ZIP, x64 PE headers, the checksum values and an explicit `-WindowsQaPassed` human attestation. It uses `gh release create` with `--target <exact built SHA>` and **refuses an existing release** to prevent silent overwrite. It uploads both EXEs, the portable ZIP, checksum manifest and build metadata. `-WindowsQaPassed` is a maintainer assertion, **not automatic proof** that GUI QA happened. Verify on <https://github.com/hslcrb/Raidian/releases>.

## Supported public statements

- Source tests passed on Linux → "소스 테스트 통과".
- `verify_pe.py` passed → "PE x64 파일 형식 확인".
- Windows GUI manual QA passed → "Windows GUI 기본 동작 확인".
- GitHub Release API/CLI reports uploaded asset → "GitHub Release 게시 완료".

**Do not conflate these gates.** The 2026-10-25 work environment did not contain Windows Python, MinGW or Wine; its Windows host was offline. The GitHub app toolset exposed in that session could merge PRs and manage Git text content, but did not expose release creation/asset upload. Hence a source/docs update is not proof of an uploaded `.exe` release.

## Hotfixes

Create `chatgpt-extrahigh/fix/<topic>` from `main`, make atomic commits with English prefix and Korean body, push each commit, open PR, and merge using no-ff. Review security/privacy before publishing another version. Do not force-push tags or replace already-published assets without clear release notes and deliberate approval.
