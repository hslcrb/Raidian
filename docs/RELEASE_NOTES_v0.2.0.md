# Raidian v0.2.0 🍒 — Electron 전환

## 달라진 점

- Python/Tkinter 의존성을 제거하고 Electron + Node.js + Web UI로 전면 리팩토링했습니다.
- 루비(Ruby) SVG 브랜딩과 버건디/체리 레드/블러시 팔레트를 유지하면서 반응형·접근성 개선.
- 조선굴림체(ChosunGu) TTF를 우선 로드하도록 `@font-face` 구성.
- 공통 Git 엔진의 UTF-8 우선/CP949 폴백, 한국어 자동 커밋, `--no-ff` 병합, 히스토리 복사·되돌리기, 여러 원격을 유지.
- 단일 Electron EXE에서 `--cli`와 `--mcp` 접근 가능하도록 구성.
- MCP 읽기 전용 기본값, allowlist, 명시적 확인·안전한 contextBridge 도입.
- 48개 테스트 및 PE/ZIP 검증 스크립트 추가.

## 설치

Windows x64 포터블 EXE는 추후 Windows 환경에서 빌드/검증을 거쳐 게시합니다. **이 문서가 존재해도 릴리스 업로드가 완료된 것은 아닙니다.** Git for Windows는 별도 설치해야 합니다.
