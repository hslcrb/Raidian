# Explicit, manual release publishing. No unattended GitHub workflow.
[CmdletBinding()]
param([string]$Tag = 'v0.1.0', [switch]$Prerelease, [switch]$WindowsQaPassed)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root
if ($Tag -notmatch '^v[0-9]+\.[0-9]+\.[0-9]+$') {
    throw '릴리스 태그는 v0.1.0과 같은 정식 버전 형식이어야 합니다.'
}
if (-not $WindowsQaPassed) {
    throw '먼저 Windows 실제 기기에서 GUI/한글/MCP를 검사한 뒤 -WindowsQaPassed를 명시해 주세요.'
}
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw 'Windows Python 및 py launcher가 필요합니다.'
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git for Windows가 필요합니다.'
}
if ((& git branch --show-current).Trim() -ne 'main') {
    throw '릴리스는 병합이 끝난 main 브랜치에서만 게시할 수 있습니다.'
}
if ((& git status --porcelain --untracked-files=no)) {
    throw '소스 파일에 미커밋 변경이 있습니다. 커밋/병합 후 다시 빌드하세요.'
}
$sourceCommit = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Git SHA를 확인하지 못했습니다.' }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'gh CLI를 설치하세요.' }
& gh auth status
if ($LASTEXITCODE -ne 0) { throw 'gh auth login을 먼저 실행하세요.' }
& py -3 -m scripts.validate_release --directory dist --tag $Tag --source-commit $sourceCommit
if ($LASTEXITCODE -ne 0) { throw '소스 출처·PE x64·SHA256·ZIP 검증에 실패했습니다.' }
$files = @('dist\Raidian.exe', 'dist\Raidian-CLI.exe',
    "dist\Raidian-$Tag-windows-x64-portable.zip", 'dist\SHA256SUMS.txt', 'dist\BUILD-INFO.json')
foreach ($path in $files) { if (-not (Test-Path $path)) { throw "릴리스 파일을 찾을 수 없습니다: $path" } }
# Refuse to publish a release without both Windows applications in the ZIP.
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead((Join-Path $root "dist\Raidian-$Tag-windows-x64-portable.zip"))
try {
    foreach ($name in @('Raidian.exe','Raidian-CLI.exe','LICENSE','README-PORTABLE.txt','BUILD-INFO.json')) {
        if (-not ($archive.Entries | Where-Object { $_.FullName -eq $name })) { throw "ZIP에 파일이 없습니다: $name" }
    }
} finally { $archive.Dispose() }
$body = "docs\RELEASE_NOTES_$Tag.md"
if (-not (Test-Path $body)) { throw '릴리스 노트가 없습니다.' }
& gh release view $Tag -R hslcrb/Raidian 1>$null 2>$null
if ($LASTEXITCODE -eq 0) {
    throw "릴리스 $Tag 가 이미 존재합니다. 자동 덮어쓰기를 하지 않습니다."
}
$flags = @('release','create',$Tag) + $files + @('--repo','hslcrb/Raidian','--target',$sourceCommit,'--title',"Raidian $Tag · 작은 Git 작업실",'--notes-file',$body)
if ($Prerelease) { $flags += '--prerelease' }
& gh @flags
if ($LASTEXITCODE -ne 0) { throw '릴리스 업로드에 실패했습니다.' }
Write-Host "게시 완료: https://github.com/hslcrb/Raidian/releases/tag/$Tag"
