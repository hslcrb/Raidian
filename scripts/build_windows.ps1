# Raidian portable Windows build. Run on actual Windows with Python and Git installed.
# GitHub Actions remains disabled; this script does NOT publish anything automatically.
[CmdletBinding()]
param(
    [ValidateSet('PyInstaller','Nuitka-MingGW')]
    [string]$Builder = 'PyInstaller'
)
$ErrorActionPreference = 'Stop'
if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    throw 'Windows 빌드 전용입니다. Linux MinGW만으로 Python/Tkinter EXE를 생성할 수 없습니다.'
}
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root
if (-not (Get-Command 'py' -ErrorAction SilentlyContinue)) {
    throw 'Windows CPython과 py launcher를 먼저 설치하세요. https://www.python.org/downloads/windows/'
}
if (-not (Get-Command 'git' -ErrorAction SilentlyContinue)) {
    throw 'Git for Windows가 필요합니다 (테스트 및 사용 시).' 
}
$version = '0.1.0'
# Bind every generated executable to the exact source commit it was built from.
$sourceCommit = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $sourceCommit -notmatch '^[0-9a-fA-F]{40}$') {
    throw 'Git 커밋 SHA를 식별할 수 없습니다. git clone으로 시작하세요.'
}
if ((& git status --porcelain --untracked-files=no)) {
    throw '추적 중인 소스에 미커밋 변경이 있습니다. 커밋/병합 후 빌드하세요.'
}
$launcher = if ($Builder -eq 'Nuitka-MingGW') { '-3.12' } else { '-3' }
$venvName = if ($Builder -eq 'Nuitka-MingGW') { '.venv-raidian-mingw' } else { '.venv-raidian-pyi' }
& py $launcher -m venv $venvName
if ($LASTEXITCODE -ne 0) { throw 'Python 가상환경을 만들지 못했습니다.' }
$python = Join-Path $root "$venvName\Scripts\python.exe"
& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip 업그레이드에 실패했습니다.' }
$deps = if ($Builder -eq 'Nuitka-MingGW') { @('nuitka>=2.4,<4','Pillow>=10,<13','ordered-set','zstandard') } else { @('pyinstaller>=6.12,<7','Pillow>=10,<13') }
& $python -m pip install @deps
if ($LASTEXITCODE -ne 0) { throw '빌드 의존성 설치에 실패했습니다.' }
& $python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw '테스트 실패: EXE 빌드를 중단합니다.' }
& $python -m compileall -q raidian scripts
if ($LASTEXITCODE -ne 0) { throw 'Python 문법 검사에 실패했습니다.' }
$icon = Join-Path $root 'build\raidian.ico'
& $python scripts/make_icon.py $icon
if ($LASTEXITCODE -ne 0) { throw '아이콘 생성 실패' }
if (-not (Test-Path 'dist')) { New-Item -ItemType Directory -Path dist | Out-Null }
$guiExe = Join-Path $root 'dist\Raidian.exe'
$cliExe = Join-Path $root 'dist\Raidian-CLI.exe'
foreach ($exe in @($guiExe,$cliExe)) { if (Test-Path $exe) { Remove-Item -LiteralPath $exe -Force } }
if ($Builder -eq 'PyInstaller') {
    $common = @('--noconfirm','--clean','--onefile','--paths','.','--add-data','assets;assets', '--icon',$icon)
    & $python -m PyInstaller @common --windowed --name Raidian scripts/launcher.py
    if ($LASTEXITCODE -ne 0) { throw 'GUI PyInstaller 빌드 실패' }
    & $python -m PyInstaller @common --console --name Raidian-CLI scripts/console.py
    if ($LASTEXITCODE -ne 0) { throw 'CLI PyInstaller 빌드 실패' }
} else {
    # On Windows, Nuitka downloads its supported MinGW64 toolchain if needed.
    # Python 3.12 is intentional; 3.13+ MinGW64 requires experimental flags.
    $common = @('--mode=onefile','--mingw64','--enable-plugin=tk-inter','--assume-yes-for-downloads',
        '--include-data-dir=assets=assets','--windows-icon-from-ico='+$icon,'--output-dir=dist',
        '--product-name=Raidian','--product-version='+$version,'--file-version='+$version)
    & $python -m nuitka @common --windows-console-mode=disable --output-filename=Raidian.exe scripts/launcher.py
    if ($LASTEXITCODE -ne 0) { throw 'GUI Nuitka+MinGW 빌드 실패' }
    & $python -m nuitka @common --windows-console-mode=force --output-filename=Raidian-CLI.exe scripts/console.py
    if ($LASTEXITCODE -ne 0) { throw 'CLI Nuitka+MinGW 빌드 실패' }
}
foreach ($exe in @($guiExe,$cliExe)) {
    if (-not (Test-Path -LiteralPath $exe)) { throw "빌드 결과가 없습니다: $exe" }
    & $python scripts/verify_pe.py $exe
    if ($LASTEXITCODE -ne 0) { throw "PE x64 검증 실패: $exe" }
}
# Run headless CLI smoke tests on Windows, not merely PE magic-byte checks.
& $cliExe --version
if ($LASTEXITCODE -ne 0) { throw 'CLI --version 확인 실패' }
& $cliExe --json doctor
if ($LASTEXITCODE -ne 0) { throw 'CLI doctor 확인 실패' }
& $cliExe --json agent-guide
if ($LASTEXITCODE -ne 0) { throw 'CLI agent-guide 확인 실패' }
$portable = Join-Path $root 'dist\portable'
if (Test-Path $portable) { Remove-Item -Recurse -Force $portable }
New-Item -ItemType Directory -Path $portable | Out-Null
Copy-Item $guiExe,$cliExe,(Join-Path $root 'LICENSE') -Destination $portable
Copy-Item (Join-Path $root 'scripts\README-PORTABLE.txt') -Destination $portable
$buildInfo = [ordered]@{
    version = "v$version"
    sourceCommit = $sourceCommit
    builder = $Builder
    platform = 'windows-amd64'
    pythonVersion = (& $python --version)
    builtAtUtc = [DateTime]::UtcNow.ToString('o')
}
$buildInfoPath = Join-Path $root 'dist\BUILD-INFO.json'
$buildInfo | ConvertTo-Json | Set-Content -LiteralPath $buildInfoPath -Encoding UTF8
Copy-Item $buildInfoPath -Destination $portable
$zip = Join-Path $root "dist\Raidian-v$version-windows-x64-portable.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $portable '*') -DestinationPath $zip -CompressionLevel Optimal
if (-not (Test-Path $zip)) { throw 'ZIP 생성 실패' }
$hashes = @($guiExe,$cliExe,$zip) | ForEach-Object {
    $h = Get-FileHash -Algorithm SHA256 -LiteralPath $_
    "$($h.Hash.ToLowerInvariant())  $([IO.Path]::GetFileName($_))"
}
$checksums = Join-Path $root 'dist\SHA256SUMS.txt'
$hashes | Set-Content -LiteralPath $checksums -Encoding ASCII
& $python -m scripts.validate_release --directory dist --tag "v$version" --source-commit $sourceCommit
if ($LASTEXITCODE -ne 0) { throw '포터블 파일 출처/체크섬 검증 실패' }
Write-Host "`n✔ Windows build prepared (not uploaded):"
Write-Host $guiExe
Write-Host $cliExe
Write-Host $zip
Write-Host $checksums
Write-Host $buildInfoPath
Write-Host '테스트할 것: Windows 실제 GUI 실행, 한글 경로, Git Credential Manager, MCP JSON-RPC.'
Write-Host '릴리스 게시: powershell -File scripts/publish_release.ps1 -WindowsQaPassed (Windows 실기기 검증 후 수동 게시)'
