# ✅ 검증 및 제한 사항 — Electron 전환 (2026-10-25)

## 이번 작업에서 로컬로 확인

- Node.js v22.16.0, Git 2.47.3 사용.
- `npm test`: **48개 단위·통합 테스트 통과** (UTF-8 한글 경로, NUL 파일명, 자동 커밋, no-ff 실제 Git 병합, cherry-pick/revert, 복수 원격, CLI 파싱, MCP 권한, 접근성 마크업, PE 헤더 검증).
- `npm run check`: Node 내장 구문 검사 통과.
- `npm run test:smoke`: Electron 파일 구조 스모크 통과.
- 첨부된 `ChosunGu.TTF` 원본의 family name 확인 및 로컬 CSS 폰트 경로 설정.

## 이 환경에서 수행하지 못한 항목

- Electron 런타임 패키지 설치(인터넷/DNS 접근 불가).
- 실제 Electron GUI 프로세스 구동 및 스크린리더 QA.
- Windows x64 포터블 EXE·ZIP 빌드(Windows PC 오프라인, Electron 바이너리 미설치).
- GitHub Release 생성/실제 바이너리 업로드(연결된 GitHub 도구에 Release POST 및 Asset Upload 기능이 없음).

## 실패하면 배포 중단

`scripts/verify-windows.mjs`는 `dist/`의 portable EXE가 `MZ` + AMD64 PE, ZIP이 PK 헤더인지 확인하며, 해시와 빌드 커밋 기록을 작성합니다. Windows 수동 실행 QA가 완료되지 않은 상태에서는 publish 스크립트 실행을 금지합니다.

**실제 Windows 바이너리 배포 완료라고 주장하지 않습니다.**
