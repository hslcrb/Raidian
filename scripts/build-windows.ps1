param([switch]$SkipTests)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ([System.Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'Windows PC에서 실행해 주세요.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node.js 22 이상이 필요합니다.' }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git for Windows가 필요합니다.' }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw 'npm이 설치되어야 합니다.' }
Set-Location (Split-Path -Parent $PSScriptRoot)
# 앱에 포함된 로컬 폰트 에셋을 prebuild 단계에서 검증합니다 (외부 폰트 다운로드 없음).
node -e "if (Number(process.versions.node.split('.')[0])<22) process.exit(1)"
if ($LASTEXITCODE -ne 0) {throw 'Node.js 22 이상이 필요합니다.'}
npm install --no-audit --no-fund
if ($LASTEXITCODE -ne 0) {throw 'npm 설치에 실패했습니다.'}
if (!$SkipTests) {npm test; if ($LASTEXITCODE -ne 0) {throw '테스트 실패'}}
npm run build:win
if ($LASTEXITCODE -ne 0) {throw 'Windows Electron 빌드 실패'}
npm run verify:win
if ($LASTEXITCODE -ne 0) {throw 'Windows PE 무결성 확인 실패'}
Write-Host '🍒 dist/의 exe와 zip을 Windows PC에서 직접 실행해 확인한 뒤 릴리스를 게시하세요.'
