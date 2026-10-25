'use strict';
const test=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {Repository,GitError,processRun,decode,normalizeSegment}=require('../src/core/git.cjs');
async function fixture(){const base=fs.mkdtempSync(path.join(os.tmpdir(),'레이디안-git-'));const repo=await Repository.init(base);await repo.git('config','user.email','tests@example.test');await repo.git('config','user.name','루비 테스트');return {repo,base,cleanup:()=>fs.rmSync(base,{recursive:true,force:true})}}
async function seed(repo,file='README.md',value='hi'){fs.writeFileSync(path.join(repo.path,file),value);await repo.commit('feat: 초기 커밋')}
async function changed(repo,file,value){fs.writeFileSync(path.join(repo.path,file),value);await repo.commit('feat: 변경')}
const tests=[
 ['한글 경로와 공백 status',async()=>{const x=await fixture();try{fs.writeFileSync(path.join(x.base,'한글 공백.txt'),'한글');const s=await x.repo.status();assert.equal(s[0].path,'한글 공백.txt');assert.equal(s[0].state,'??')}finally{x.cleanup()}}],
 ['한글·개행 포함 파일명 보존',async()=>{if(process.platform==='win32')return;const x=await fixture();try{fs.writeFileSync(path.join(x.base,'한글\n별.txt'),'a');assert.equal((await x.repo.status())[0].path,'한글\n별.txt')}finally{x.cleanup()}}],
 ['자동 메시지는 기능 파일 추가',async()=>{const x=await fixture();try{fs.writeFileSync(path.join(x.base,'안녕.js'),'ok');await x.repo.commit();assert.match((await x.repo.history())[0].message,/^feat: 새 파일 추가/)}finally{x.cleanup()}}],
 ['문서만 수정하면 docs 자동 분류',async()=>{const x=await fixture();try{fs.writeFileSync(path.join(x.base,'README.md'),'hi');await x.repo.commit();fs.writeFileSync(path.join(x.base,'README.md'),'hi again');await x.repo.commit();assert.match((await x.repo.history())[0].message,/^docs:/)}finally{x.cleanup()}}],
 ['변경 없음 커밋 방지',async()=>{const x=await fixture();try{await assert.rejects(()=>x.repo.commit(),GitError)}finally{x.cleanup()}}],
 ['체크인된 파일이 한글명으로 이력에 표시',async()=>{const x=await fixture();try{await seed(x.repo,'안녕하세요.txt','봄');const h=await x.repo.history();assert.equal(h.length,1);assert.equal(h[0].author,'루비 테스트')}finally{x.cleanup()}}],
 ['작업 변경 시 브랜치 전환 금지',async()=>{const x=await fixture();try{await seed(x.repo);await x.repo.createBranch('other',null,false);fs.writeFileSync(path.join(x.base,'새파일.txt'),'x');await assert.rejects(()=>x.repo.switch('other'),/미커밋/)}finally{x.cleanup()}}],
 ['no-ff 병합 커밋은 두 부모를 가짐',async()=>{const x=await fixture();try{await seed(x.repo);await x.repo.createBranch('feature/one');await changed(x.repo,'side.txt','side');await x.repo.switch('main');await x.repo.merge('feature/one');const sha=await x.repo.git('rev-parse','HEAD');const parts=(await x.repo.git('rev-list','--parents','-n','1',sha)).split(' ');assert.equal(parts.length,3)}finally{x.cleanup()}}],
 ['브랜치 이름은 chatgpt-extrahigh 네임스페이스',async()=>{const x=await fixture();try{await seed(x.repo);const name=await x.repo.nestedBranch('기능','한글 작업');assert.equal(name,'chatgpt-extrahigh/기능/한글-작업');assert.equal(await x.repo.branch(),name)}finally{x.cleanup()}}],
 ['브랜치 생성 전 이름 검증',async()=>{const x=await fixture();try{await seed(x.repo);await assert.rejects(()=>x.repo.createBranch('-oops'),GitError);await assert.rejects(()=>x.repo.nestedBranch('..','ok'),GitError)}finally{x.cleanup()}}],
 ['cherry-pick 과거 커밋 새 기록 적용',async()=>{const x=await fixture();try{await seed(x.repo);await x.repo.createBranch('feature/a');await changed(x.repo,'one.txt','A');const sha=await x.repo.git('rev-parse','HEAD');await x.repo.switch('main');await x.repo.cherryPick(sha);assert.equal(fs.readFileSync(path.join(x.base,'one.txt'),'utf8'),'A');assert.equal((await x.repo.history()).length,2)}finally{x.cleanup()}}],
 ['revert는 취소를 새 커밋에 보관',async()=>{const x=await fixture();try{await seed(x.repo);await changed(x.repo,'undo.txt','U');const sha=await x.repo.git('rev-parse','HEAD');await x.repo.revert(sha);assert.equal(fs.existsSync(path.join(x.base,'undo.txt')),false);assert.equal((await x.repo.history()).length,3)}finally{x.cleanup()}}],
 ['커밋 SHA 형식 검증',async()=>{const x=await fixture();try{await seed(x.repo);await assert.rejects(()=>x.repo.revert('--hard'),/SHA/);await assert.rejects(()=>x.repo.cherryPick('hi'),/SHA/)}finally{x.cleanup()}}],
 ['다중 원격 추가·삭제',async()=>{const x=await fixture();try{await x.repo.remoteAdd('origin','https://github.com/hslcrb/Raidian.git');await x.repo.remoteAdd('backup','ssh://example.test/backup');assert.deepEqual([...new Set((await x.repo.remotes()).map(x=>x.name))].sort(),['backup','origin']);await x.repo.remoteRemove('backup');assert.deepEqual([...new Set((await x.repo.remotes()).map(x=>x.name))],['origin'])}finally{x.cleanup()}}],
 ['원격 인자 검증',async()=>{const x=await fixture();try{await assert.rejects(()=>x.repo.remoteAdd('--upload-pack=bad','url'),GitError);await assert.rejects(()=>x.repo.fetch('-p'),GitError);await assert.rejects(()=>x.repo.push('-x'),GitError)}finally{x.cleanup()}}],
 ['커밋 범위 제한 및 빈 기록 처리',async()=>{const x=await fixture();try{assert.deepEqual(await x.repo.history(),[]);await assert.rejects(()=>x.repo.history(900),GitError)}finally{x.cleanup()}}],
 ['직접 셸 없이 git 인자 배열',async()=>{const x=await fixture();try{const s=await processRun('git',['rev-parse','--is-inside-work-tree'],x.base);assert.equal(s,'true');await assert.rejects(()=>processRun('git',['bad\0arg'],x.base),GitError)}finally{x.cleanup()}}],
 ['UTF-8·CP949 출력 디코딩',()=>{assert.equal(decode(Buffer.from('한글','utf8')),'한글');assert.equal(decode(Buffer.from([0xc7,0xd1,0xb1,0xdb])),'한글')}],
 ['계층 이름 조각 정규화',()=>{assert.equal(normalizeSegment('안녕 / 세상'),'안녕-세상');assert.throws(()=>normalizeSegment('.lock'),GitError)}],
 ['스테이징 없이 커밋 시 처리',async()=>{const x=await fixture();try{fs.writeFileSync(path.join(x.base,'note.txt'),'hi');await assert.rejects(()=>x.repo.commit('',false),/스테이징/)}finally{x.cleanup()}}]
];
for(const [name,fn] of tests)test(name,fn);
