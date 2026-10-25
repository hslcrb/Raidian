# 변경 이력

## 0.2.0 — Electron 리팩토링 (2026-10-25)

- feat: Electron 메인/보안 preload/반응형 웹 UI 도입
- feat: 순수 Node.js Git 엔진/CLI/MCP 통합
- feat: no-ff 병합, 자동 한국어 커밋, 계층형 브랜치, 복수 원격, PR 연동 유지
- feat: 조선굴림체 WOFF2 및 무손실 압축된 TTF 원본을 `assets/fonts/`에 직접 포함; Git 서브모듈과 폰트 다운로드 제거
- security: 비활성화한 Node renderer, 허용 목록 IPC/MCP, 확인 절차
- test: 한글·Git 이력·MCP·정적 접근성 50개 테스트
- build: Windows portable/zip electron-builder 설정 및 무결성 검증, 수동 게시 스크립트
- docs: README·AGENTS·BUILD·BRAND·USER_GUIDE·RELEASING 전면 갱신

## 0.1.0 — Python/Tkinter 초기 버전

Python 기반의 첫 번째 GUI, CLI, MCP를 구현했습니다. 이력은 GitHub의 기존 PR #1~#4에서 확인할 수 있습니다. 소스는 0.2.0부터 Electron으로 대체됩니다.
