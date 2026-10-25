'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
test('Electron package 핀 및 Windows 포터블 타겟',()=>{const pkg=JSON.parse(read('package.json'));assert.equal(pkg.devDependencies.electron,'45.0.0');assert.ok(pkg.build.win.target.some(t=>t.target==='portable'));assert.equal(pkg.main,'src/electron/main.cjs')});
test('renderer에는 nodeIntegration 차단, context isolation',()=>{const s=read('src/electron/main.cjs');assert.match(s,/nodeIntegration:\s*false/);assert.match(s,/contextIsolation:\s*true/);assert.match(s,/sandbox:\s*true/)});
test('preload만 허용된 bridge',()=>{const s=read('src/electron/preload.cjs');assert.match(s,/contextBridge/);assert.doesNotMatch(read('src/renderer/app.js'),/require\(|child_process|eval\(/)});
test('CSP 및 접근성 시맨틱',()=>{const s=read('src/renderer/index.html');assert.match(s,/Content-Security-Policy/);assert.match(s,/aria-live="polite"/);assert.match(s,/<button/);assert.match(s,/data-testid="commit-message"/)});
test('한국어 폰트 CSS · 대체 글꼴',()=>{const s=read('src/renderer/style.css');assert.match(s,/ChosunGu\.woff2/);assert.match(s,/Malgun Gothic/);assert.match(s,/prefers-reduced-motion/)});
test('마스코트 자산 및 문서 존재',()=>{for(const f of ['assets/brand/raidian-hero.svg','assets/brand/raidian-mark.svg','README.md','LICENSE','assets/fonts/README.md'])assert.ok(fs.existsSync(path.join(root,f)),f)});
test('GitHub Actions 전체 주석 처리',()=>{for(const line of read('.github/workflows/windows-build.yml').split(/\r?\n/)){assert.ok(!line.trim()||line.trim().startsWith('#'))}});
test('릴리스 PE 검증 함수가 잘못된 헤더를 거부',async()=>{const {checkExe}=await import('../scripts/verify-windows.mjs');assert.throws(()=>checkExe(Buffer.alloc(1024)),/PE/);const b=Buffer.alloc(2048);b.write('MZ');b.writeUInt32LE(128,0x3c);b.write('PE\0\0',128);b.writeUInt16LE(0x8664,132);assert.doesNotThrow(()=>checkExe(b))});

test('폰트는 외부 연결 없이 assets/fonts에서 직접 읽는다',async()=>{
 const {verifyAssets,expectedGitSha}=await import('../scripts/font-assets.mjs');
 const info=verifyAssets();
 assert.equal(info.originalBytes,4972060);
 assert.equal(expectedGitSha,'953386f09aee424a7e8e8cb08ea4c44733bdedcb');
 assert.equal(info.woff2Bytes,1474960);
 assert.equal(fs.readFileSync(path.join(root,'assets/fonts/ChosunGu.woff2')).subarray(0,4).toString('ascii'),'wOF2');
 assert.equal(fs.existsSync(path.join(root,'.gitmodules')),false);
 const pkg=JSON.parse(read('package.json'));
 assert.ok(pkg.build.files.includes('assets/fonts/ChosunGu.woff2'));
 assert.doesNotMatch(pkg.scripts['prebuild:win'],/fetch|install-font/);
 assert.ok(!fs.existsSync(path.join(root,'scripts/install-font.mjs')));
});

test('조선굴림체 원본을 무손실로 복원할 수 있다',async()=>{
 const {verifyAssets,gitBlobSha,expectedGitSha}=await import('../scripts/font-assets.mjs');
 const result=verifyAssets({restore:true});
 assert.equal(result.originalBytes,4972060);
 assert.equal(gitBlobSha(fs.readFileSync(path.join(root,'assets/fonts/ChosunGu.TTF'))),expectedGitSha);
});
