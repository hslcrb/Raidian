'use strict';
const { Repository, GitError } = require('./git.cjs');
const { execFileSync } = require('node:child_process');
const pkg = require('../../package.json');
const MUTATIONS = new Set(['init','commit','branch-create','branch-child','switch','merge','copy-commit','revert','remote-add','remote-remove','fetch','pull','push','gh-pr-create']);
const CONFIRM = new Set(['merge','copy-commit','revert','remote-remove','gh-pr-create']);
const ACTIONS = Object.freeze({
  status:'변경 파일', log:'커밋 기록', branches:'브랜치 목록', remotes:'원격 목록', diff:'파일 변경 비교',
  'agent-guide':'AI 에이전트 안내', doctor:'개발 환경 검사', init:'새 저장소 생성',
  commit:'로컬 커밋 작성', 'branch-create':'브랜치 만들기', 'branch-child':'작업 분류별 브랜치', switch:'브랜치 이동',
  merge:'no-ff 병합', 'copy-commit':'특정 커밋 복사', revert:'특정 커밋의 변경만 되돌리기',
  'remote-add':'원격 추가', 'remote-remove':'원격 제거', fetch:'원격 정보 가져오기', pull:'원격 통합(no-ff)',push:'원격 푸시',
  'gh-prs':'GitHub PR 목록', 'gh-pr-create':'GitHub PR 생성'
});
function agentGuide(){return {
  application:'Raidian',version:pkg.version,encoding:'UTF-8',
  interfaces:{gui:'npm start',cli:'node bin/raidian.cjs --repo PATH --json status',mcp:'node bin/raidian-mcp.cjs --repo PATH',interactive:'node bin/raidian.cjs shell'},
  defaults:{merge:'--no-ff --no-edit',commit:'빈 메시지는 변경 유형으로 자동 한국어 Conventional Commit',history:'revert (원본 이력 삭제 없음)',mcp:'읽기 전용; --allow-write + confirm:true'},
  safety:['변경 전 git 상태를 조회하세요','임의 shell 실행이나 force push는 지원하지 않습니다','브랜치 이름의 /는 실제 부모 분기 관계를 보장하지 않습니다'],
  actions:ACTIONS,
};}
function which(command) {try{return execFileSync(process.platform==='win32'?'where':'which',[command],{encoding:'utf8',timeout:3000}).trim().split(/\r?\n/)[0]}catch{return null}}
function doctor(){return {version:pkg.version,node:process.version,platform:process.platform,git:which('git'),gh:which('gh'),electron:Boolean(process.versions.electron),font:'assets/fonts/ChosunGu.woff2'};}
function checkAction(action) { if(!Object.hasOwn(ACTIONS,action))throw new GitError(`지원하지 않는 작업: ${action}`); }
async function dispatch(action,args={},context={}){
  checkAction(action);
  if(!args||typeof args!=='object'||Array.isArray(args))throw new GitError('입력은 JSON 객체여야 합니다.');
  if(context.mcp){
    if(MUTATIONS.has(action)&&!context.allowWrite)throw new GitError('MCP 서버가 읽기 전용입니다. --allow-write 필요');
    if(MUTATIONS.has(action)&&args.confirm!==true)throw new GitError('Git 변경 작업에는 confirm:true가 필요합니다.');
  } else if(context.requireConfirmation&&CONFIRM.has(action)&&args.confirm!==true){throw new GitError('이력에 영향을 줄 수 있습니다. 확인 후 실행해 주세요.');}
  if(action==='doctor')return doctor();
  if(action==='agent-guide')return agentGuide();
  if(action==='init'){
    if(context.mcp)throw new GitError('MCP에서는 새 폴더 생성을 허용하지 않습니다.');
    if(!args.path||typeof args.path!=='string')throw new GitError('생성할 폴더 경로가 필요합니다.');
    return {repository:(await Repository.init(args.path)).path};
  }
  const r = context.repository || await Repository.open(context.repo||'.');
  switch(action){
    case 'status':return {branch:await r.branch(),files:await r.status()};
    case 'log':return r.history(args.limit===undefined?25:Number(args.limit));
    case 'branches':return {active:await r.branch(),branches:await r.branches()};
    case 'remotes':return r.remotes();
    case 'diff':return r.diff(args.file||'');
    case 'commit':return r.commit(args.message||'',args.stageAll!==false);
    case 'branch-create':return r.createBranch(args.name,args.base||null,args.switch!==false);
    case 'branch-child':return r.nestedBranch(args.group,args.detail,args.base||null);
    case 'switch':return r.switch(args.name);
    case 'merge':return r.merge(args.source);
    case 'copy-commit':return r.cherryPick(args.sha);
    case 'revert':return r.revert(args.sha);
    case 'remote-add':return r.remoteAdd(args.name,args.url);
    case 'remote-remove':return r.remoteRemove(args.name);
    case 'fetch':return r.fetch(args.remote||'--all');
    case 'pull':return r.pull(args.remote||'origin');
    case 'push':return r.push(args.remote||'origin');
    case 'gh-prs':return r.githubPrs();
    case 'gh-pr-create':return r.githubPrCreate(args.base||'main');
    default:throw new GitError('명령 구현을 찾을 수 없습니다.');
  }
}
module.exports={dispatch,doctor,agentGuide,ACTIONS,MUTATIONS,CONFIRM};
