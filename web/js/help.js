import {app} from '../../../scripts/app.js';
const buttons=new Map();
let catalog;
const load=()=>catalog??=fetch(new URL('../node-references.json',import.meta.url)).then(r=>{if(!r.ok)throw Error('Core references unavailable');return r.json();}).catch(e=>{catalog=undefined;throw e;});
async function register(){if(window.generetiReference)window.generetiReference.registerDocuments(await load());}
function mount(){for(const [node,{button,row}]of buttons){const header=document.querySelector(`[data-node-id="${CSS.escape(String(node.id))}"] .lg-node-header`)?.firstElementChild;if(header&&button.parentElement!==header)header.append(button);else if(!header&&!row.contains(button))row.append(button);}}
let dialog;
async function open(node,button){
 try{
  await register();
  if(window.generetiReference){window.generetiReference.toggle(node,button);return;}
  if(dialog?.open&&dialog.dataset.node===String(node.id)){dialog.close();return;}
  if(!dialog){dialog=document.createElement('dialog');dialog.className='genereticore-help';const close=document.createElement('button');close.textContent='×';close.title=close.ariaLabel='Close reference';close.onclick=()=>dialog.close();dialog.append(close,document.createElement('article'));document.body.append(dialog);}
  const docs=await load(),body=dialog.querySelector('article');const text=docs[node.comfyClass]||docs.GeneretiCoreWelcome;
  const render=app.extensionManager?.renderMarkdownToHtml;
  if(render){body.style.whiteSpace='normal';body.innerHTML=render(text);}else{body.style.whiteSpace='pre-wrap';body.textContent=text;}
  dialog.dataset.node=String(node.id);if(!dialog.open)dialog.showModal();
 }catch(error){console.error('GeneretiCore Help:',error);}
}
app.registerExtension({name:'GeneretiCore.Help',setup(){
 const style=document.createElement('style');style.textContent='.genereticore-header-help{flex:none;margin-right:8px;width:20px;height:20px;padding:0;border:0;border-radius:6px;background:transparent;color:inherit;font-size:12px;display:inline-flex;align-items:center;justify-content:center;cursor:pointer}.genereticore-header-help:hover{background:color-mix(in srgb,currentColor 12%,transparent)}.genereticore-header-help:focus-visible{outline:2px solid currentColor;outline-offset:-2px}.genereticore-help{max-width:640px;max-height:80vh;overflow:auto;color:var(--input-text,currentColor);background:var(--comfy-input-bg,#222);border:0;border-radius:6px}.genereticore-help article{padding:16px;user-select:text}';document.head.append(style);
 let pending=false;new MutationObserver(()=>{if(!pending){pending=true;requestAnimationFrame(()=>{pending=false;mount();});}}).observe(document.body,{childList:true,subtree:true});
 window.addEventListener('genereti-reference-ready',()=>void register());void register();
},nodeCreated(node){
 if(!node.comfyClass?.startsWith('GeneretiCore')&&!['GeneretiSDXSGenerate','GeneretiSDTurboGenerate'].includes(node.comfyClass))return;
 const button=document.createElement('button');button.type='button';button.textContent='?';button.className='genereticore-header-help';button.title=button.ariaLabel=`Reference for ${node.title}`;button.onpointerdown=e=>e.stopPropagation();button.onclick=e=>{e.stopPropagation();void open(node,button);};
 const row=document.createElement('div');row.append(button);buttons.set(node,{button,row});
 const widget=node.addDOMWidget('genereticore_reference','GENERETICORE_REFERENCE',row,{serialize:false});widget.computeSize=width=>[width,row.childElementCount?20:0];widget.options.getMinHeight=()=>row.childElementCount?20:0;widget.options.getMaxHeight=widget.options.getMinHeight;
 const removed=node.onRemoved;node.onRemoved=function(){button.remove();buttons.delete(node);return removed?.apply(this,arguments);};requestAnimationFrame(mount);
}});
