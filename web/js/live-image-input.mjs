// Copy borrowed frames during subscribeLive's synchronous callback. Keep one
// owned canvas; encoding only happens when the native worker is ready.
export function createLiveImageInput(node,{subscribeLive,makeCanvas=()=>document.createElement('canvas')}={}){
 const canvas=makeCanvas(),context=canvas.getContext('2d');let release=null,ready=false;
 function accept({bitmap}){
  if(!bitmap)return;
  const scale=Math.min(1,512/Math.max(bitmap.width,bitmap.height));
  canvas.width=Math.max(1,Math.round(bitmap.width*scale));canvas.height=Math.max(1,Math.round(bitmap.height*scale));
  context.drawImage(bitmap,0,0,canvas.width,canvas.height);ready=true;
 }
 return {
  start(){
   if(release)return;
   if(!subscribeLive)throw Error('Update Genereti to a companion bridge with subscribeLive support, then reload Comfy.');
   release=subscribeLive(node,accept,()=>{ready=false;},{inputName:'image'});
  },
  stop(){release?.();release=null;ready=false;},
  capture(){return ready?canvas.toDataURL('image/png'):null;},
  dispose(){this.stop();canvas.width=canvas.height=0;}
 };
}
