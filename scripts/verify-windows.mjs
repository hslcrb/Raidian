#!/usr/bin/env node
/** Fail closed: do not mistake a Linux file or empty placeholder for Windows EXE. */
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {execFileSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const pkg=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));
const dist=path.join(root,'dist');
const names=[`Raidian-${pkg.version}-win-x64-portable.exe`,`Raidian-${pkg.version}-win-x64.zip`];
const checksums=[];const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
function checkExe(buffer){if(buffer.length<512||buffer.toString('ascii',0,2)!=='MZ')throw new Error('유효한 Windows PE가 아닙니다.');const offset=buffer.readUInt32LE(0x3c);if(offset+6>buffer.length||buffer.toString('ascii',offset,offset+4)!=='PE\0\0'||buffer.readUInt16LE(offset+4)!==0x8664)throw new Error('Windows x64 PE 헤더가 없습니다.');}
function verify(){if(!fs.existsSync(dist))throw new Error('dist/가 없습니다. Windows 빌드가 필요합니다.');for(const name of names){const loc=path.join(dist,name);if(!fs.existsSync(loc))throw new Error(`필수 산출물 누락: ${name}`);const info=fs.statSync(loc);if(info.size<1024*1024)throw new Error(`산출물이 비정상적으로 작습니다: ${name}`);if(name.endsWith('.exe'))checkExe(fs.readFileSync(loc));if(name.endsWith('.zip')){const bytes=fs.readFileSync(loc);if(bytes.subarray(0,2).toString()!=='PK')throw new Error('ZIP 헤더가 없습니다.');}checksums.push(`${sha(loc)}  ${name}`)}
 const commit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();if(!/^[a-f0-9]{40}$/.test(commit))throw new Error('정확한 소스 Git 커밋을 찾지 못했습니다.');
 const metadata={application:'Raidian',version:pkg.version,target:'windows-x64',sourceCommit:commit,artifacts:names,createdAt:new Date().toISOString()};
 fs.writeFileSync(path.join(dist,'BUILD-INFO.json'),JSON.stringify(metadata,null,2)+'\n');checksums.push(`${sha(path.join(dist,'BUILD-INFO.json'))}  BUILD-INFO.json`);fs.writeFileSync(path.join(dist,'SHA256SUMS.txt'),checksums.join('\n')+'\n');console.log('✓ Verified Windows PE/ZIP and SHA256',commit);
}
if(import.meta.url===`file://${process.argv[1]}`||process.argv[1]?.endsWith('verify-windows.mjs')){try{verify()}catch(error){console.error('검증 실패:',error.message);process.exitCode=1}}
export {checkExe,verify};
