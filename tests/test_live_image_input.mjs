import assert from 'node:assert/strict';
import {createLiveImageInput} from '../web/js/live-image-input.mjs';
let frame,status,subscriptions=0,releases=0,draws=0,encoded=0;
const canvas={width:0,height:0,getContext:()=>({drawImage(image){assert.equal(image.closed,false);draws++;}}),toDataURL(){encoded++;return `frame:${draws}`;}};
const node={id:3};
const input=createLiveImageInput(node,{makeCanvas:()=>canvas,subscribeLive(target,onFrame,onStatus,options){
 assert.equal(target,node);assert.equal(options.inputName,'image');frame=onFrame;status=onStatus;subscriptions++;return ()=>{releases++;};
}});
assert.equal(input.capture(),null);input.start();input.start();assert.equal(subscriptions,1);
const borrowed={width:1024,height:512,closed:false};frame({bitmap:borrowed});borrowed.closed=true;
assert.equal(encoded,0);assert.equal(canvas.width,512);assert.equal(canvas.height,256);assert.equal(input.capture(),'frame:1');
frame({bitmap:{width:128,height:96,closed:false}});assert.equal(input.capture(),'frame:2');assert.equal(canvas.height,96);
status('No browser live source');assert.equal(input.capture(),null);
input.stop();assert.equal(releases,1);assert.equal(input.capture(),null);input.start();assert.equal(subscriptions,2);input.dispose();assert.equal(releases,2);
assert.throws(()=>createLiveImageInput(node,{makeCanvas:()=>canvas}).start(),/Update Genereti/);
console.log('Shared subscription, borrowed-frame copying, latest frame, source invalidation and release checks passed');
