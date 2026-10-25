# 🪟 Windows 포터블 Electron 빌드

## 1. 요구 환경

Windows 10/11 x64, Node.js 22 이상, Git for Windows, 네트워크(NPM/Electron 배포 파일 다운로드)가 필요합니다. Linux에서 Cross-build는 electron-builder와 Wine 등 추가 의존성이 필요하므로 **Windows에서 직접 빌드하는 것이 기본**입니다. 이제 Electron이므로 MinGW/PyInstaller/Python은 필요 없습니다.

> 주의: Windows용 `Raidian.exe`가 실제로 생성되지 않았으면 EXE가 있다고 표기하지 않습니다. CI를 활성화하지 않았습니다.

## 2. 소스와 폰트

```powershell
git clone https://github.com/hslcrb/Raidian.git
cd Raidian
# 조선굴림체 웹폰트와 무손실 보관 원본은 이미 assets/fonts/에 들어 있습니다.
node .\scripts\font-assets.mjs
# 원본 TTF 파일 자체가 필요한 경우에만: npm run font:restore
```

폰트 원형 및 권리를 확인하세요: [assets/fonts/README.md](../assets/fonts/README.md).

## 3. 자동 빌드

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-windows.ps1
```

스크립트는 npm 설치, 테스트, `electron-builder --win portable zip --x64`, PE+ZIP 무결성 검사를 차례로 실행합니다.

성공 시:

- `dist/Raidian-0.2.0-win-x64-portable.exe`
- `dist/Raidian-0.2.0-win-x64.zip`
- `dist/SHA256SUMS.txt`
- `dist/BUILD-INFO.json` (Git SHA, 버전, 플랫폼, 검사 시각)

포터블 EXE는 Electron·Node 런타임을 포함하지만 Git과 선택적 gh는 별도 설치해야 해요.

## 4. Windows 수동 QA

- [ ] EXE를 Windows에서 실행해 한글 폴더/경로와 조선굴림체 확인
- [ ] 파일 상태, 한국어 자동 커밋, 브랜치 전환, no-ff 병합·충돌 처리
- [ ] cherry-pick, revert, 원격 2개, GitHub PR 연동
- [ ] `Raidian-...exe --cli --repo . --json doctor` 콘솔 출력 검사
- [ ] `Raidian-...exe --mcp --repo .`에 JSON-RPC 한 줄 전달 후 응답 검사
- [ ] ZIP 압축 해제 뒤 EXE 직접 실행
- [ ] Defender/SmartScreen 경고와 미서명 상태 확인 (코드 서명 미설정)

## 5. 릴리스

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish-release.ps1 -WindowsQaPassed
```

`gh release create`를 사용하며, 대상 브랜치가 `main`인지, `BUILD-INFO.json`의 Git SHA가 현재 HEAD와 일치하는지, 이미 릴리스가 존재하는지 검사합니다. 먼저 실제 Windows QA를 완료해야 합니다.
