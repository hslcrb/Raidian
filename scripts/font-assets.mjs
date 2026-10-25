#!/usr/bin/env node
/** Check repository-vendored ChosunGu assets and optionally restore the exact uploaded TTF. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const fonts = path.join(root, 'assets', 'fonts');
const ttf = path.join(fonts, 'ChosunGu.TTF');
const packed = path.join(fonts, 'ChosunGu.TTF.gz');
const webfont = path.join(fonts, 'ChosunGu.woff2');
const expectedTTFSize = 4972060;
const expectedGitSha = '953386f09aee424a7e8e8cb08ea4c44733bdedcb';
const expectedPackedSha256 = '06301ef89b447097ba5dd5d21b0614dcc0a4c352fb54dc48ebf4b1acb1e124dc';
const expectedWebfontSha256 = '730b5342ca75792fbd6b2fe9fada4e2fe24bd9fb0a2a158277b8f0fcc8f47606';

function gitBlobSha(buffer) {
  return crypto.createHash('sha1')
    .update(Buffer.from(`blob ${buffer.length}\0`))
    .update(buffer).digest('hex');
}
function sha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}
function verifyAssets({restore = false} = {}) {
  // Both assets are committed to this repository. This function never downloads fonts.
  for (const file of [packed, webfont]) {
    if (!fs.existsSync(file)) throw new Error(`폰트 파일을 찾을 수 없습니다: ${path.relative(root, file)}`);
  }
  const packedBytes = fs.readFileSync(packed);
  const webBytes = fs.readFileSync(webfont);
  if (sha256(packedBytes) !== expectedPackedSha256) throw new Error('원본 TTF 압축본의 SHA-256 검증 실패');
  if (sha256(webBytes) !== expectedWebfontSha256) throw new Error('웹폰트의 SHA-256 검증 실패');
  if (webBytes.toString('ascii', 0, 4) !== 'wOF2') throw new Error('WOFF2 헤더가 올바르지 않습니다.');
  const original = zlib.gunzipSync(packedBytes);
  if (original.length !== expectedTTFSize || gitBlobSha(original) !== expectedGitSha) {
    throw new Error('첨부한 조선굴림체 TTF 원본과 일치하지 않습니다.');
  }
  if (fs.existsSync(ttf) && gitBlobSha(fs.readFileSync(ttf)) !== expectedGitSha) {
    throw new Error('로컬 ChosunGu.TTF가 원본과 다릅니다. 안전을 위해 덮어쓰지 않습니다.');
  }
  if (restore && !fs.existsSync(ttf)) fs.writeFileSync(ttf, original, {flag: 'wx'});
  return {woff2Bytes: webBytes.length, archiveBytes: packedBytes.length, originalBytes: original.length, restored: restore};
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const result = verifyAssets({restore: process.argv.includes('--restore')});
    console.log(`🍒 조선굴림체 저장소 에셋 검증 완료 · 원본 ${result.originalBytes.toLocaleString()} bytes${result.restored ? ' · TTF 복원 완료' : ''}`);
  } catch (err) {console.error(err.message); process.exitCode = 1;}
}
export {gitBlobSha, verifyAssets, expectedGitSha};
