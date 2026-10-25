<div align="center">

<img src="assets/brand/raidian-hero.svg" alt="Raidian 레이디안: 웃는 Git 브랜치 캐릭터 루비와 버건디 배너" width="100%" />

### Git은 어렵지 않아도 되니까. ♥

**한글이 예쁘게 보이고, 실수는 덜 무섭고, 클릭은 더 쉬운 Git.**  
Python과 Tkinter로 만든 조그맣고 야무진 Git 작업실입니다.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-551128?logo=python&logoColor=white)](https://www.python.org/) [![Git](https://img.shields.io/badge/Git-필수-A72146?logo=git&logoColor=white)](https://git-scm.com/) [![License MIT](https://img.shields.io/badge/License-MIT-C42B54?logoColor=white)](LICENSE) [![Workflows disabled](https://img.shields.io/badge/Actions-수동_빌드-90616D?logo=githubactions&logoColor=white)](.github/workflows/windows-build.yml)

**[5분 시작하기](#-5분이면-시작해요)** · **[기능 한눈에](#-레이디안은-이렇게-움직여요)** · **[CLI / MCP](#-사람과-에이전트가-함께-써요)** · **[Windows 빌드](#-윈도우-포터블-빌드)**

</div>

---

## 🌷 안녕! 나는 레이디안이야

Git Bash의 투명한 동작은 살리고, 낯선 명령어는 읽기 쉬운 버튼으로 옮겼어요. 커밋은 **내 컴퓨터에 기록**, 푸시는 **원격 저장소로 전송**. 이 차이를 처음부터 보여줍니다. 한글 경로와 메시지는 UTF-8 중심으로 다루고 Windows의 CP949 출력도 고려했어요.

| 이런 순간 | 레이디안에서는 |
| :-- | :-- |
| 😵 `git status`가 낯설어요 | 변경 파일을 표에서 확인해요. |
| ✍️ 커밋 메시지를 깜빡했어요 | 파일 변경 유형으로 한국어 메시지를 **규칙 기반** 생성해요. AI가 지어내지 않아요. |
| 🌱 브랜치를 깔끔하게 나누고 싶어요 | `chatgpt-extrahigh/feature/작업명` 형태로 만들어요. **이름의 `/`는 실제 부모 브랜치가 아니에요.** |
| 🌳 병합해도 분기 이력이 남았으면 해요 | 기본적으로 `git merge --no-ff --no-edit`를 사용해요. |
| 🕰️ 예전 커밋의 변경이 필요해요 | `cherry-pick`으로 **새 커밋**에 가져와요. |
| 🩹 과거 특정 커밋이 실수였어요 | `revert`로 취소하는 **새 커밋**을 만들어요. 공유 이력은 지우지 않아요. |
| 🤝 AI 에이전트도 쓰게 하고 싶어요 | 읽기 전용 기본 MCP, JSON CLI, 키보드 접근 가능한 GUI를 제공해요. |

> **루비의 한마디** 💌 “이력이 꼬였을 땐 지우기보다 남겨서 바로잡자. 미래의 우리에게 친절하니까!”

## 🍓 5분이면 시작해요

### 1. 준비물

- **Python 3.10 이상**, **Git** (필수). Windows에서는 [Git for Windows](https://gitforwindows.org/)를 설치해 주세요.
- **GitHub CLI (`gh`)**는 PR 목록/생성 기능을 쓸 때만 필요해요. [설치 안내](https://cli.github.com/)
- Tkinter는 일반적인 Windows용 Python 설치에 포함돼요. 일부 Linux 배포판에서는 별도의 `python3-tk` 패키지가 필요해요.

### 2. 설치 없이 소스로 열기

```powershell
# PowerShell · Git은 설치돼 있어야 해요.
git clone --depth 1 https://github.com/hslcrb/Raidian.git
cd Raidian
python -m raidian gui
```

창이 열리면 **[폴더 열기] → 변경 파일 살펴보기 → 메시지 작성 → [커밋] → [푸시]** 순서로 시작하세요. `Ctrl+Enter`는 커밋, `F5`는 새로고침이에요.

### 3. 명령어로 사용하기 (선택)

```powershell
python -m pip install -e .
raidian --repo . status
raidian --repo . --json status
raidian --repo . commit -m "docs: 사용 방법 정리"
raidian --repo . commit                  # 메시지가 비었을 때 자동 결정
raidian --repo . branch-child feature hello-git
raidian --repo . doctor
```

`--repo`와 `--json` 옵션은 **서브명령보다 앞**에 배치해 주세요. `commit`은 기본적으로 현재 변경 파일을 모두 스테이징하고 커밋하니 **[변경 파일]을 먼저 확인**하는 습관이 좋아요.

## 🧁 레이디안은 이렇게 움직여요

| 영역 | 무엇을 하나요? | 조심할 점 |
| :--- | :--- | :--- |
| **변경 파일** | 추가·수정·삭제·이름 변경을 한눈에 표시 | 커밋 전에 의도치 않은 파일이 없는지 확인 |
| **커밋 이력** | 커밋 SHA·날짜·메시지 탐색 | 복사(cherry-pick)와 되돌리기(revert)는 서로 달라요 |
| **브랜치** | 계층형 이름 생성, 기존 브랜치 전환 | 변경 내용이 남아 있으면 안전을 위해 전환 거부 |
| **병합 · no-ff** | 분기 관계가 보이도록 병합 | 충돌은 자동으로 덮어쓰지 않아요 |
| **원격** | 여러 원격 추가/제거, 가져오기, 푸시 | 자동 강제 푸시(`--force`) 없음 |
| **GitHub** | `gh`를 통한 PR 조회·생성 | 로그인은 별도 `gh auth login` |

**단축키를 좋아하는 분께**

| 키 | 기능 | 키 | 기능 |
| --- | --- | --- | --- |
| `Ctrl+O` | 저장소 열기 | `F5` | 새로고침 |
| `Ctrl+Enter` | 커밋 | `Ctrl+Shift+Enter` | 커밋 + 푸시 |
| `Alt+B` | 하위 작업 브랜치 | `Alt+P` | 푸시 |

모든 pill 액션은 포커스 이동 후 `Enter` 또는 `Space`로 실행할 수 있어요. **현재의 Tkinter 커스텀 Canvas 버튼은 운영체제별 스크린리더 지원에 차이가 있어요.** 접근성 검증을 계속 개선할 예정이에요.

## 🪄 사람과 에이전트가 함께 써요

GUI·CLI·MCP는 **같은 Git 엔진**을 사용해요. 서로 다른 곳에서 숨겨진 Git 명령을 마음대로 실행하지 않아요.

**CLI — 자동화용 UTF-8 JSON**

```powershell
raidian --repo . --json status
raidian --repo . --json agent-guide
raidian shell    # 친숙한 대화형 프롬프트
```

**MCP — 처음에는 읽기 전용**

```powershell
python -m raidian.mcp --repo "C:\work\my-repo"
# 쓰기를 정말 허용해야 한다면:
python -m raidian.mcp --repo "C:\work\my-repo" --allow-write
```

MCP 호출에서 실제 변경을 요청할 때는 **서버 `--allow-write` + 개별 도구 `confirm: true`**가 모두 있어야 해요. 이는 호출자의 인간 승인을 기술적으로 보증하는 기능이 아니므로, 권한이 제한된 신뢰 가능한 에이전트에게만 쓰기 권한을 주세요. 임의 셸 명령·강제 푸시·임의 이력 삭제 도구는 제공하지 않아요.

더 깊이 보고 싶다면 [에이전트·MCP 가이드](docs/AGENTS.md)와 [Git 명령·안전 정책](docs/ARCHITECTURE.md)을 참고하세요.

## 🎀 윈도우 포터블 빌드

**Windows에서** 다음을 실행하면 PyInstaller 기반 GUI `Raidian.exe`와 콘솔 `Raidian-CLI.exe`를 포함하는 포터블 ZIP을 생성하도록 스크립트를 제공해요.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
# 선택: Windows 환경에서 MinGW64를 사용하는 Nuitka 빌드
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -Builder Nuitka-MingGW
```

압축을 풀고 `Raidian.exe`를 실행하면 GUI가 열려요. `Raidian-CLI.exe --json doctor`는 콘솔 진단, `Raidian-CLI.exe mcp --repo "C:\work\repo"`는 MCP 서버예요. **Git은 필수 외부 의존성**이고, `gh`는 선택 외부 의존성이에요. 즉 Python 설치는 필요 없지만 Git은 따로 설치되어야 해요.

> ⚠️ **빌드 상태**: 본 저장소에는 Windows 빌드 스크립트가 있으며, **Windows용 EXE 실행 검증 및 GitHub Release 바이너리 게시 여부는 릴리스 페이지에서 별도로 확인**해야 해요. MinGW만으로 Linux의 PyInstaller를 Windows EXE로 바꿀 수 없어요. Windows Python/런타임이 필요한 이유는 [빌드 가이드](docs/BUILD_WINDOWS.md)에 정리했어요.

📦 [최신 Releases 페이지](https://github.com/hslcrb/Raidian/releases) · [빌드/검증 방법](docs/BUILD_WINDOWS.md) · [릴리스 절차](docs/RELEASING.md)

## 🎨 브랜딩 · 여기는 버건디 스튜디오

<div align="center">
<img src="assets/brand/raidian-mark.svg" width="96" alt="루비 마스코트 마크" />

**Ruby · 루비** — Git의 세 갈래가 살짝 웃고 있는 작은 친구.

</div>

| 색 | 코드 | 역할 |
| :-- | :-- | :-- |
| 🍷 Deep Burgundy | `#551128` | 타이틀·아이덴티티 |
| 🍒 Cherry Red | `#A72146` | 중요 작업·기본 버튼 |
| 💗 Rosy Red | `#C42B54` | 호버·강조 |
| 🌸 Soft Blush | `#FCECEF` | 보조 버튼·선택 상태 |
| 🧻 Paper White | `#FFFFFF` | 카드·본문 |

브랜드와 SVG의 사용·변경 규칙: [BRAND.md](docs/BRAND.md). 첨부 서체 파일은 확인되지 않아 **현재 폰트 파일을 포함하지 않습니다**. 폰트를 재배포할 권한이 있는 경우 `assets/fonts/`에 TTF를 넣어 Windows 빌드에 포함할 수 있어요. [폰트 안내](assets/README.md)

## 🧪 만들고, 점검하고, 함께 키워요

```powershell
python -m unittest discover -s tests -v
python -m compileall -q raidian scripts
```

- [사용자 사용 설명서](docs/USER_GUIDE.md) · [프로그램 구조](docs/ARCHITECTURE.md) · [에이전트 계약](docs/AGENTS.md)
- [Windows 빌드](docs/BUILD_WINDOWS.md) · [릴리스 체크리스트](docs/RELEASING.md) · [변경 기록](CHANGELOG.md) · [검증 기록](docs/VALIDATION.md)
- [기여 안내](CONTRIBUTING.md) · [보안 정책](SECURITY.md) · [MIT 라이선스](LICENSE)

Git 문제는 어렵지만, 오류 안내는 어려울 필요가 없다고 믿어요. 작은 PR부터 반갑게 환영합니다. 🌷

<div align="center">

---

**Tiny Git. Clear history. Happy commits.**  
Made with ♥ for calmer commits.

</div>
