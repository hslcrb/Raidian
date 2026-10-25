# Raidian 검증 기록 · 2026-10-25

> 기능 구현·테스트 결과와 **실제 Windows 실행 파일 검증**을 구별해서 기록합니다. GitHub README에 보이는 것과 실제 릴리스 바이너리 상태가 다르면 이 문서가 사실을 명확히 합니다.

## 1. 작업 범위 및 코드 상태

- 기존 PR [#1](https://github.com/hslcrb/Raidian/pull/1): 19개 파일별 커밋, Tkinter GUI·Git 엔진·CLI·MCP 구현, merge commit `d6a5c6107ac2e7a800ade3855ac6d5c65bb02832`.
- 문서·브랜드·빌드 PR [#2](https://github.com/hslcrb/Raidian/pull/2): 24개 파일별 커밋, 귀여운 루비 SVG, 포터블 빌드 스크립트 및 운영 문서, merge commit `5d9e10bb67e711073cc47d1697f421449ad85d18`.
- 두 PR 모두 GitHub의 `merge` 병합 방식 사용. 커밋/푸시는 GitHub 저장소 작업 브랜치에 파일별로 즉시 반영했습니다.
- 작업 브랜치 네임스페이스: `chatgpt-extrahigh/`.

## 2. 로컬 검증 (실행됨)

| 테스트 | 결과 | 의미 |
| --- | --- | --- |
| `python -m unittest discover -s tests -v` | **19건 통과** | 임시 Git 저장소, 한글 경로, 메시지 자동 선택, no-ff, cherry-pick, revert, 다중 원격, CLI/MCP |
| `python -m compileall -q raidian scripts` | **통과** | Python 문법/임포트 가능한 소스 컴파일 확인 |
| `xvfb-run` Tkinter Workbench 생성 | **통과** | 1100×760 가로 배치, 720×640 세로 배치, 메인 브랜치 표시 |
| SVG XML 파싱 / CairoSVG 미리보기 | **통과** | SVG 문법 유효, 브랜드 헤더/심볼 렌더링 |
| `.github/workflows` 활성 YAML 점검 | **통과** | 워크플로 파일의 모든 비어있지 않은 줄이 `#` 주석 |
| Windows PE 헤더 검사기 합성 fixture | **통과** | x64 시뮬레이션 MZ/PE 메타데이터 파싱 **만** 확인 |
| 실제 Windows EXE 빌드 및 기동 | **미실행** | Windows Python·Wine·MinGW 부재, Windows 기기 오프라인 |
| GitHub Release 등록·자산 업로드 | **미실행** | 연결된 GitHub 도구는 PR 병합은 지원하지만 Release 생성/업로드 미지원 |

위 결과는 Linux Debian 13 / CPython 3.13 / Git 2.47 계열의 작업 환경에서 얻은 것입니다. Windows PE 테스트는 **실제 실행 파일 생성 테스트가 아닙니다**.

## 3. 새 아키텍처

- 공통 Git 엔진: UTF-8 우선 및 CP949 fallback, 명령 인자 배열, `shell=False`, 안전한 작업 트리 검사.
- GUI: Tkinter 표/입력/버튼, 버건디 테마, 루비 마스코트, 너비에 따라 배치 전환, 명령 작업자 스레드.
- CLI: JSON 출력 및 대화형 프롬프트.
- MCP: 2025-11-25까지의 레거시 handshake와 2026-07-28 stateless discovery 지원. read-only 기본/쓰기 opt-in.
- Windows: `build_windows.ps1`가 **Windows 머신에서만** PyInstaller 또는 Nuitka/MinGW 빌드를 실행하도록 준비됨.
- 릴리스: 명시적 `publish_release.ps1`가 `gh` CLI를 통해 ZIP/체크섬을 게시하도록 준비됨. **이 스크립트는 이 환경에서 실행되지 않음**.

## 4. 차단 요소와 다음 확인

1. 신뢰할 수 있는 Windows 10/11 x64 개발 머신에서 Python 3.12 x64, Git for Windows 설치.
2. `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1 -Builder Nuitka-MingGW` 또는 기본 PyInstaller 명령 실행.
3. 생성된 `Raidian.exe`, `Raidian-CLI.exe`, 포터블 ZIP을 **실제 Windows에서** 수동 테스트.
4. 첨부 서체가 있다면 원본 파일과 재배포 허가 확인 후 다시 빌드.
5. SHA256 체크섬 검토 후 `powershell -File scripts/publish_release.ps1 -Tag v0.1.0 -Prerelease` 명시적 실행.
6. GitHub Releases 페이지에서 태그, 파일 크기, 자산 업로드가 확인되기 전에는 '릴리스 게시 완료'라고 말하지 않음.

## 5. 오픈소스 관리

- MIT 라이선스와 기여/보안 정책 구비.
- 라이선스가 확인되지 않은 커스텀 폰트는 커밋하지 않음.
- README와 SVG에는 외부 사용자 추적 코드를 넣지 않음.
- 워크플로 전체 주석 처리 상태 유지.
- 향후 실제 Windows 테스트에서 발생한 오류 및 포터블 용량을 이 문서에 추가할 것.
