'use strict';
const path = require('node:path');
const { app, BrowserWindow, ipcMain, dialog, shell, clipboard } = require('electron');
const { Repository } = require('../core/git.cjs');
const { dispatch, MUTATIONS } = require('../core/commands.cjs');
const pkg = require('../../package.json');

// A single runtime powers GUI, CLI and MCP. The GUI never receives Node privileges.
const mode = process.argv.includes('--cli') ? 'cli' : process.argv.includes('--mcp') ? 'mcp' : 'gui';
if (mode !== 'gui') {
  const index = process.argv.indexOf(mode === 'cli' ? '--cli' : '--mcp');
  const argv = process.argv.slice(index + 1);
  const runner = mode === 'cli' ? require('../core/cli.cjs').main : require('../mcp/server.cjs').main;
  runner(argv).then(n => process.exit(n)).catch(error => {console.error(error.message);process.exit(1)});
} else {
  let mainWindow, repository = null, busy = false;
  const gotLock=app.requestSingleInstanceLock();
  if (!gotLock) app.quit();
  else {
    app.on('second-instance', () => { if (mainWindow) { if (mainWindow.isMinimized()) mainWindow.restore(); mainWindow.focus(); } });
    app.whenReady().then(async () => {
      app.setAppUserModelId('io.github.hslcrb.raidian');
      mainWindow = new BrowserWindow({
        width: 1180, height: 790, minWidth: 660, minHeight: 560,
        backgroundColor: '#F9F6F7', title: `Raidian ${pkg.version}`,
        autoHideMenuBar: true,
        webPreferences: {
          preload: path.join(__dirname,'preload.cjs'),
          contextIsolation: true, nodeIntegration: false,
          sandbox: true, webSecurity: true, devTools: process.argv.includes('--dev')
        }
      });
      mainWindow.webContents.setWindowOpenHandler(() => ({action:'deny'}));
      mainWindow.webContents.on('will-navigate',(event,url)=>{if(!url.startsWith('file://'))event.preventDefault()});
      await mainWindow.loadFile(path.join(__dirname,'../renderer/index.html'));
      const initial=process.argv.indexOf('--repo');
      if(initial>=0&&process.argv[initial+1]){
        try{repository=await Repository.open(process.argv[initial+1]); mainWindow.webContents.send('raidian:repository-changed');}catch{/* Show friendly empty state. */}
      } else {
        try{repository=await Repository.open(process.cwd());mainWindow.webContents.send('raidian:repository-changed');}catch{/* no repository selected */}
      }
    });
    app.on('activate',()=>{if(BrowserWindow.getAllWindows().length===0)app.quit()});
    app.on('window-all-closed',()=>app.quit());
  }
  ipcMain.handle('raidian:snapshot',async()=>({ok:true,data:repository?await repository.snapshot():null}));
  ipcMain.handle('raidian:folder',async(event,init=false)=>{
    if(busy)return {ok:false,error:'작업이 진행 중입니다. 완료 후 폴더를 바꾸세요.'};
    if(typeof init!=='boolean')return {ok:false,error:'잘못된 요청입니다.'};
    const result=await dialog.showOpenDialog(mainWindow,{properties:['openDirectory','createDirectory']});
    if(result.canceled||!result.filePaths.length)return {ok:true,data:null};
    try{
      repository=init?await Repository.init(result.filePaths[0]):await Repository.open(result.filePaths[0]);
      return {ok:true,data:await repository.snapshot()};
    }catch(e){return {ok:false,error:e.message}}
  });
  ipcMain.handle('raidian:action',async(event,action,args={})=>{
    if(busy)return {ok:false,error:'이전 작업이 끝날 때까지 기다려 주세요.'};
    if(typeof action!=='string'||!args||typeof args!=='object'||Array.isArray(args))return {ok:false,error:'요청 형식 오류'};
    if(!repository)return {ok:false,error:'Git 폴더를 먼저 선택해 주세요.'};
    const pinned=repository;
    busy=true;
    try{
      const data=await dispatch(action,args,{repository:pinned,requireConfirmation:true});
      const snapshot=MUTATIONS.has(action)?await pinned.snapshot():null;
      return {ok:true,data,snapshot};
    }catch(e){return {ok:false,error:e.message}}
    finally{busy=false}
  });
  ipcMain.handle('raidian:open-url',async(_event,url)=>{
    if(typeof url!=='string'||url.length>1000||!/^https:\/\/github\.com\/[A-Za-z0-9-]+\/[A-Za-z0-9_.-]+\/(pull|issues)\/\d+(?:[/?#].*)?$/.test(url))return false;
    await shell.openExternal(url);return true;
  });
  ipcMain.handle('raidian:copy',async(_event,value)=>{
    if(typeof value!=='string'||value.length>2048)return false;
    clipboard.writeText(value);return true;
  });
}
