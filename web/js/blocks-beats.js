import {GeneretiCoreClient,ResultPair} from './client.js';
import {resultViewer} from './result-viewer.js';
import {W,H,SHAPES,emptyBoard,features,candidates,moveState,seededBag,PATTERNS,musicState,baselineMusic} from './blocks-engine.mjs';
const $=id=>document.getElementById(id),client=new GeneretiCoreClient(),stream='arcade-'+crypto.randomUUID();
const moveView=resultViewer({properties:{}}),musicView=resultViewer({properties:{}});$('move-result').append(moveView.element);$('music-result').append(musicView.element);
let board=emptyBoard(),nextPiece=seededBag(),pieces=0,lines=0,epoch=0,revision=0,running=false,requestId=null,falling=null,pendingPiece=null,options=[],lastMove=null;
const music=new ResultPair();music.accept('calm',0);let audio=null,audioOn=false,step=0,nextTick=0,voices=new Set(),lastMetrics=null,frameAt=0;
const colors=['#81a9ff','#8fdac4','#d5a6ff','#f2c96d','#fa9c86','#84c9ed','#ddec91'];
function status(text){$('status').textContent=text;}
function stats(){ $('pieces').textContent=pieces;$('lines').textContent=lines;$('height').textContent=features(board).height; }
function patterns(){const pattern=PATTERNS[music.current];document.documentElement.style.setProperty('--accent',pattern.color);$('music-current').textContent=music.current;$('music-next').textContent=music.next??'—';$('pattern').replaceChildren(...Array.from({length:16},(_,i)=>{const el=document.createElement('span');if(pattern.beats.includes(i))el.classList.add('note');if(audioOn&&i===step)el.classList.add('playing');return el;}));}
async function decide(prompt,question,choices,myEpoch,kind){
  if($('player').value==='baseline')return null;
  const submitted=await client.submit({task:'decision.evaluate',model:'d1-omni-600m',inputs:{prompt,question,choices},options:{max_tokens:1},stream_id:stream,input_revision:++revision,policy:'latest'});
  if(myEpoch!==epoch){await client.cancel(submitted.request_id);throw Error('Canceled');}
  requestId=submitted.request_id;let answer=null,error=null;
  await client.follow(requestId,event=>{if(myEpoch!==epoch)return;if(event.type==='completed'){answer=event.payload.content;lastMetrics=event.payload.timings;}if(event.type==='failed')error=event.payload.message;});
  requestId=null;if(myEpoch!==epoch)throw Error('Canceled');if(error||!answer)throw Error(error??'Decision did not complete');
  if(!choices.includes(answer.choice))throw Error('Decision returned an unknown label');
  (kind==='move'?moveView:musicView).show(JSON.stringify({source:'d1 · Core ML',...answer,metrics:lastMetrics}));return answer;
}
function showOptions(choice){$('options').replaceChildren(...options.map(c=>{const el=document.createElement('div');el.className='candidate'+(c.label===choice?' selected':'');const heading=document.createElement('b');heading.textContent=c.label+' · '+(c.r*90)+'° / column '+(c.x+1);const detail=document.createElement('small');detail.textContent=`${c.lines} rows · ${c.holes} holes · height ${c.height}`;el.append(heading,detail);return el;}));}
async function turn(myEpoch){
  const piece=pendingPiece??=nextPiece();options=candidates(board,piece);if(!options.length){pause();status('Top out · Reset to play the same seed again.');return;}
  const prompt=moveState(board,piece,options);$('state').textContent=prompt;showOptions(null);status('Choosing a legal '+piece+' placement…');
  const decision=await decide(prompt,'Choose the best drop: maximize cleared rows; minimize holes, total column height and unevenness. Choose A, B, C or D.',options.map(c=>c.label),myEpoch,'move');
  if(myEpoch!==epoch)return;const choice=decision?.choice??options[0].label,selected=options.find(c=>c.label===choice);showOptions(choice);
  if(!decision)moveView.show(JSON.stringify({source:'authored heuristic · no AI',choice,utility:selected.utility,features:{lines:selected.lines,holes:selected.holes,height:selected.height}}));
  const start=performance.now(),duration=Number($('pace').value);falling={...selected,piece,start,duration};
  await new Promise(resolve=>setTimeout(resolve,duration));if(myEpoch!==epoch)return;
  board=selected.board.map(row=>row.map(v=>v? v:0)); // placement occupancy is authoritative
  // Keep a color per landed tetromino without changing collision semantics.
  selected.shape.forEach((row,dy)=>row.forEach((v,dx)=>{if(v&&!selected.lines)board[selected.y+dy][selected.x+dx]=1+Object.keys(SHAPES).indexOf(piece);}));
  falling=null;pendingPiece=null;pieces++;lines+=selected.lines;lastMove={piece,choice,lines:selected.lines};stats();
  if(pieces===1||pieces%4===0||selected.lines){
    const text=musicState(board,selected.lines,pieces),reply=await decide(text,'Choose one authored soundtrack: calm for low stack, drive for steady play, tense for danger, celebrate when rows clear.',['calm','drive','tense','celebrate'],myEpoch,'music');
    if(myEpoch!==epoch)return;const chosen=reply?.choice??baselineMusic(board,selected.lines);
    if(!reply)musicView.show(JSON.stringify({source:'authored rule · no AI',state:text,choice:chosen}));
    music.accept(chosen,++revision,'bar');
    // With audio stopped there is no sounding bar to preserve; stage immediately for preview.
    if(!audioOn){music.trigger('bar');music.setPhase(1);}patterns();
  }
  status(($('player').value==='baseline'?'Heuristic':'d1')+` · ${piece} → ${choice} · ${pieces} pieces · ${lines} cleared rows`);
}
async function play(){if(running){pause();return;}if($('player').value==='d1'){try{const s=await client.status(),model=s.models.find(m=>m.id==='d1-omni-600m');if(!model?.available)throw Error(model?.unavailable_reason??'d1 is not available');if(!model.installed)throw Error('Download d1 explicitly before Start game.');}catch(e){status(e.message);return;}}
  running=true;const myEpoch=++epoch;$('play').textContent='Ⅱ Pause game';$('play').setAttribute('aria-pressed','true');$('player').disabled=true;
  try{while(running&&myEpoch===epoch)await turn(myEpoch);}catch(e){if(myEpoch===epoch){pause();status('Paused · '+e.message);}}
}
function pause(){running=false;epoch++;falling=null;$('play').textContent='▷ Start game';$('play').setAttribute('aria-pressed','false');$('player').disabled=false;if(requestId){client.cancel(requestId).catch(()=>{});requestId=null;}}
$('play').onclick=play;$('reset').onclick=()=>{pause();board=emptyBoard();nextPiece=seededBag();pendingPiece=null;pieces=lines=0;options=[];lastMove=null;stats();$('state').textContent='Reset to seed 7. Press Start game.';$('options').replaceChildren();moveView.show('Reset · no current decision');musicView.show('Reset · no current decision');music.current='calm';music.next=null;step=0;patterns();status('Reset · no inference until Start game');};
$('download').onclick=async()=>{if(running)return;try{$('download').disabled=true;status('Explicitly downloading pinned d1…');const r=await client.submit({task:'model.download',model:'d1-omni-600m',inputs:{},options:{},policy:'fifo',stream_id:stream+'-download',input_revision:++revision});let error=null;await client.follow(r.request_id,e=>{if(e.type==='download_progress')status('Downloading d1 · '+Math.round(e.payload.fraction*100)+'%');if(e.type==='failed')error=e.payload.message;});status(error??'d1 installed · press Start game');}catch(e){status(e.message);}finally{$('download').disabled=false;}};
function note(freq,time,length,type='triangle',gain=.055){const osc=audio.createOscillator(),amp=audio.createGain();osc.type=type;osc.frequency.value=freq;osc.connect(amp);amp.connect(audio.destination);amp.gain.setValueAtTime(0,time);amp.gain.linearRampToValueAtTime(gain,time+.008);amp.gain.exponentialRampToValueAtTime(.0001,time+length);osc.start(time);osc.stop(time+length+.02);voices.add(osc);osc.onended=()=>{voices.delete(osc);amp.disconnect();osc.disconnect();};}
function tick(){if(!audioOn)return;while(nextTick<audio.currentTime+.09){if(step===0){music.trigger('bar');music.setPhase(1);patterns();}const p=PATTERNS[music.current];if(p.beats.includes(step)){const index=p.beats.indexOf(step),midi=p.notes[index%p.notes.length];note(440*2**((midi-69)/12),nextTick,.18);}
 if(step%4===0)note(58,nextTick,.08,'sine',.10);if(step%4===2)note(140,nextTick,.035,'triangle',.025);
 $('music-clock').textContent=`${p.bpm} BPM · step ${step+1}/16`;
 Array.from($('pattern').children).forEach((el,i)=>el.classList.toggle('playing',i===step));step=(step+1)%16;nextTick+=60/p.bpm/4;}}
