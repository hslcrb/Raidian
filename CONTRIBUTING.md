# Contributing to Raidian 🍓

작은 PR, 명확한 이유, 안전한 Git 이력. 귀여운 화면도 좋지만 **읽을 수 있는 코드와 설명 가능한 동작**을 우선합니다.

## 준비

1. 이슈에서 재현 방법과 기대 동작을 정리합니다.
2. 새로운 브랜치에서 작업합니다. AI 에이전트 브랜치는 `chatgpt-extrahigh/<feature>/<detail>` 규칙을 따릅니다.
3. **초마이크로 커밋**으로 분리합니다. 커밋 문구는 `fix: 한글 파일명 파싱 수정`처럼 영문 Conventional Commit 접두어와 한글 메시지를 씁니다.
4. 원격에 매 커밋 푸시하고 PR에서 테스트 결과 및 사용성 변화를 설명합니다.
5. PR을 GitHub의 `merge` 방식으로 합쳐 개별 커밋과 merge commit을 유지합니다.

## 테스트

```sh
python -m unittest discover -s tests -v
python -m compileall -q raidian scripts
```

- Python 표준 라이브러리를 우선합니다. 실제 Git 레포를 이용하는 단위/통합 테스트를 작성하고 네트워크 접근이 필요한 테스트는 분리합니다.
- CLI/JSON/MCP는 공통 `raidian/core.py`를 우회하지 않아야 합니다.
- 화면 레이블·키보드 경로·명시적인 사용자 확인을 놓치지 마세요.
- Git Bash 출력을 정확히 해석하고, `shell=True` 또는 자동 `--force`를 도입하지 마세요.
- 외부 폰트를 올릴 때는 별도의 재배포 허가 증거와 라이선스를 제출합니다.

## 빌드 및 릴리스

Actions는 의도적으로 주석만 있습니다. Windows 실행 검증 후 `scripts/build_windows.ps1`로 포터블 ZIP을 만들고 [릴리스 가이드](docs/RELEASING.md)를 따릅니다. 운영체제별 바이너리를 임의로 '정상 빌드'라고 표기하지 마세요.
