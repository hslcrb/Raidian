param([string]$Tag='v0.2.0',[switch]$WindowsQaPassed)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (!$WindowsQaPassed) {throw '실제 Windows에서 GUI, CLI, MCP 동작 검사 후 -WindowsQaPassed로 진행하세요.'}
if (!(Get-Command gh -ErrorAction SilentlyContinue)) {throw 'GitHub CLI(gh)가 필요합니다.'}
Set-Location (Split-Path -Parent $PSScriptRoot)
$version=(node -p 'require("./package.json").version').Trim()
if ($Tag -ne "v$version") {throw "태그($Tag)와 package.json 버전($version)이 다릅니다."}
$head=(git rev-parse HEAD).Trim()
$branch=(git branch --show-current).Trim()
if ($branch -ne 'main') {throw 'main 브랜치에서만 릴리스를 게시합니다.'}
node scripts/verify-windows.mjs
if ($LASTEXITCODE -ne 0) {throw '배포 산출물 검증에 실패했습니다.'}
$build = Get-Content 'dist/BUILD-INFO.json' -Raw | ConvertFrom-Json
if ($build.sourceCommit -ne $head) {throw '실제 소스 Git SHA와 산출물이 일치하지 않습니다.'}
gh release view $Tag 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {throw "이미 $Tag 릴리스가 있습니다. 자동 덮어쓰기는 하지 않습니다."}
$exe="dist/Raidian-$version-win-x64-portable.exe";$zip="dist/Raidian-$version-win-x64.zip"
gh release create $Tag $exe $zip 'dist/SHA256SUMS.txt' 'dist/BUILD-INFO.json' --title "Raidian $Tag · Ruby says hi! 🍒" --notes-file 'docs/RELEASE_NOTES_v0.2.0.md' --target $head
if ($LASTEXITCODE -ne 0) {throw '릴리스 업로드 실패'}
Write-Host "GitHub Release 게시 완료: $Tag"
