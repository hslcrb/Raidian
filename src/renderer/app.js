'use strict';
// Renderer gets only audited methods exposed by the isolated Electron preload.
(() => {
 const $=id=>document.getElementById(id);
 const state={snapshot:null,selected:null,busy:false};
 const btnIds=['push','fetch','pull','branch-create','branch-switch','merge','remotes','github','commit-only','commit-push','copy-commit','revert','copy-sha'];
 function status(message,kind='info'){$('status').textContent=message;document.querySelector('.dot').style.background=kind==='error'?'#E5484D':'#B0375C';}
 function busy(isBusy){state.busy=isBusy;$('busy-indicator').hidden=!isBusy;for(const id of [...btnIds,'open-repo','init-repo','refresh'])$(id).disabled=isBusy||(btnIds.includes(id)&&!state.snapshot);$('commit-message').disabled=isBusy;updateSelectionButtons()}
 function updateSelectionButtons(){const enabled=Boolean(state.snapshot&&state.selected&&!state.busy);for(const id of ['copy-commit','revert','copy-sha'])$(id).disabled=!enabled}
 function text(tag,value,cls){const n=document.createElement(tag);n.textContent=String(value);if(cls)n.className=cls;return n}
 function render(snapshot){state.snapshot=snapshot;state.selected=null;const has=!!snapshot;
  $('repo-path').textContent=has?snapshot.repository:'아직 저장소가 없어요';$('repo-path').title=has?snapshot.repository:'Git 폴더 열기';
  $('branch-name').textContent=has?snapshot.branch:'저장소를 열어 볼까요?';
  $('file-count').textContent=String(snapshot?.files?.length||0);
  const tbody=$('file-list');tbody.replaceChildren();
  if(!has||!snapshot.files.length){const tr=document.createElement('tr');const td=text('td',has?'깨끗해요! 변경된 파일이 없습니다. 🌷':'저장소를 열면 파일이 보여요.','empty');td.colSpan=2;tr.append(td);tbody.append(tr)}
  else for(const f of snapshot.files){const tr=document.createElement('tr');const t1=document.createElement('td'),t2=document.createElement('td');t1.append(text('span',f.state,'state-chip'));t2.textContent=f.from?`${f.path} (이전: ${f.from})`:f.path;tr.append(t1,t2);tbody.append(tr)}
  const history=$('history-list');history.replaceChildren();
  if(!has||!snapshot.history.length)history.append(text('li',has?'아직 커밋이 없어요. 첫 기록을 남겨봐요!':'기록을 보려면 저장소를 열어 주세요.','empty'));
  else for(const h of snapshot.history){const li=document.createElement('li'),button=document.createElement('button');button.type='button';button.className='history-button';button.setAttribute('aria-pressed','false');button.dataset.testid='commit-'+h.sha.slice(0,7);button.title=`${h.sha} / ${h.author}`;
   button.append(text('span',h.sha.slice(0,7),'history-sha'));const right=document.createElement('span');right.className='history-desc';right.append(text('strong',h.message));right.append(text('small',`${h.author} · ${h.date}`));button.append(right);
   button.addEventListener('click',()=>{for(const b of history.querySelectorAll('button'))b.setAttribute('aria-pressed','false');button.setAttribute('aria-pressed','true');state.selected=h.sha;$('selected-sha').textContent=`선택 ${h.sha.slice(0,10)}`;updateSelectionButtons()});li.append(button);history.append(li);
  }
  $('selected-sha').textContent='커밋을 선택해 주세요.';
  for(const id of btnIds)$(id).disabled=!has||state.busy;
  updateSelectionButtons();
 }
 async function load(){if(state.busy)return;try{const r=await window.raidian.snapshot();if(!r.ok)throw Error(r.error);render(r.data);if(r.data)status(`✓ ${r.data.branch} · 파일 ${r.data.files.length}개 · 준비 완료`);}catch(e){status(e.message,'error')}}
 async function choose(init=false){if(state.busy)return;busy(true);try{const r=await window.raidian.chooseFolder({init});if(!r.ok)throw Error(r.error);if(r.data){render(r.data);status(`🍒 ${init?'새 저장소를 만들었어요':'저장소를 열었어요'}: ${r.data.branch}`)}}catch(e){status(e.message,'error')}finally{busy(false)}}
 async function run(action,args={},announcement='작업을 완료했어요.'){
  if(state.busy)return null;busy(true);status('Git 작업을 진행 중입니다…');
  try{const r=await window.raidian.action(action,args);if(!r.ok)throw Error(r.error);if(r.snapshot)render(r.snapshot);status(`✓ ${announcement}`);return r.data}
  catch(e){status(`⚠ ${e.message}`,'error');return null}finally{busy(false)}
 }
 function ask({title,description='',fields=[],button='진행',danger=false}){
  return new Promise(resolve=>{
   const dialog=$('action-dialog'),form=$('dialog-form'),container=$('dialog-fields');
   $('dialog-title').textContent=title;$('dialog-description').textContent=description;container.replaceChildren();
   $('dialog-submit').textContent=button;$('dialog-submit').className=`btn ${danger?'btn-blush':'btn-primary'}`;
   for(const item of fields){const label=document.createElement('label');label.textContent=item.label;let control;
    if(item.options){control=document.createElement('select');for(const opt of item.options){const option=document.createElement('option');option.value=typeof opt==='string'?opt:opt.value;option.textContent=typeof opt==='string'?opt:opt.label;control.append(option)}}
    else{control=document.createElement('input');control.type='text';control.placeholder=item.placeholder||'';control.maxLength=item.maxLength||400;control.value=item.default||'';}
    control.name=item.name;control.required=Boolean(item.required);if(item.value)control.value=item.value;
    control.dataset.testid=`dialog-${item.name}`;label.append(control);container.append(label)
   }
   let done=false;const finish=value=>{if(done)return;done=true;cleanup();if(dialog.open)dialog.close();resolve(value)};
   const submit=e=>{e.preventDefault();const values=Object.fromEntries(new FormData(form).entries());finish(values)};
   const cancelled=()=>finish(null);
   const cleanup=()=>{form.removeEventListener('submit',submit);$('dialog-cancel').removeEventListener('click',cancelled);$('dialog-close').removeEventListener('click',cancelled);dialog.removeEventListener('cancel',cancelled)};
   form.addEventListener('submit',submit);$('dialog-cancel').addEventListener('click',cancelled);$('dialog-close').addEventListener('click',cancelled);dialog.addEventListener('cancel',cancelled);
   dialog.showModal();container.querySelector('input,select')?.focus();
  });
 }
 function remotes(){return [...new Set((state.snapshot?.remotes||[]).map(r=>r.name))]}
 function branches(){return state.snapshot?.branches||[]}
 async function remoteChoice(label){const names=remotes();if(!names.length){status('원격 저장소가 없습니다. [원격 관리]에서 주소를 추가하세요.','error');return null}if(names.length===1)return names[0];const v=await ask({title:label,description:'원격 주소를 선택해 주세요.',fields:[{name:'remote',label:'원격',options:names}],button:'선택'});return v?.remote||null}
 async function commit(push=false){if(!state.snapshot){status('먼저 Git 폴더를 열어 주세요.','error');return}const msg=$('commit-message').value;const output=await run('commit',{message:msg},msg.trim()?'커밋을 기록했어요.':'자동 커밋 메시지로 기록했어요.');if(output===null)return;$('commit-message').value='';if(push){const remote=await remoteChoice('커밋을 어디로 푸시할까요?');if(remote)await run('push',{remote},`${remote}에 푸시했어요.`)}}
 function confirmQuestion(title,description,field='확인'){return ask({title,description,fields:[],button:field,danger:true})}
 function bind(id,handler){$(id).addEventListener('click',()=>{Promise.resolve(handler()).catch(e=>status(e.message,'error'))})}
 bind('open-repo',()=>choose());bind('init-repo',()=>choose(true));bind('refresh',load);
 bind('push',async()=>{const remote=await remoteChoice('푸시할 원격을 선택해 주세요');if(remote)await run('push',{remote},'원격에 푸시했어요.')});
 bind('fetch',async()=>{await run('fetch',{remote:'--all'},'원격 변경 내역을 가져왔어요.')});
 bind('pull',async()=>{const remote=await remoteChoice('풀할 원격을 선택해 주세요');if(remote){const v=await confirmQuestion('원격 변경을 병합할까요?','작업 트리가 깨끗해야 하며, no-ff 방식으로 병합해요.','풀 진행');if(v)await run('pull',{remote},'원격의 변경 사항을 병합했어요.')}});
 bind('branch-create',async()=>{const v=await ask({title:'하위 작업 브랜치 🌱',description:'브랜치 이름은 계층처럼 보여도 실제 부모 관계는 시작점으로 결정돼요.',fields:[{name:'group',label:'분류',placeholder:'feature',default:'feature',required:true},{name:'detail',label:'작업 이름',placeholder:'my-task',required:true},{name:'base',label:'시작 브랜치',options:[{value:'',label:'현재 HEAD'},...branches()]}],button:'브랜치 만들기'});if(v)await run('branch-child',v,'브랜치를 만들고 전환했어요.')});
 bind('branch-switch',async()=>{const choices=branches().filter(b=>b!==state.snapshot.branch);if(!choices.length){status('전환할 다른 브랜치가 없어요.');return}const v=await ask({title:'어느 브랜치로 갈까요?',description:'미커밋 변경이 있다면 안전을 위해 전환하지 않습니다.',fields:[{name:'name',label:'브랜치',options:choices}],button:'전환'});if(v)await run('switch',v,'브랜치를 전환했어요.')});
 bind('merge',async()=>{const choices=branches().filter(b=>b!==state.snapshot.branch);if(!choices.length){status('병합할 다른 브랜치가 없어요.');return}const v=await ask({title:'no-ff 병합 🌳',description:'현재 브랜치에 지정한 브랜치의 내용을 병합해요. 작업 이력은 별도 병합 커밋으로 남깁니다.',fields:[{name:'source',label:'병합할 브랜치',options:choices}],button:'병합하기',danger:true});if(v)await run('merge',{...v,confirm:true},'no-ff 병합했어요.')});
 bind('remotes',async()=>{const names=remotes();const v=await ask({title:'원격 관리 🌏',description:'origin 외에도 여러 개의 원격 저장소를 사용할 수 있어요.',fields:[{name:'action',label:'작업',options:[{value:'add',label:'새 원격 추가'},{value:'remove',label:'원격 제거'}]},{name:'name',label:'원격 이름 (제거할 때 기존 이름을 입력)',placeholder:names.join(', ')||'backup',required:true},{name:'url',label:'원격 URL (추가할 때 필수)',placeholder:'https://github.com/owner/repo.git'}],button:'적용'});if(!v)return;if(v.action==='add')await run('remote-add',{name:v.name,url:v.url},'원격 주소를 추가했어요.');else{const conf=await confirmQuestion('원격을 제거할까요?',`${v.name} 연결 정보를 삭제합니다. 원격 저장소 파일은 삭제하지 않아요.`,'원격 제거');if(conf)await run('remote-remove',{name:v.name,confirm:true},'원격 연결 정보를 제거했어요.')}});
 bind('github',async()=>{const v=await ask({title:'GitHub와 협동하기 ♡',description:'GitHub CLI(gh) 설치와 로그인이 필요해요. PR 목록을 조회하거나 현재 브랜치로 PR을 생성합니다.',fields:[{name:'action',label:'기능',options:[{value:'list',label:'열린 PR 목록 확인'},{value:'create',label:'현재 브랜치로 PR 생성'}]},{name:'base',label:'PR 기준 브랜치',default:'main'}],button:'실행'});if(!v)return;if(v.action==='create'){const confirm=await confirmQuestion('GitHub PR을 생성할까요?',`기준 브랜치: ${v.base}. gh pr create --fill을 실행합니다.`,'PR 만들기');if(confirm)await run('gh-pr-create',{base:v.base,confirm:true},'GitHub PR을 생성했어요.');return}const prs=await run('gh-prs',{},'PR 목록을 불러왔어요.');if(prs===null)return;if(!prs.length){status('열려 있는 PR이 없어요.');return}const choice=await ask({title:`열린 PR ${prs.length}개`,description:'열어볼 PR을 선택하세요.',fields:[{name:'url',label:'Pull Request',options:prs.map(p=>({value:p.url,label:`#${p.number} ${p.title}`}))}],button:'GitHub에서 열기'});if(choice){const opened=await window.raidian.openLink(choice.url);if(!opened)status('안전한 GitHub 링크만 열 수 있어요.','error')}});
 bind('copy-commit',async()=>{if(!state.selected)return;const sha=state.selected;const conf=await confirmQuestion('이 커밋을 복사할까요?',`${sha.slice(0,12)}의 변경 사항을 현재 브랜치에 새 커밋으로 적용해요. 원본 커밋은 그대로예요.`,'cherry-pick');if(conf)await run('copy-commit',{sha,confirm:true},'과거 커밋의 변경을 복사했어요.')});
 bind('revert',async()=>{if(!state.selected)return;const sha=state.selected;const conf=await confirmQuestion('이 커밋을 되돌릴까요?',`${sha.slice(0,12)}의 변경을 되돌리는 새 커밋을 작성합니다. 공유 기록은 삭제하지 않아요.`,'revert');if(conf)await run('revert',{sha,confirm:true},'특정 커밋의 변경만 되돌렸어요.')});
 bind('copy-sha',async()=>{if(state.selected){const copied=await window.raidian.copy(state.selected);status(copied?'커밋 SHA를 복사했어요.':'복사할 수 없어요.',copied?'info':'error')}});
 $('commit-form').addEventListener('submit',e=>{e.preventDefault();void commit(false)});bind('commit-push',()=>commit(true));
 document.addEventListener('keydown',e=>{
  if ($('action-dialog').open) return;
  const key=e.key.toLowerCase();if(e.key==='F5'){e.preventDefault();void load()}
  if((e.ctrlKey||e.metaKey)&&key==='o'){e.preventDefault();void choose()}
  if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();void commit(e.shiftKey)}
  if(e.altKey&&key==='b'){e.preventDefault();$('branch-create').click()}
  if(e.altKey&&key==='p'){e.preventDefault();$('push').click()}
 });
 window.raidian.onRepositoryChanged(load);
 void load();
})();
