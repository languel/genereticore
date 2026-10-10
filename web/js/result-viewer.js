/** Local read-only JSON navigation. Values always use textContent, never HTML. */
export function resultViewer(node) {
  const root=document.createElement('div'); root.className='genereticore-result';
  const bar=document.createElement('div'); bar.className='genereticore-controls';
  const mode=document.createElement('select'); mode.title='Result display: collapsible tree, pretty text, or minified JSON'; mode.setAttribute('aria-label','Result display mode');
  for(const [value,label] of [['tree','Tree'],['pretty','Pretty'],['minified','Minified']]) {const option=document.createElement('option');option.value=value;option.textContent=label;mode.append(option);}
  mode.value=node.properties.genereticoreResultMode ?? 'tree';
  if(CSS.supports('appearance','base-select')) {
    mode.classList.add('genereticore-glyph-choice');
    const trigger=document.createElement('button');trigger.type='button';
    trigger.append(document.createElement('selectedcontent'));mode.prepend(trigger);
    const paths={tree:'<path d="M6 4v16m0-12h8m-8 8h8"/><rect x="14" y="5" width="6" height="6" rx="1"/><rect x="14" y="13" width="6" height="6" rx="1"/>',
      pretty:'<path d="M4 5h16M8 10h12M8 15h9M4 20h16"/>',
      minified:'<path d="M3 12h18m-14-5 5 5-5 5m10-10-5 5 5 5"/>'};
    for(const option of mode.options){
      const label=option.textContent;option.dataset.label=label;
      const icon=document.createElement('span');icon.className='genereticore-choice-icon';
      icon.innerHTML=`<svg aria-hidden="true" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${paths[option.value]}</svg>`;
      const text=document.createElement('span');text.className='genereticore-choice-label';text.textContent=label;
      option.replaceChildren(icon,text);
    }
  }
  function choiceTip(){mode.title='Result display · '+(mode.selectedOptions[0]?.dataset.label??mode.selectedOptions[0]?.textContent)+' · Tree, Pretty or Minified';}
  choiceTip();
  let minimized=false,frozen=false,pending;
  const minimize=document.createElement('button'),freeze=document.createElement('button');
  for(const b of [minimize,freeze]){b.type='button';b.style.cssText='width:20px;height:20px;padding:0;border:0;border-radius:6px;background:transparent;color:inherit;font-size:12px;display:inline-flex;align-items:center;justify-content:center';}
  function state(){minimize.textContent=minimized?'›':'⌄';minimize.title=minimize.ariaLabel=minimized?'Restore local preview':'Minimize local preview · inference continues';minimize.setAttribute('aria-expanded',String(!minimized));freeze.textContent='❄';freeze.title=freeze.ariaLabel='Freeze local preview · inference continues';freeze.setAttribute('aria-pressed',String(frozen));body.hidden=minimized;}
  minimize.onclick=()=>{minimized=!minimized;state();};freeze.onclick=()=>{frozen=!frozen;state();if(!frozen&&pending!==undefined){const value=pending;pending=undefined;show(value);}};
  const body=document.createElement('div');body.className='genereticore-result-body';
  const text=document.createElement('textarea');text.readOnly=true;text.setAttribute('aria-label','Result text');text.placeholder='Run the workflow to see the result here.';
  let raw='',parsed,valid=false;const expanded=new Map();let count=0;
  const primitive=(value,key)=>{const line=document.createElement('div');line.className='genereticore-leaf';const name=document.createElement('span');name.className='genereticore-key';name.textContent=key==null?'':key+': ';const data=document.createElement('span');data.className='genereticore-'+(value===null?'null':typeof value);data.textContent=JSON.stringify(value);line.append(name,data);return line;};
  function branch(value,key,path,depth) {
    if(++count>5000) {const limit=document.createElement('div');limit.textContent='Tree limit reached; use Pretty or Minified to read the full result.';return limit;}
    if(!value||typeof value!=='object')return primitive(value,key);
    const entries=Object.entries(value);const details=document.createElement('details');
    const summary=document.createElement('summary');summary.textContent=(key==null?'':key+': ')+(Array.isArray(value)?`Array (${entries.length})`:`Object {${entries.length}}`);details.append(summary);
    let built=false;function build(){if(built)return;built=true;const children=document.createElement('div');children.className='genereticore-children';for(const [k,v] of entries){if(count>=5000){const notice=document.createElement("div");notice.textContent="Tree limit reached; use Pretty or Minified for the full result.";children.append(notice);break;}children.append(branch(v,k,path+'/'+JSON.stringify(k),depth+1));}details.append(children);}
    details.open=expanded.get(path)??depth<2;
    if(details.open)build();details.addEventListener('toggle',()=>{expanded.set(path,details.open);if(details.open)build();});return details;
  }
  function render(){body.replaceChildren();count=0;
    if(valid&&mode.value==='tree') {body.append(branch(parsed,null,'',0));body.setAttribute('aria-label','JSON tree');}
    else {text.value=valid?JSON.stringify(parsed,null,mode.value==='minified'?undefined:2):raw;body.append(text);body.removeAttribute('aria-label');}
  }
  mode.addEventListener('change',()=>{node.properties.genereticoreResultMode=mode.value;choiceTip();render();});
  bar.append(minimize,freeze,mode);root.append(bar,body);state();render();
  let view;const attach=()=>{if(!view&&window.generetiCompanion){window.generetiCompanion.ensureControlStyle();bar.classList.add("genereti-node-controls");view=window.generetiCompanion.visualNodeControls(node,body,bar);}};
  window.addEventListener("genereti-companion-ready",attach);queueMicrotask(attach);const removed=node.onRemoved;node.onRemoved=function(){window.removeEventListener("genereti-companion-ready",attach);return removed?.apply(this,arguments);};
  function show(value){if(frozen){pending=value;return;}raw=String(value);valid=false;try{parsed=JSON.parse(raw);valid=true;}catch{}render();}
  return {element:root,show};
}
