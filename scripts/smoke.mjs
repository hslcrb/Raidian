import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
for(const file of ['src/electron/main.cjs','src/electron/preload.cjs','src/renderer/index.html','src/renderer/style.css','src/renderer/app.js','assets/brand/raidian-mark.svg']){
 const full=path.join(root,file);if(!fs.existsSync(full)||!fs.statSync(full).size)throw Error(`${file} 누락`);
}
console.log('🍒 Electron 파일 구조 스모크 검증 통과 (실제 Electron 실행 테스트는 별도)');
