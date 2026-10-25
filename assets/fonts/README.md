# 조선굴림체 / ChosunGu

**폰트 저작권:** (주)조선일보사. **프로그램 소스 MIT 라이선스는 이 폰트에 적용되지 않습니다.**

- 원본 소개 및 사용 조건: https://event.chosun.com/100/100font.html
- 라이선스 안내 (원문 인용): https://www.sandollcloud.com/free-font/16242/ChosunGu
- 사용자 첨부 원본 파일명: `ChosunGu.TTF` (Regular)
- 서체를 변형·판매하지 않으며 별도 판매 대가를 받지 않습니다.

조선일보 전용서체는 개인·기업에 무료 제공되며 타인에게 자유롭게 배포할 수 있지만, 복사·배포 대가 청구 또는 수정 후 판매를 금지하고 원형대로 사용해야 한다는 별도 조건이 있습니다.

Electron은 `src/renderer/style.css`의 `@font-face`를 통해 `assets/fonts/ChosunGu.TTF`를 로드합니다. 폰트 파일을 포함하지 않은 개발 환경에서는 시스템 한글 글꼴로 대체 표시됩니다.

> 빌드 준비: 사용자에게 제공받은 원본을 `assets/fonts/ChosunGu.TTF`에 위치시키세요. 원본 파일의 내용을 수정하지 마세요.

## 무결성 확인 및 자동 설치

`npm run font:install`은 `fonts-archive/ChosunGu` 저장소의 고정 커밋에서 원본을 받으며, 첨부 파일과 동일한 Git blob SHA `953386f09aee424a7e8e8cb08ea4c44733bdedcb` 및 4,972,060바이트 크기를 확인한 후만 사용합니다. 이미 TTF가 있다면 다운로드하지 않고 동일성을 확인합니다. 원본을 수정하지 않습니다. npm Windows 빌드 시 prebuild 단계가 자동으로 수행합니다.

## GitHub 서브모듈로 연결

`assets/fonts/vendor`는 공개 GitHub `fonts-archive/ChosunGu`의 **동일한 원본**을 고정 커밋으로 가리키는 Git submodule입니다. `git clone --recurse-submodules` 하면 해당 공개 저장소의 파일을 가져올 수 있습니다. `npm run font:install`은 서브모듈 파일을 검증하여 `ChosunGu.TTF`로 복사하거나, 서브모듈이 없는 경우 동일한 원본을 고정 URL에서 내려받습니다.
