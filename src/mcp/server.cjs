'use strict';
/** STDIO JSON-RPC MCP server. No generic command execution. */
const readline=require('node:readline');
const {Repository,GitError}=require('../core/git.cjs');
const {dispatch,ACTIONS,MUTATIONS}=require('../core/commands.cjs');
const pkg=require('../../package.json');
const DESCRIPTIONS={status:{},log:{limit:'integer'},branches:{},remotes:{},diff:{file:'string'},'agent-guide':{},doctor:{},
 commit:{message:'string',stageAll:'boolean'},'branch-create':{name:'string',base:'string',switch:'boolean'},'branch-child':{group:'string',detail:'string',base:'string'},switch:{name:'string'},merge:{source:'string'},'copy-commit':{sha:'string'},revert:{sha:'string'},'remote-add':{name:'string',url:'string'},'remote-remove':{name:'string'},fetch:{remote:'string'},pull:{remote:'string'},push:{remote:'string'},'gh-prs':{},'gh-pr-create':{base:'string'}};
const REQUIRED={'branch-create':['name'],'branch-child':['group','detail'],switch:['name'],merge:['source'],'copy-commit':['sha'],revert:['sha'],'remote-add':['name','url'],'remote-remove':['name']};
function toolsCatalog(allowWrite){return Object.keys(DESCRIPTIONS).filter(k=>allowWrite||!MUTATIONS.has(k)).map(name=>{
 const properties=Object.fromEntries(Object.entries(DESCRIPTIONS[name]).map(([key,type])=>[key,{type}]));
 if(MUTATIONS.has(name))properties.confirm={type:'boolean',const:true,description:'사용자 승인 후 true를 전달하세요.'};
 return {name:`git_${name.replaceAll('-','_')}`,description:ACTIONS[name],inputSchema:{type:'object',properties,required:[...(REQUIRED[name]||[]),...(MUTATIONS.has(name)?['confirm']:[])],additionalProperties:false}};
});}
class Server {
 constructor(repo,allowWrite=false){this.repo=repo;this.allowWrite=allowWrite;}
 async handle(obj){if(!obj||typeof obj!=='object'||Array.isArray(obj))return {jsonrpc:'2.0',id:null,error:{code:-32600,message:'Invalid Request'}};
  if(!Object.hasOwn(obj,'id'))return null;
  const {id,method,params={}}=obj;
  if(typeof method!=='string'||!params||typeof params!=='object')return {jsonrpc:'2.0',id,error:{code:-32600,message:'Invalid Request'}};
  let result;
  try{
   if(method==='initialize')result={protocolVersion:'2025-11-25',capabilities:{tools:{listChanged:false}},serverInfo:{name:'raidian',version:pkg.version},instructions:'읽기 전용 기본. 변경 도구는 --allow-write 와 confirm:true 필요.'};
   else if(method==='server/discover')result={protocolVersion:'2026-07-28',capabilities:{tools:{}},serverInfo:{name:'raidian',version:pkg.version}};
   else if(method==='ping')result={};
   else if(method==='tools/list')result={tools:toolsCatalog(this.allowWrite)};
   else if(method==='tools/call'){
    const name=params.name,arguments_=params.arguments||{};
    if(typeof name!=='string'||!name.startsWith('git_'))throw new GitError('도구 이름이 유효하지 않습니다.');
    const action=name.slice(4).replaceAll('_','-');
    if(!Object.hasOwn(DESCRIPTIONS,action))throw new GitError('허용되지 않은 MCP 도구입니다.');
    try{const data=await dispatch(action,arguments_,{repository:this.repo,mcp:true,allowWrite:this.allowWrite});
      const payload={ok:true,data,agent_hint:'쓰기 이후 status를 확인하세요.'};
      result={content:[{type:'text',text:JSON.stringify(payload)}],structuredContent:payload,isError:false};
    }catch(e){const payload={ok:false,error:e.message,agent_hint:'실패 시 status를 읽고 충돌을 검사하세요.'};result={content:[{type:'text',text:JSON.stringify(payload)}],structuredContent:payload,isError:true};}
   } else return {jsonrpc:'2.0',id,error:{code:-32601,message:'Method not found'}};
   return {jsonrpc:'2.0',id,result};
  }catch(e){return {jsonrpc:'2.0',id,error:{code:-32602,message:e.message}}}
 }
}
async function main(args=process.argv.slice(2)){
 const i=args.indexOf('--repo');if(i<0||!args[i+1]){console.error('사용법: raidian-mcp --repo /path/to/repo [--allow-write]');return 2}
 const allowWrite=args.includes('--allow-write');let server;try{server=new Server(await Repository.open(args[i+1]),allowWrite)}catch(e){console.error(e.message);return 1}
 const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});for await (const line of rl){if(!line.trim())continue;let response;try{response=await server.handle(JSON.parse(line))}catch(e){response={jsonrpc:'2.0',id:null,error:{code:-32700,message:'Parse error'}}}if(response)process.stdout.write(JSON.stringify(response)+'\n')}
 return 0;
}
module.exports={Server,main,toolsCatalog};
