'use strict';
/** Small, audited process boundary shared by Electron IPC, CLI and MCP. */
const { spawn } = require('node:child_process');
const { stat, mkdir, realpath } = require('node:fs/promises');
const path = require('node:path');
const { TextDecoder } = require('node:util');

class GitError extends Error {
  constructor(message, code = 1) { super(String(message || 'Git 작업을 완료하지 못했습니다.').trim()); this.name = 'GitError'; this.code = code; }
}
const unsafeName = (name) => typeof name !== 'string' || !name.trim() || name.startsWith('-') || /[\0\r\n]/.test(name);
function decode(data) {
  if (!Buffer.isBuffer(data)) return String(data || '');
  const utf = new TextDecoder('utf-8', { fatal: false }).decode(data);
  if (!utf.includes('\uFFFD')) return utf;
  try { return new TextDecoder('euc-kr').decode(data); } catch { return utf; }
}
async function processRun(binary, args, cwd, timeout = 90_000) {
  if (!Array.isArray(args) || args.some(x => typeof x !== 'string' || x.includes('\0'))) throw new GitError('명령 인자가 올바르지 않습니다.');
  const env = { ...process.env, GIT_TERMINAL_PROMPT: '0', GCM_INTERACTIVE: 'never' };
  return await new Promise((resolve, reject) => {
    let finished = false, timedOut = false;
    const proc = spawn(binary, args, { cwd, env, windowsHide: true, shell: false, stdio: ['ignore','pipe','pipe'] });
    let out = [], err = [], total = 0;
    const timer = setTimeout(() => { timedOut = true; proc.kill(); }, timeout);
    const fail = e => { if (!finished) { finished = true; clearTimeout(timer); reject(new GitError(e.message || e)); } };
    proc.on('error', fail);
    const add = (target, data) => { total += data.length; if (total > 16 * 1024 * 1024) { proc.kill(); fail(new Error('Git 출력이 16MiB 한도를 초과했습니다.')); } else target.push(data); };
    proc.stdout.on('data', c => add(out, c));
    proc.stderr.on('data', c => add(err, c));
    proc.on('close', code => {
      if (finished) return;
      finished = true; clearTimeout(timer);
      const stdout = decode(Buffer.concat(out)), stderr = decode(Buffer.concat(err));
      if (timedOut) return reject(new GitError('명령이 제한 시간 내 완료되지 않았습니다.'));
      if (code !== 0) return reject(new GitError(stderr.trim() || stdout.trim() || `${binary}: 종료 코드 ${code}`, code || 1));
      resolve(stdout.replace(/\n$/, ''));
    });
  });
}
function normalizeSegment(value) {
  if (String(value || '').trim().endsWith('.lock')) throw new GitError('브랜치 이름에 .lock을 사용할 수 없습니다.');
  const token = String(value || '').trim().normalize('NFC').replace(/[^\p{L}\p{N}._-]+/gu, '-').replace(/^[.\-]+|[.\-]+$/g, '');
  if (!token || token === '.' || token === '..' || token.endsWith('.lock')) throw new GitError('브랜치 단계 이름이 올바르지 않습니다.');
  return token;
}
function shaRef(value) {
  if (!/^[0-9a-f]{7,40}$/i.test(String(value))) throw new GitError('커밋 SHA는 7~40자의 16진수여야 합니다.');
  return value;
}
class Repository {
  constructor(root) { this.path = root; }
  static async open(location = '.') {
    const candidate = path.resolve(String(location));
    try { if (!(await stat(candidate)).isDirectory()) throw new GitError('Git 저장소 폴더를 선택하세요.'); }
    catch (e) { if (e instanceof GitError) throw e; throw new GitError(`폴더가 없습니다: ${candidate}`); }
    const root = await processRun('git', ['rev-parse', '--show-toplevel'], candidate);
    return new Repository(await realpath(root.trim()));
  }
  static async init(location) {
    const folder = path.resolve(String(location));
    await mkdir(folder, { recursive: true });
    await processRun('git', ['init', '-b', 'main'], folder);
    return Repository.open(folder);
  }
  git(...args) { return processRun('git', ['-c', 'core.quotepath=false', '-c', 'i18n.logOutputEncoding=utf-8', ...args], this.path); }
  gh(...args) { return processRun('gh', args, this.path); }
  async branch() { return (await this.git('branch','--show-current')).trim() || '(detached HEAD)'; }
  async branches() { return (await this.git('branch','--format=%(refname:short)')).split('\n').filter(Boolean); }
  async status() {
    const raw = await this.git('status','--porcelain=v1','-z','--untracked-files=normal');
    const parts = raw.split('\0'), output = [];
    for (let i = 0; i < parts.length; i++) {
      const item = parts[i]; if (!item) continue;
      if (item.length < 4 || item[2] !== ' ') throw new GitError('Git 상태 결과를 해석할 수 없습니다.');
      const entry = { state: item.slice(0,2), path: item.slice(3) };
      if (/[RC]/.test(entry.state)) entry.from = parts[++i];
      output.push(entry);
    }
    return output;
  }
  async history(limit=25) {
    if (!Number.isInteger(limit) || limit < 1 || limit > 200) throw new GitError('조회 범위는 1~200입니다.');
    let raw; try { raw = await this.git('log', `-${limit}`, '--date=short', '--format=%H%x1f%an%x1f%ad%x1f%s%x1e'); }
    catch (e) { if (/does not have any commits yet|your current branch|unknown revision or path/i.test(e.message)) return []; throw e; }
    return raw.split('\x1e').map(s => s.trim().split('\x1f')).filter(a => a.length === 4)
      .map(([sha,author,date,message]) => ({sha,author,date,message}));
  }
  async remotes() {
    const entries=[];
    for (const line of (await this.git('remote','-v')).split('\n')) {
      const match=/^(\S+)\s+(.+?)\s+\((fetch|push)\)$/.exec(line);
      if(match) entries.push({name:match[1],url:match[2],kind:match[3]});
    }
    return entries;
  }
  async snapshot(){const [branch,files,history,remotes,branches]=await Promise.all([this.branch(),this.status(),this.history(),this.remotes(),this.branches()]);return {repository:this.path,branch,files,history,remotes,branches};}
  async ensureClean(){if((await this.status()).length) throw new GitError('미커밋 변경이 있습니다. 커밋하거나 보관한 후 진행하세요.');}
  static messageFor(files) {
    if (!files.length) throw new GitError('커밋할 변경 사항이 없습니다.');
    const codes=files.map(f=>f.state), paths=files.map(f=>f.path.toLowerCase());
    if(codes.every(c=>c.includes('D'))) return 'chore: 삭제된 파일 정리';
    if(paths.every(f=>/\.(md|rst|txt)$/.test(f))) return 'docs: 문서 업데이트';
    if(codes.every(c=>c==='??'||c.includes('A'))) return 'feat: 새 파일 추가';
    if(codes.every(c=>c.includes('R'))) return 'refactor: 파일 구조 정리';
    return 'chore: 변경 사항 업데이트';
  }
  async commit(message='',stageAll=true) {
    const before = await this.status();
    if (!before.length) throw new GitError('변경 사항이 없어 커밋하지 않았습니다.');
    if (stageAll) await this.git('add','--all');
    const staged = (await this.git('diff','--cached','--name-only','-z')).split('\0').filter(Boolean);
    if (!staged.length) throw new GitError('스테이징된 변경 파일이 없습니다.');
    const text = String(message || '').trim() || Repository.messageFor(before.filter(f=>staged.includes(f.path)));
    if (text.includes('\0')||text.includes('\n') || text.length>500) throw new GitError('커밋 메시지 형식을 확인하세요.');
    return await this.git('commit','-m',text);
  }
  async createBranch(name, base=null, switchBranch=true) {
    if(unsafeName(name)) throw new GitError('브랜치 이름이 올바르지 않습니다.');
    await this.git('check-ref-format','--branch',name);
    if(switchBranch) await this.ensureClean();
    return switchBranch ? this.git('switch','-c',name,...(base?[base]:[])) : this.git('branch',name,...(base?[base]:[]));
  }
  async nestedBranch(group,detail,base=null){const name=`chatgpt-extrahigh/${normalizeSegment(group)}/${normalizeSegment(detail)}`;await this.createBranch(name,base);return name;}
  async switch(name){if(unsafeName(name)) throw new GitError('브랜치 이름을 확인하세요.');await this.ensureClean();return this.git('switch',name);}
  async merge(source){if(unsafeName(source))throw new GitError('병합할 브랜치를 확인하세요.');await this.ensureClean();if(source===await this.branch())throw new GitError('자기 브랜치는 병합할 수 없습니다.');return this.git('merge','--no-ff','--no-edit',source);}
  async cherryPick(sha){await this.ensureClean();return this.git('cherry-pick','--no-edit',shaRef(sha));}
  async revert(sha){await this.ensureClean();return this.git('revert','--no-edit',shaRef(sha));}
  async remoteAdd(name,url){if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(name)||unsafeName(url))throw new GitError('원격 이름과 주소를 확인하세요.');return this.git('remote','add',name,url);}
  async remoteRemove(name){if(!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(name))throw new GitError('원격 이름이 올바르지 않습니다.');return this.git('remote','remove',name);}
  async hasUpstream(){try{await this.git('rev-parse','--abbrev-ref','@{upstream}');return true;}catch{return false;}}
  async push(remote='origin'){
    if(!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(remote))throw new GitError('원격 이름이 올바르지 않습니다.');
    const branch=await this.branch();if(branch.startsWith('('))throw new GitError('분리된 HEAD 상태에서는 푸시하지 않습니다.');
    if(await this.hasUpstream()) return this.git('push',remote);
    return this.git('push','--set-upstream',remote,branch);
  }
  async fetch(remote='--all') {if(remote==='--all')return this.git('fetch','--all','--prune');if(!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(remote))throw new GitError('원격 이름이 올바르지 않습니다.');return this.git('fetch','--prune',remote);}
  async pull(remote='origin'){await this.ensureClean();if(!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(remote))throw new GitError('원격 이름이 올바르지 않습니다.');const branch=await this.branch();return this.git('pull','--no-rebase','--no-ff',remote,branch);}
  async githubPrs(){return JSON.parse(await this.gh('pr','list','--json','number,title,headRefName,url','--limit','25'));}
  async githubPrCreate(base='main'){if(unsafeName(base))throw new GitError('기준 브랜치가 올바르지 않습니다.');return this.gh('pr','create','--fill','--base',base);}
  async diff(file='') { if(file && (file.startsWith('-')||file.includes('\0')))throw new GitError('파일 경로를 확인하세요.');return this.git('diff','--',...(file?[file]:[])); }
}
module.exports={Repository,GitError,processRun,decode,normalizeSegment};
