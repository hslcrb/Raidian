'use strict';
const { contextBridge, ipcRenderer }=require('electron');
// Small explicit bridge: no require(), arbitrary IPC channel or filesystem access in renderer.
contextBridge.exposeInMainWorld('raidian',Object.freeze({
  snapshot:()=>ipcRenderer.invoke('raidian:snapshot'),
  chooseFolder:({init=false}={})=>ipcRenderer.invoke('raidian:folder',Boolean(init)),
  action:(name,args={})=>ipcRenderer.invoke('raidian:action',name,args),
  openLink:url=>ipcRenderer.invoke('raidian:open-url',url),
  copy:text=>ipcRenderer.invoke('raidian:copy',text),
  onRepositoryChanged:(callback)=>{
    if(typeof callback!=='function')return ()=>{};
    const handler=()=>callback();ipcRenderer.on('raidian:repository-changed',handler);
    return ()=>ipcRenderer.removeListener('raidian:repository-changed',handler);
  }
}));
