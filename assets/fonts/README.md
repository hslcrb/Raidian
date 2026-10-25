# 조선굴림체 / ChosunGu 🍒

> **폰트 에셋은 전부 이 저장소 안에 있어요.** 서브모듈, GitHub 폰트 미러, 자동 다운로드는 필요하지 않습니다.

| 저장소 파일 | 내용과 용도 |
|---|---|
| `ChosunGu.woff2` | Electron 화면에서 직접 사용하는 웹폰트 (WOFF2, 1,474,960 bytes) |
| `ChosunGu.TTF.gz` | 사용자가 첨부한 **원본 `ChosunGu.TTF` 4,972,060 bytes를 무손실 gzip 보관** (2,142,322 bytes) |
| `ChosunGu.TTF` | `npm run font:restore`로 정확히 복구할 수 있는 로컬 파일 (기본 Git 추적에서는 제외) |

원본 Git blob SHA-1: `953386f09aee424a7e8e8cb08ea4c44733bdedcb`  
원본 SHA-256: `d6fab61a754bc7bfd0e5e4259b3ab4156f0386a0ada0679329a31d130f38da81`

```bash
npm run font:verify  # WOFF2와 압축 원본의 SHA-256, 복원한 TTF의 원본 Git SHA 검사
npm run font:restore # 네트워크 없이 ChosunGu.TTF를 같은 폴더에 정확히 복구
```

`src/renderer/style.css`의 `@font-face`는 WOFF2를 직접 읽습니다. `npm run build:win`은 폰트 검증을 통과한 다음에만 빌드를 시작합니다. 원본은 압축 *보관*이므로 TTF 바이트를 변경하지 않으며, WOFF2는 Electron 표시용 파생 웹폰트입니다.

## 저작권 및 이용 조건

**서체 권리자:** (주)조선일보사. 프로그램 소스의 MIT 라이선스가 이 서체에 적용되지는 않습니다. 원본 소개 및 배포 조건은 [조선일보 공식 안내](https://event.chosun.com/100/100font.html)를 확인하세요. 폰트의 별도 판매나 허가되지 않은 수정·재배포를 하지 마세요.
