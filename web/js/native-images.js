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
 const footer=document.createElement('div');footer.className='genereticore-image-status';
 footer.style.cssText='font-size:12px;line-height:1.5;padding:2px 8px;box-sizing:border-box;color:inherit;width:100%';
 const toggle=document.createElement('button');toggle.type='button';toggle.title=toggle.ariaLabel='Show or hide image status and timings';toggle.style.cssText='border:0;background:transparent;color:inherit;padding:0;cursor:pointer;font:inherit';
 const details=document.createElement('div');
 const status=document.createElement('div');status.setAttribute('role','status');status.setAttribute('aria-live','polite');status.style.cssText='overflow-wrap:anywhere';
 const timing=document.createElement('div');timing.style.cssText='font-variant-numeric:tabular-nums;white-space:normal';timing.textContent='Total — ms · Model — ms';
 details.append(status,timing);footer.append(toggle,details);
 const statusWidget=node.addDOMWidget('genereticore_image_status','GENERETICORE_IMAGE_STATUS',footer,{serialize:false,hideOnZoom:false});
 const height=()=>details.hidden?26:Math.max(68,footer.scrollHeight);
 statusWidget.computeSize=width=>[width,height()];statusWidget.options.getMinHeight=height;statusWidget.options.getMaxHeight=height;
 function expand(expanded){details.hidden=!expanded;toggle.textContent=expanded?'⌄ Status':'› Status';toggle.setAttribute('aria-expanded',String(expanded));node.properties.genereticore_status_collapsed=!expanded;node.setDirtyCanvas?.(true,true);}
 expand(!node.properties.genereticore_status_collapsed);
 toggle.onclick=()=>{expand(details.hidden);node.setSize?.([node.size[0],node.computeSize()[1]]);};
 function report(text,error=false){if(status.textContent!==text)status.textContent=text;status.title=text;if(error){expand(true);node.setSize?.([node.size[0],node.computeSize()[1]]);}}
 let lastLiveStatus=0;
 function reportLive(text){const now=performance.now();if(now-lastLiveStatus<1000)return;lastLiveStatus=now;report(text);}
 let lastTiming=0,totalSum=0,modelSum=0,samples=0,modelSamples=0,hasImage=false;
 function measure(total,model){totalSum+=total;samples++;if(model!==null&&Number.isFinite(Number(model))){modelSum+=Number(model);modelSamples++;}const now=performance.now();if(now-lastTiming<1000)return;timing.textContent=`Total ${Math.round(totalSum/samples)} ms · Model ${modelSamples?Math.round(modelSum/modelSamples):'—'} ms`;lastTiming=now;totalSum=modelSum=samples=modelSamples=0;}

 function button(glyph,title,fn){const b=document.createElement('button');b.type='button';b.textContent=glyph;b.title=b.ariaLabel=title;b.onclick=fn;bar.append(b);return b;}
 function state(){play.textContent=running?'Ⅱ':'▶';play.title=play.ariaLabel=running?'Pause image inference':'Start local image inference';play.setAttribute('aria-pressed',String(running));play.disabled=node._generetiExecutionMode==='Comfy Queue';promptToggle.setAttribute('aria-pressed',String(live));promptToggle.title=promptToggle.ariaLabel=live?'Apply prompt while typing':'Hold prompt draft until Send or Cmd/Ctrl+Enter';}
 function pause(){running=false;epoch++;clearTimeout(timer);state();report('Paused · last image held');}
 function commit(){applied=value(node,'prompt');node.properties.genereti_applied_prompt=applied;}
 const play=button('▶','Start local image inference',()=>{if(running)pause();else{running=true;epoch++;hasImage=false;totalSum=modelSum=samples=modelSamples=0;lastTiming=lastLiveStatus=performance.now();state();report('Computing first image…');void tick();}});
 const promptToggle=button('ϟ','Apply prompt while typing',()=>{live=!live;node.properties.genereti_live_prompt=live;if(live)commit();state();});
 button('↑','Send held prompt · Cmd/Ctrl+Enter',commit);
 const download=button('↓','Download image model',async()=>{
  const entry=catalog?.bundles?.find(b=>b.family===(families[node.comfyClass]==='sd_turbo'?'sd-turbo':'sdxs'));
  if(!entry)return;
  if(running)pause();
  try{
   const response=await fetch('/genereticore/coreml/download',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({family:entry.family})});
   const data=await response.json();if(!response.ok)throw Error(data.detail??'Download could not start.');
   downloadPending=true;await updateCatalog();
  }catch(error){report(error.message,true);}
 });
 const terms=document.createElement('a');terms.textContent='ⓘ';terms.target='_blank';terms.rel='noopener';terms.title=terms.ariaLabel='Model credits, source links and license terms';bar.append(terms);
 bar.style.flexWrap='wrap';
 const delivery=node.widgets?.find(w=>w.name==='genereti_delivery');if(delivery)delivery.computeSize=width=>[width,Math.max(32,bar.scrollHeight)];
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
   const image=await capture(node);if(image===null){reportLive('Source delivery paused');delay=250;return;}
   if(!running||session!==epoch)return;
   const payload={image,family:families[node.comfyClass],model_path:value(node,'model_path'),prompt:live?value(node,'prompt'):applied};
   for(const key of ['mode','seed','control_scale','invert','preprocess','strength']){const v=value(node,key);if(v!==undefined)payload[key]=v;}
   phase=(phase+Number(value(node,'movement')??0)*.035)%(2*Math.PI);payload.noise_phase=phase;
   if(hasImage)reportLive('Running · last image held while computing');
   const response=await fetch('/genereticore/coreml/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(60000)});
   if(response.status===429){reportLive('Generator busy · waiting');delay=750;return;}
   if(!response.ok){let message=await response.text();try{message=JSON.parse(message).detail??message;}catch{}throw Error(message);}
   const bitmap=await createImageBitmap(await response.blob());
   try{if(running&&!disposed&&session===epoch){bridge.publishLive(node,bitmap);hasImage=true;reportLive('Running · last image held while computing');measure(performance.now()-start,response.headers.get('X-Inference-Ms'));}}finally{bitmap.close();}
  }catch(error){if(!disposed&&session===epoch){pause();report(error.message,true);}}
  finally{pending=false;if(running&&!disposed&&session===epoch)timer=setTimeout(tick,delay);}
 }
 let catalog,downloadPending=false,lastCatalogCheck=0;
 async function updateCatalog(){try{const r=await fetch('/genereticore/coreml/status');if(r.ok){catalog=await r.json();update();}}catch{}}
 function update(){bindEditor();const path=node.widgets?.find(w=>w.name==='model_path'),mode=node.widgets?.find(w=>w.name==='mode'),profile=catalog?.model_paths?.[path?.value];if(path&&catalog){path.options??={};path.options.values=Object.entries(catalog.model_paths).filter(([,p])=>p.family===families[node.comfyClass]).map(([p])=>p);if(!path.options.values.length)path.options.values=['not installed'];}if(mode&&profile){mode.options??={};mode.options.values=profile.modes;if(!profile.modes.includes(mode.value))mode.value=profile.modes[0];}}
 const updateWidgets=update;
 update=function(){
  updateWidgets();
  const entry=catalog?.bundles?.find(b=>b.family===(families[node.comfyClass]==='sd_turbo'?'sd-turbo':'sdxs'));
  if(!entry){download.hidden=true;terms.hidden=true;return;}
  download.hidden=false;terms.hidden=false;terms.href=`https://huggingface.co/${entry.repo}/blob/${entry.revision}/Notice.txt`;
  const busy=['download','verify','install'].includes(entry.phase);
  const anyBusy=catalog.bundles.some(b=>['download','verify','install'].includes(b.phase));
  download.disabled=anyBusy||entry.installed;download.textContent=entry.installed?'✓':'↓';
  const label=entry.family==='sdxs'?'SDXS':'SD Turbo';
  download.title=download.ariaLabel=entry.installed?`${label} bundle installed`:`Download ${label} · ${(entry.download_bytes/1e9).toFixed(2)} GB · local model`;
  if(busy){downloadPending=true;report(`${entry.phase==='verify'?'Verifying':entry.phase==='install'?'Installing':'Downloading'} ${label} · ${Math.round(100*entry.done/entry.total)}%`);}
  else if(downloadPending){downloadPending=false;report(entry.phase==='error'?entry.detail:`${label} installed · choose 512px and press Start`,entry.phase==='error');}
  if(entry.installed){const widget=node.widgets?.find(w=>w.name==='model_path');if(widget&&(!catalog.model_paths?.[widget.value]||widget.value==='not installed')){widget.value=entry.family==='sdxs'?'512/unet.mlpackage':'512/turbo_unet.mlpackage';updateWidgets();}}
 };
 const recovery=setInterval(()=>{update();if(Date.now()-lastCatalogCheck>2000){lastCatalogCheck=Date.now();void updateCatalog();}},500);void updateCatalog();state();report('Paused · press Start, or use Queue and Comfy Run');
 const removed=node.onRemoved;node.onRemoved=function(){disposed=true;pause();clearInterval(recovery);window.removeEventListener('pagehide',pause);return removed?.apply(this,arguments);};window.addEventListener('pagehide',pause);
}
app.registerExtension({name:'GeneretiCore.NativeImages',setup(){window.addEventListener('genereti-companion-ready',()=>{for(const n of app.graph?._nodes??[])if(families[n.comfyClass])attach(n);});},nodeCreated(node){if(families[node.comfyClass]){requestAnimationFrame(()=>attach(node));}}});
