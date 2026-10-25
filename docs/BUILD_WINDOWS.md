# Windows portable EXE build guide

## Important reality check

**MinGW-w64 is a cross-compiler for C/C++, not a general converter of a Linux Python/Tkinter program into a Windows self-contained binary.** PyInstaller builds for the operating system where its Python runs. For Windows GUI packaging, Python, Tcl/Tk and loader modules must be Windows-compatible. A practical path is **native Windows**; a more advanced alternative is **Wine + Windows CPython + Windows PyInstaller**, which still requires Windows runtimes and full functional testing on Windows.

The repository's default builder is **PyInstaller on Windows**. A second Windows-only option uses **Nuitka with MinGW64**, as requested. It compiles Python on Windows using the supported MinGW toolchain; it does **not** claim unsupported Linux→Windows Nuitka cross-compilation.

| Option | Runs on | Compiler/bundler | Status |
| --- | --- | --- | --- |
| `-Builder PyInstaller` | Windows | Windows CPython + PyInstaller | Script provided; Windows run not verified here |
| `-Builder Nuitka-MingGW` | Windows + Python 3.12 | Nuitka + MinGW64 | Script provided; Windows run not verified here |
| Linux-only `mingw-w64` | Linux | Windows-targeting C/C++ compiler | Insufficient alone for this Python GUI |
| Wine + Windows CPython | Linux with Wine configured | Windows PyInstaller in Wine | Not packaged as a validated workflow |

References: [PyInstaller manual](https://pyinstaller.org/en/stable/), [Nuitka user manual](https://nuitka.net/user-documentation/user-manual.html).

## Prerequisites on a trusted Windows 10/11 x64 machine

1. Install Windows Python from python.org. For `-Builder Nuitka-MingGW`, install **Python 3.12 x64** and `py` launcher; Python 3.13+ requires a Nuitka experimental MinGW mode.
2. Install Git for Windows so `git --version` succeeds in PowerShell.
3. To publish, optionally install GitHub CLI, sign in (`gh auth login`) and ensure push access to `hslcrb/Raidian`.
4. Ensure network access for pip and (for Nuitka) the MinGW compiler download. Antivirus or policy may intercept build output.
5. Ensure there is free disk space for 2 onefile builds and an isolated Python venv.

## Build

```powershell
# In a checkout of Raidian on Windows:
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1

# Or Nuitka, backed by MinGW64, on Python 3.12:
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -Builder Nuitka-MingGW
```

Script does: create an isolated environment; install its pinned-major tools; run unit tests; compile Python; generate an icon; build GUI and console; validate PE x64 headers; smoke-test CLI/doctor/agent-guide; zip binaries with README and LICENSE; generate SHA256SUMS.

Expected outputs **only after a successful build**:

```
dist/
  Raidian.exe                       # GUI, no console
  Raidian-CLI.exe                   # CLI + MCP (subcommand: mcp)
  Raidian-v0.1.0-windows-x64-portable.zip
  SHA256SUMS.txt
```

The optional embedded fonts must be placed in `assets/fonts/` with an appropriate redistribution license before compiling; without them Windows system fonts are used. Source SVG icons do not require proprietary typefaces.

## Post-build verification on **actual Windows**, required for release

1. PowerShell: `Get-FileHash dist\Raidian.exe -Algorithm SHA256` and compare the generated checksums.
2. `dist\Raidian-CLI.exe --version`, `--json doctor`, and `--json agent-guide` must print valid output.
3. Create a temporary Git repo in a folder containing Hangul and spaces. In GUI, edit a Hangul-named file and confirm commit, history and status.
4. Test keyboard-only usage, focus indication, visible error text, narrow window layout.
5. Test two named remotes and `gh` PR listing if installed; do not test with production credentials by default.
6. Test default no-ff merge and no history rewrite on disposable branches.
7. Confirm MCP JSON-RPC line-delimited stdout is machine-readable, does not print prompts to stdout, and the default mode refuses writes.
8. Check `git.exe` is actually present on target Windows, either in PATH or via user installation. Python bundle alone does not include Git.
9. Check `.zip` contains the TWO EXEs, `LICENSE`, `README-PORTABLE.txt`. The ZIP itself is **not** a signed installer.

**DO NOT claim the release is validated merely because `MZ`/`PE` headers are present.** `verify_pe.py` only checks format and x64 CPU type; GUI and Git must be tested on Windows before publication.

## Publishing

```powershell
powershell -File .\scripts\publish_release.ps1 -Tag v0.1.0 -Prerelease
```

The publish script is never invoked automatically. It requires an authenticated `gh`, the verified ZIP and checksums, and uploads to the intended repository. See [RELEASING.md](RELEASING.md). Existing same-name release assets are **not** overwritten automatically.

## Troubleshooting

- `py` absent: use python.org installation with **Python launcher for Windows** checked.
- Nuitka `--mingw64` fails on Python 3.13+: use CPython 3.12; do not silently use experimental flags for release.
- Tk plugin missing in Nuitka: verify the builder version and `--enable-plugin=tk-inter` support.
- PyInstaller missing Tcl/Tk: make sure you use an official Windows Python installer and rerun clean.
- Antivirus warning: unsigned onefile programs commonly trigger reputation warnings. Verify SHA256, consider code signing, and do not instruct users to disable antivirus.
- `git` not found after EXE starts: Git for Windows is external and should be installed separately.
- Failure on Linux: the Windows script intentionally refuses Linux; don't rename an ELF file to `.exe`.
