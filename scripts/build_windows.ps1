# Local Windows build only. No Actions workflow is executed.
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
py -3 -m venv .venv
$python = Join-Path $PWD '.venv\Scripts\python.exe'
& $python -m pip install --upgrade pip
& $python -m pip install pyinstaller
& $python -m unittest discover -s tests -v
& $python -m PyInstaller --noconfirm --clean --onefile --windowed --name Raidian --add-data 'assets;assets' --collect-submodules raidian --paths . scripts/launcher.py
Write-Host 'Ready: dist\Raidian.exe'