setInterval(tick,25);
$('audio').onclick=async()=>{if(audioOn){audioOn=false;await audio.suspend();$('audio').textContent='♫ Start audio';$('audio').setAttribute('aria-pressed','false');$('music-clock').textContent='audio off';}else{audio??=new AudioContext();await audio.resume();audioOn=true;step=0;nextTick=audio.currentTime+.05;$('audio').textContent='■ Stop audio';$('audio').setAttribute('aria-pressed','true');}patterns();};
const ctx=$('board').getContext('2d');function draw(time){const cell=32;ctx.fillStyle='#0f131b';ctx.fillRect(0,0,320,640);for(let y=0;y<H;y++)for(let x=0;x<W;x++){ctx.strokeStyle='#ffffff08';ctx.strokeRect(x*cell,y*cell,cell,cell);if(board[y][x])block(x,y,colors[(board[y][x]-1)%colors.length]);}if(falling){const progress=Math.min(1,(time-falling.start)/falling.duration);const y=falling.y*(1-(1-progress)**2);falling.shape.forEach((row,dy)=>row.forEach((v,dx)=>{if(v){ctx.globalAlpha=.20;block(falling.x+dx,falling.y+dy,'#fff');ctx.globalAlpha=1;block(falling.x+dx,y+dy,PATTERNS[music.current].color);}}));}frameAt=time;requestAnimationFrame(draw);}
function block(x,y,color){ctx.fillStyle=color;ctx.fillRect(x*32+2,y*32+2,28,28);ctx.fillStyle='#ffffff24';ctx.fillRect(x*32+4,y*32+4,24,4);}
window.addEventListener('pagehide',()=>{pause();audioOn=false;audio?.close();});stats();patterns();requestAnimationFrame(draw);
