#!/usr/bin/env node
/** Install original font from a pinned public GitHub mirror if not supplied locally. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const destination=path.join(root,'assets','fonts','ChosunGu.TTF');
const vendor=path.join(root,'assets','fonts','vendor','ChosunGu.TTF');
const expectedGitSha='953386f09aee424a7e8e8cb08ea4c44733bdedcb';
const source='https://raw.githubusercontent.com/fonts-archive/ChosunGu/2a24ae8662e620f88c2783bc08e52453cb93c144/ChosunGu.TTF';
function gitBlobSha(buffer){return crypto.createHash('sha1').update(Buffer.from(`blob ${buffer.length}\0`)).update(buffer).digest('hex')}
async function installFont({download=true}={}){
 if(fs.existsSync(destination)){
  const buf=fs.readFileSync(destination);
  if(gitBlobSha(buf)!==expectedGitSha)throw Error('조선굴림체 파일 검증 실패: 첨부 원본과 SHA가 다릅니다.');
  return {status:'verified-local',bytes:buf.length};
 }
 if(fs.existsSync(vendor)){
  const buf=fs.readFileSync(vendor);
  if(gitBlobSha(buf)!==expectedGitSha)throw Error('고정 서브모듈 폰트 Git SHA가 원본과 다릅니다.');
  fs.writeFileSync(destination,buf,{flag:'wx'});
  return {status:'verified-git-submodule',bytes:buf.length};
 }
 if(!download)throw Error('assets/fonts/ChosunGu.TTF 파일이 없습니다.');
 console.log('공개 아카이브에서 동일 원본 조선굴림체를 확인한 뒤 내려받습니다…');
 const response=await fetch(source,{signal:AbortSignal.timeout(60000)});
 if(!response.ok)throw Error(`폰트 다운로드 실패: HTTP ${response.status}`);
 const expectedSize=4972060;
 const bytes=Buffer.from(await response.arrayBuffer());
 if(bytes.length!==expectedSize||gitBlobSha(bytes)!==expectedGitSha)throw Error('받은 폰트의 원본 Git SHA / 크기가 다릅니다. 배포를 중단합니다.');
 fs.mkdirSync(path.dirname(destination),{recursive:true});fs.writeFileSync(destination,bytes,{flag:'wx'});
 return {status:'verified-downloaded',bytes:bytes.length};
}
if(process.argv[1]?.endsWith('install-font.mjs')) installFont().then(x=>console.log(`✓ 조선굴림체 준비: ${x.status} (${x.bytes} bytes)`)).catch(e=>{console.error(e.message);process.exitCode=1});
export {gitBlobSha,installFont,expectedGitSha,source};
