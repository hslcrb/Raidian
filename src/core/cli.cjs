'use strict';
const readline=require('node:readline/promises');
const {stdin: input,stdout: output}=require('node:process');
const {dispatch,ACTIONS,MUTATIONS}=require('./commands.cjs');
const pkg=require('../../package.json');
const HELP=`🍒 Raidian ${pkg.version} · 작은 Git 작업실
사용법: raidian [--repo PATH] [--json] 명령 [인자] [옵션]
명령: ${Object.keys(ACTIONS).join(', ')}
대화형: raidian shell   |   UI: raidian gui   |   안내: raidian agent-guide
예시: raidian --repo . --json status
      raidian commit                  (자동 메시지)
      raidian branch-child feature korean-path
      raidian merge feature/new --yes (기본 no-ff)
      raidian copy-commit 01234567 --yes
      raidian remote-add backup https://github.com/owner/repo.git
      raidian --json doctor
`;
function tokenize(line){const result=[];let cur='',quote='',escape=false;for(const c of line){if(escape){cur+=c;escape=false;continue}if(c==='\\' && quote==='"'){escape=true;continue}if(quote){if(c===quote)quote='';else cur+=c;continue}if(c==='"'||c==="'"){quote=c;continue}if(/\s/.test(c)){if(cur){result.push(cur);cur=''}continue}cur+=c}if(quote)throw new Error('따옴표를 닫으세요.');if(cur)result.push(cur);return result;}
function parse(argv){const x={repo:'.',json:false,action:null,args:{},yes:false};const parts=[];
 for(let i=0;i<argv.length;i++){
  const a=argv[i], next=()=>{if(i+1>=argv.length)throw new Error(`${a} 값이 필요합니다.`);return argv[++i]};
  if(a==='--repo')x.repo=next();else if(a==='--json')x.json=true;else if(a==='--yes')x.yes=true;
  else if(a==='--version')x.action='version';else if(a==='--help'||a==='-h')x.action='help';
  else if(a==='--limit')x.args.limit=Number(next());else if(a==='-m'||a==='--message')x.args.message=next();
  else if(a==='--from')x.args.base=next();else if(a==='--no-switch')x.args.switch=false;else if(a==='--no-stage')x.args.stageAll=false;
  else if(a==='--remote')x.args.remote=next();else if(a==='--base')x.args.base=next();else if(a==='--file')x.args.file=next();
  else if(a.startsWith('-'))throw new Error(`알 수 없는 옵션: ${a}`);else parts.push(a);
 }
 if(x.action!=='help'&&x.action!=='version')x.action=parts.shift()||'gui';
 const a=x.args;
 switch(x.action){
  case 'init':a.path=parts[0];break;
  case 'branch-create':case 'switch':a.name=parts[0];break;
  case 'branch-child':a.group=parts[0];a.detail=parts[1];break;
  case 'merge':a.source=parts[0];break;
  case 'copy-commit':case 'revert':a.sha=parts[0];break;
  case 'remote-add':a.name=parts[0];a.url=parts[1];break;
  case 'remote-remove':a.name=parts[0];break;
  case 'diff':a.file=a.file||parts[0]||'';break;
  case 'commit':break;
  default:if(parts.length)throw new Error(`불필요한 인자: ${parts.join(' ')}`);
 }
 a.confirm=x.yes;return x;
}
async function execute(argv,{print=true}={}){
 const opt=parse(argv);
 if(opt.action==='help'){if(print)console.log(HELP);return {ok:true,data:HELP}};
 if(opt.action==='version'){if(print)console.log(pkg.version);return {ok:true,data:pkg.version}};
 if(opt.action==='gui'){if(!process.versions.electron)throw new Error('GUI는 Electron 런타임에서 실행합니다. npm start를 사용하세요.');return {ok:true,data:'GUI started'}};
 if(opt.action==='shell'){await shell(opt.repo);return {ok:true,data:'종료'}};
 const data=await dispatch(opt.action,opt.args,{repo:opt.repo,requireConfirmation:true});
 if(print)console.log(opt.json?JSON.stringify({ok:true,data},null,2):(typeof data==='string'?data:JSON.stringify(data,null,2)));
 return {ok:true,data};
}
async function shell(repo){let root=repo;const rl=readline.createInterface({input,output});console.log('🍒 Raidian 명령 셸 · help / exit / cd 경로');try{while(true){const line=(await rl.question('raidian> ')).trim();if(!line)continue;if(['exit','quit'].includes(line))break;if(['help','?'].includes(line)){console.log(HELP);continue}try{const a=tokenize(line);if(a[0]==='cd'){if(!a[1])throw new Error('경로가 필요합니다.');root=a[1];console.log(root);continue}await execute(['--repo',root,...a])}catch(e){console.error('오류:',e.message)}}}catch(e){if(e.code!=='ERR_USE_AFTER_CLOSE'&&e.code!=='ERR_INVALID_STATE')throw e}finally{rl.close()}}
async function main(argv=process.argv.slice(2)){try{await execute(argv);return 0}catch(e){if(argv.includes('--json'))console.log(JSON.stringify({ok:false,error:e.message},null,2));else console.error(`오류: ${e.message}`);return 1}}
module.exports={main,parse,tokenize,execute,HELP};
