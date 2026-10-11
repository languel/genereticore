import {app} from '../../../scripts/app.js';
const type='GeneretiCoreBrowserUpscale',value=(n,k)=>n.widgets?.find(w=>w.name===k)?.value;
function attach(node){
 if(node._coreBrowserUpscale||!window.generetiCompanion)return;node._coreBrowserUpscale=true;node.properties??={};
 const bridge=window.generetiCompanion;bridge.attachExecutionMode(node);const bar=node._generetiExecutionModeElement;
 let worker,release,running=false,ready=false,pending=false,dirty=false,dead=false,revision=0,id=0,timer,total=0,modelTotal=0,count=0,updated=0,started=0,current='';
 const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d',{willReadFrequently:true});
 const row=document.createElement('div');row.style.cssText='display:flex;align-items:center;gap:4px;font-size:12px;font-variant-numeric:tabular-nums';
 const dot=document.createElement('button');dot.textContent='●';dot.style.cssText='width:20px;border:0;background:transparent;padding:0';const text=document.createElement('span');text.textContent='Download · load · start';text.hidden=!!node.properties.genereticore_status_collapsed;row.append(dot,text);
 dot.onclick=()=>{text.hidden=!text.hidden;node.properties.genereticore_status_collapsed=text.hidden;dot.setAttribute('aria-expanded',String(!text.hidden));};
 const w=node.addDOMWidget('browser_status','GENERETICORE_BROWSER_STATUS',row,{serialize:false});w.computeSize=width=>[width,Math.max(26,row.scrollHeight)];
 function report(s,error=false){dot.title=dot.ariaLabel=s+' · click to show or hide timings';dot.style.color=error?'#ee7979':running?'#69c58a':'#999';if(error||!running||!count){text.textContent=s;if(error)text.hidden=false;}}
 function button(glyph,title,fn){const b=document.createElement('button');b.textContent=glyph;b.type='button';b.title=b.ariaLabel=title;b.onclick=fn;bar.append(b);return b;}
 function stop(){running=false;revision++;release?.();release=null;dirty=false;clearTimeout(timer);node._generetiTransportRefresh?.();report('Paused · last image held');}
 function unload(){stop();worker?.terminate();worker=null;ready=pending=false;current='';report('Unloaded · last image held');}
 function pump(){if(!running||!ready||pending||!dirty||dead)return;if(current!==value(node,'model')+':'+value(node,'backend')){unload();return;}dirty=false;pending=true;started=performance.now();const data=ctx.getImageData(0,0,canvas.width,canvas.height);worker.postMessage({type:'frame',id:++id,revision,rgba:data.data.buffer,width:canvas.width,height:canvas.height,scale:value(node,'scale')},[data.data.buffer]);}
 async function load(){
  unload();const model=value(node,'model'),backend=value(node,'backend');current=model+':'+backend;const loadRevision=revision;
  try{const status=await (await fetch('/genereticore/browser/status')).json();if(dead||revision!==loadRevision)return;if(!status.installed)throw Error('Download browser models and runtime with ↓ first.');
   worker=new Worker(new URL('./onnx-worker.mjs',import.meta.url),{type:'module'});
   worker.onerror=e=>{unload();report('Browser worker failed: '+e.message,true);};
   worker.onmessage=({data:m})=>{
    if(m.type==='ready'){ready=true;report(`Loaded ${backend} · cold ${Math.round(m.loadMs)} ms · press Start`);pump();}
    if(m.type==='error'){unload();report(m.message,true);}
    if(m.type==='result'){pending=false;try{if(running&&!dead&&m.revision===revision&&current===value(node,'model')+':'+value(node,'backend')){bridge.publishLive(node,m.bitmap);total+=performance.now()-started;modelTotal+=m.modelMs;count++;if(performance.now()-updated>1000){text.textContent=`${backend} · Total ${Math.round(total/count)} ms · ≈ ${(1000*count/total).toFixed(1)} FPS · Model ${Math.round(modelTotal/count)} ms`;updated=performance.now();total=modelTotal=count=0;}}}finally{m.bitmap.close();}timer=setTimeout(pump,0);}
   };report('Loading '+backend+' · compiling first inference…');worker.postMessage({type:'load',model,backend});
  }catch(e){unload();report(e.message,true);}
 }
 node._generetiTransportState=()=>({text:running?'Ⅱ':'▶',title:running?'Pause browser upscaling':'Start browser upscaling',disabled:node._generetiExecutionMode==='Comfy Queue'});
 node._generetiToggleTransport=()=>{
  if(running){stop();return;}if(!ready||current!==value(node,'model')+':'+value(node,'backend')){report('Load the selected model/backend with ↑ first.',true);return;}
  if(!bridge.subscribeLive){report('Update Genereti for shared live subscriptions.',true);return;}
  running=true;total=modelTotal=count=0;updated=performance.now();node._generetiTransportRefresh?.();
  const subscription=bridge.subscribeLive(node,({bitmap})=>{
   if(!bitmap||!running)return;if(Math.min(bitmap.width,bitmap.height)<2||Math.max(bitmap.width,bitmap.height)>256){stop();report('Resize input explicitly to 2–256px per side.',true);return;}
   if(canvas.width!==bitmap.width||canvas.height!==bitmap.height){revision++;canvas.width=bitmap.width;canvas.height=bitmap.height;}
   ctx.drawImage(bitmap,0,0);dirty=true;pump();
  },s=>{revision++;dirty=false;report(s);},{inputName:'image'});if(running)release=subscription;else subscription();
 };
 const download=button('↓','Download browser models and ONNX runtime',async()=>{unload();try{const r=await fetch('/genereticore/browser/download',{method:'POST'});if(!r.ok)throw Error((await r.json()).detail);report('Downloading browser artifacts…');}catch(e){report(e.message,true);}});
 button('↑','Load selected ONNX model and backend',()=>void load());button('×','Unload browser model · release worker and GPU memory',unload);
 const poll=setInterval(async()=>{try{const s=await (await fetch('/genereticore/browser/status')).json();download.disabled=s.installed||s.phase==='download';if(s.installed)download.innerHTML='<svg width="12" height="12" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8 L6 11 L13 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="square" stroke-linejoin="miter"/></svg>';else download.textContent='↓';download.title=download.ariaLabel=s.installed?'Browser ONNX models and runtime installed':`Download browser models and ONNX runtime · ${(s.total/1e6).toFixed(1)} MB`;if(s.phase==='download')report(`Download ${Math.round(100*s.done/s.total)}%`);if(s.phase==='error')report(s.detail,true);if(ready&&current!==value(node,'model')+':'+value(node,'backend'))unload();}catch{}},1500);
 node._generetiLiveSource={retain(){},release(){}};node._generetiSetExecutionMode=mode=>{if(mode==='Comfy Queue')stop();node._generetiTransportRefresh?.();};
 text.title='Total is worker round-trip including preprocessing and output; Model is inference only. FPS is an estimate, not display refresh. Browser resizing differs from native Lanczos.';
 const removed=node.onRemoved;node.onRemoved=function(){dead=true;unload();clearInterval(poll);window.removeEventListener('pagehide',unload);return removed?.apply(this,arguments);};window.addEventListener('pagehide',unload);node._generetiTransportRefresh?.();
}
app.registerExtension({name:'GeneretiCore.BrowserUpscale',setup(){window.addEventListener('genereti-companion-ready',()=>{for(const n of app.graph?._nodes??[])if(n.comfyClass===type)attach(n);});},nodeCreated(node){if(node.comfyClass===type)requestAnimationFrame(()=>attach(node));}});
