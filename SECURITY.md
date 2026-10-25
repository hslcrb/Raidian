# 🛡️ 보안 정책

Raidian은 사용자 파일을 직접 변경하는 Git 도구이므로 보수적인 작업 범위가 중요합니다.

## 보호 장치

- Electron renderer에서 Node 통합 비활성화, sandbox 및 contextIsolation 적용
- preload IPC 허용 목록과 Git 명령 `spawn` 인자 배열 (`shell:false`)
- GitHub 이외의 무분별한 링크 탐색 금지, 콘텐츠 CSP 적용
- MCP 읽기 전용 기본값, 쓰기 플래그 + 도구 호출별 `confirm:true` 요구
- 강제 푸시·임의 명령·과거 커밋 직접 제거 기능 미제공

이 조치는 모든 공격을 차단한다는 보증은 아닙니다. `--allow-write` 서버는 신뢰된 호출자에게만 노출하세요.

## 제보 방법

취약점을 발견하면 공개 Issue에 악용 절차/민감 정보를 쓰지 말고 저장소의 **Security → Report a vulnerability** 기능을 이용하세요. GitHub private vulnerability reporting을 사용할 수 없다면 관리자에게 비공개 방식으로 연락하세요.

## 외부 구성 요소

Windows에 설치된 Git/GitHub CLI 및 Electron/Node 런타임의 업데이트·자격 증명 관리도 중요합니다. 조선굴림체는 소프트웨어의 MIT 라이선스와 별도로 저작권자 이용 조건을 따릅니다.
