# Raidian assets ♥

- `brand/raidian-hero.svg` — 귀여운 Git 친구 **루비**가 등장하는 README 배너.
- `brand/raidian-mark.svg` — 버건디 라운드 사각형의 루비 심볼.
- `fonts/` — 재배포·임베딩 허가를 받은 TTF 파일만 추가하세요. **현재 업로드된 사용자 폰트 원본을 확인할 수 없어 기본 저장소에는 포함되어 있지 않습니다.**

## 폰트 임베딩

1. 원본 `.ttf`와 폰트 라이선스/권리자를 직접 확인합니다. 상업적 사용/수정/재배포/소프트웨어 번들 허가 여부를 검토하세요.
2. `assets/fonts/<font>.ttf`에 놓고 폰트 라이선스 및 저작권 고지를 함께 관리합니다.
3. Windows GUI는 해당 TTF를 `AddFontResourceExW(..., FR_PRIVATE, ...)`로 현재 프로세스에서만 등록합니다. *시스템 폰트로 영구 설치하지 않습니다.*
4. Windows 빌드 스크립트는 `assets` 폴더를 번들에 포함합니다. Tk의 폰트 패밀리 이름은 TTF 파일 이름과 다를 수 있으므로 글꼴의 내부 Family를 검사하세요.
5. 첨부 폰트 파일이 없는 경우 `Wanted Sans`/`Pretendard`/`맑은 고딕`/`Noto Sans CJK KR` 등 **설치된** 폰트를 우선 사용합니다.

## 브랜드 자산

SVG는 편집 가능한 벡터이고 폰트 파일을 내장하지 않습니다. 동작과 이력은 [브랜드북](../docs/BRAND.md)에서 확인하세요. 빌드 시 Windows ICO는 [`scripts/make_icon.py`](../scripts/make_icon.py)로 생성되며 Pillow가 필요합니다.
