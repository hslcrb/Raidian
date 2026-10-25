# 🚀 릴리스 매뉴얼

1. `main`에 PR이 merge commit(no-ff)으로 병합됐는지 확인.
2. Windows x64에서 Node/Git/gh 준비, `npm run font:verify`로 저장소 내 조선굴림체 에셋 검사.
3. `npm install`, `npm test`, `npm run build:win`, `npm run verify:win` 통과.
4. Windows에서 폰트·한글·브랜치·병합·CLI·MCP 실사용 QA.
5. `scripts/publish-release.ps1 -WindowsQaPassed` 실행.
6. `gh release view v0.2.0 --json assets,tagName,url`로 실제 자산 업로드 확인.

**자산:** Windows x64 포터블 EXE, ZIP, SHA256SUMS.txt, BUILD-INFO.json. 빌드 도구 설정으로 실행 파일이 자동 생성되는 것과 GitHub Release로 업로드되었다는 것은 다른 단계입니다.

**무결성:** 릴리스 소스 커밋 SHA가 `BUILD-INFO.json`과 맞지 않으면 발행하지 않습니다. 미서명 Windows 프로그램은 운영체제 경고가 나타날 수 있으니 README에서 안내합니다. 자동 Actions 워크플로는 모든 줄을 주석 처리하여 실행되지 않게 유지합니다.

실제 릴리스가 없으면 릴리스 페이지를 빈 상태로 표기하고, 다운로드를 안내하지 마세요.
