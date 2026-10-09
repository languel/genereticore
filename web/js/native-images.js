import {app} from '../../../scripts/app.js';
const families={GeneretiSDXSGenerate:'sdxs',GeneretiSDTurboGenerate:'sd_turbo'};
const value=(node,name)=>node.widgets?.find(w=>w.name===name)?.value;
function source(node){
 const slot=node.inputs?.find(i=>i.name==='image'),link=node.graph?.links?.[slot?.link];
 const parent=node.graph?.getNodeById(link?.origin_id);
 if(!parent)throw Error('Connect a livecode or drawing image. Use Comfy Run for other IMAGE sources.');
 if(parent._generetiLivePaused||parent._generetiExecutionMode==='Comfy Queue')return null;
 return parent;
}
async function capture(node){
 if(value(node,'mode')==='text')return undefined;
 const parent=source(node);if(!parent)return null;
 if(parent._generetiLivecode?.captureDataUrl)return parent._generetiLivecode.captureDataUrl({live:true});
 if(parent._generetiDrawing?.captureDataUrl)return parent._generetiDrawing.captureDataUrl();
 if(parent._generetiTexture?.captureDataUrl)return parent._generetiTexture.captureDataUrl();
 throw Error('Live input requires a running livecode, drawing or texture source. Queue accepts any IMAGE.');
}
function attach(node){
 if(node._genereticoreImageUI||!window.generetiCompanion)return;
 node._genereticoreImageUI=true;
 const bridge=window.generetiCompanion;bridge.attachExecutionMode(node);
 const bar=node._generetiExecutionModeElement;let running=false,pending=false,disposed=false,timer,epoch=0,phase=0;
 let applied=node.properties.genereti_applied_prompt??value(node,'prompt'),live=node.properties.genereti_live_prompt??true;
 const status=document.createElement('span');status.setAttribute('role','status');status.setAttribute('aria-live','polite');status.style.cssText='flex-basis:100%;font-size:11px;white-space:normal';
 function button(glyph,title,fn){const b=document.createElement('button');b.type='button';b.textContent=glyph;b.title=b.ariaLabel=title;b.onclick=fn;bar.append(b);return b;}
 function state(){play.textContent=running?'Ⅱ':'▶';play.title=play.ariaLabel=running?'Pause image inference':'Start local image inference';play.setAttribute('aria-pressed',String(running));play.disabled=node._generetiExecutionMode==='Comfy Queue';promptToggle.setAttribute('aria-pressed',String(live));promptToggle.title=promptToggle.ariaLabel=live?'Apply prompt while typing':'Hold prompt draft until Send or Cmd/Ctrl+Enter';}
 function pause(){running=false;epoch++;clearTimeout(timer);state();status.textContent='Paused · last image held';}
 function commit(){applied=value(node,'prompt');node.properties.genereti_applied_prompt=applied;}
 const play=button('▶','Start local image inference',()=>{if(running)pause();else{running=true;epoch++;state();void tick();}});
 const promptToggle=button('ϟ','Apply prompt while typing',()=>{live=!live;node.properties.genereti_live_prompt=live;if(live)commit();state();});
 button('↑','Send held prompt · Cmd/Ctrl+Enter',commit);bar.append(status);bar.style.flexWrap='wrap';
 node._generetiLiveSource={retain(){},release(){}}; // Connecting/opening a viewer never starts inference.
 node._generetiSetExecutionMode=mode=>{if(mode==='Comfy Queue')pause();state();};
 node._generetiRestorePrompt=()=>{applied=node.properties.genereti_applied_prompt??value(node,'prompt');live=node.properties.genereti_live_prompt??true;state();};
 const editor=node.widgets?.find(w=>w.name==='prompt');
 if(editor){const serialize=editor.serializeValue;editor.serializeValue=async()=>live?(serialize?await serialize.call(editor):editor.value):applied;}
 function bindEditor(){const el=editor?.inputEl??editor?.element?.querySelector?.('textarea');if(el&&!el._genereticorePrompt){el._genereticorePrompt=true;el.addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey)){e.preventDefault();e.stopPropagation();editor.value=el.value;commit();}});}}
 async function tick(){
  if(!running||disposed)return;
  if(pending){timer=setTimeout(tick,100);return;}
  pending=true;const session=epoch,start=performance.now();let delay=42;
  try{
   const image=await capture(node);if(image===null){status.textContent='Source delivery paused';delay=250;return;}
   if(!running||session!==epoch)return;
   const payload={image,family:families[node.comfyClass],model_path:value(node,'model_path'),prompt:live?value(node,'prompt'):applied};
   for(const key of ['mode','seed','control_scale','invert','preprocess','strength']){const v=value(node,key);if(v!==undefined)payload[key]=v;}
   phase=(phase+Number(value(node,'movement')??0)*.035)%(2*Math.PI);payload.noise_phase=phase;
   status.textContent='Computing · last image held';
   const response=await fetch('/genereticore/coreml/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(60000)});
   if(response.status===429){status.textContent='Generator busy · waiting';delay=750;return;}
   if(!response.ok){let message=await response.text();try{message=JSON.parse(message).detail??message;}catch{}throw Error(message);}
   const bitmap=await createImageBitmap(await response.blob());
   try{if(running&&!disposed&&session===epoch){bridge.publishLive(node,bitmap);status.textContent=`${Math.round(performance.now()-start)} ms total · ${response.headers.get('X-Inference-Ms')} ms model`;}}finally{bitmap.close();}
  }catch(error){if(!disposed&&session===epoch){pause();status.textContent=error.message;status.title=error.message;}}
  finally{pending=false;if(running&&!disposed&&session===epoch)timer=setTimeout(tick,delay);}
 }
 let catalog;async function updateCatalog(){try{const r=await fetch('/genereticore/coreml/status');if(r.ok){catalog=await r.json();update();}}catch{}}
 function update(){bindEditor();const path=node.widgets?.find(w=>w.name==='model_path'),mode=node.widgets?.find(w=>w.name==='mode'),profile=catalog?.model_paths?.[path?.value];if(path&&catalog){path.options??={};path.options.values=Object.entries(catalog.model_paths).filter(([,p])=>p.family===families[node.comfyClass]).map(([p])=>p);if(!path.options.values.length)path.options.values=['not installed'];}if(mode&&profile){mode.options??={};mode.options.values=profile.modes;if(!profile.modes.includes(mode.value))mode.value=profile.modes[0];}}
 const recovery=setInterval(update,500);void updateCatalog();state();status.textContent='Paused · press Start, or use Queue and Comfy Run';
 const removed=node.onRemoved;node.onRemoved=function(){disposed=true;pause();clearInterval(recovery);window.removeEventListener('pagehide',pause);return removed?.apply(this,arguments);};window.addEventListener('pagehide',pause);
}
app.registerExtension({name:'GeneretiCore.NativeImages',setup(){window.addEventListener('genereti-companion-ready',()=>{for(const n of app.graph?._nodes??[])if(families[n.comfyClass])attach(n);});},nodeCreated(node){if(families[node.comfyClass]){requestAnimationFrame(()=>attach(node));}}});
