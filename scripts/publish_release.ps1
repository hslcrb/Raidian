# Explicit, manual release publishing. No unattended GitHub workflow.
[CmdletBinding()]
param([string]$Tag = 'v0.1.0', [switch]$Prerelease)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'gh CLI를 설치하세요.' }
& gh auth status
if ($LASTEXITCODE -ne 0) { throw 'gh auth login을 먼저 실행하세요.' }
$files = @("dist\Raidian-$Tag-windows-x64-portable.zip",'dist\SHA256SUMS.txt')
foreach ($path in $files) { if (-not (Test-Path $path)) { throw "릴리스 파일을 찾을 수 없습니다: $path" } }
# Refuse to publish a release without both Windows applications in the ZIP.
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead((Join-Path $root $files[0]))
try {
    foreach ($name in @('Raidian.exe','Raidian-CLI.exe','LICENSE','README-PORTABLE.txt')) {
        if (-not ($archive.Entries | Where-Object { $_.FullName -eq $name })) { throw "ZIP에 파일이 없습니다: $name" }
    }
} finally { $archive.Dispose() }
$body = 'docs\RELEASE_NOTES_v0.1.0.md'
if (-not (Test-Path $body)) { throw '릴리스 노트가 없습니다.' }
& gh release view $Tag -R hslcrb/Raidian 1>$null 2>$null
if ($LASTEXITCODE -eq 0) {
    & gh release upload $Tag @files -R hslcrb/Raidian
} else {
    $flags = @('release','create',$Tag) + $files + @('--repo','hslcrb/Raidian','--target','main','--title',"Raidian $Tag · 작은 Git 작업실",'--notes-file',$body)
    if ($Prerelease) { $flags += '--prerelease' }
    & gh @flags
}
if ($LASTEXITCODE -ne 0) { throw '릴리스 업로드에 실패했습니다.' }
Write-Host "게시 완료: https://github.com/hslcrb/Raidian/releases/tag/$Tag"
