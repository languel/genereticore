import assert from 'node:assert/strict';
import {packImage,unpackImage,reflect} from '../web/js/onnx-image.mjs';
assert.deepEqual(Array.from({length:8},(_,i)=>reflect(i,3)),[0,1,2,1,0,1,2,1]);
const pixels=new Uint8ClampedArray([255,0,0,255,0,255,0,255,0,0,255,0,0,0,0,255]);
const tensor=packImage(pixels,2,2,4);assert.equal(tensor[0],1);assert.equal(tensor[1],0);assert.equal(tensor[16+1],1);assert.equal(tensor[4],1);assert.equal(tensor[16+4],1);assert.equal(tensor[32+4],1);
const output=unpackImage(new Float32Array([1,2,-1,.5,0,0,0,0,0,0,0,0]),2,2,2);assert.deepEqual(Array.from(output.slice(0,8)),[255,0,0,255,255,0,0,255]);
assert.throws(()=>packImage(new Uint8ClampedArray(4),1,1),/2–256/);assert.throws(()=>packImage(new Uint8ClampedArray(0),256,256),/2–256/);
console.log('Reflection, NCHW ordering, alpha-on-white, crop and clamping checks passed');
