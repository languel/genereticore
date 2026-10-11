import {packImage,unpackImage} from './onnx-image.mjs';
let ort,session,backend,model;
self.onmessage=async({data:m})=>{
 try{
  if(m.type==='load'){
   backend=m.backend;model=m.model;
   if(!['webgpu','wasm'].includes(backend)||!['animevideo','general'].includes(model))throw Error('Unknown browser backend or model.');
   if(backend==='webgpu'&&!navigator.gpu)throw Error('WebGPU is unavailable. Select WASM explicitly to use CPU.');
   ort=await import('/genereticore/browser/assets/ort.webgpu.bundle.min.mjs');ort.env.wasm.numThreads=1;ort.env.wasm.proxy=false;ort.env.wasm.wasmPaths=new URL('/genereticore/browser/assets/',self.location).href;
   const start=performance.now();session=await ort.InferenceSession.create('/genereticore/browser/assets/'+model+'.onnx',{executionProviders:[backend],graphOptimizationLevel:'all'});
   const warm=await session.run({image:new ort.Tensor('float32',new Float32Array(3*266*266),[1,3,266,266])});for(const v of Object.values(warm))v.dispose();
   self.postMessage({type:'ready',loadMs:performance.now()-start,backend,model});return;
  }
  if(m.type==='frame'){
   if(!session)throw Error('Load a model first.');const start=performance.now(),{width,height}=m;
   const x=new ort.Tensor('float32',packImage(new Uint8ClampedArray(m.rgba),width,height),[1,3,266,266]);const prepared=performance.now();
   const outputs=await session.run({image:x});const predicted=performance.now();const y=outputs.output;
   try{
    const pixels=unpackImage(y.data,width*4,height*4);const large=new OffscreenCanvas(width*4,height*4);large.getContext('2d').putImageData(new ImageData(pixels,width*4,height*4),0,0);
    const factor={source:1,'2x':2,'4x':4}[m.scale];if(!factor)throw Error('Unknown output scale');
    const result=new OffscreenCanvas(width*factor,height*factor),ctx=result.getContext('2d');ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(large,0,0,result.width,result.height);
    const bitmap=result.transferToImageBitmap();self.postMessage({type:'result',id:m.id,revision:m.revision,bitmap,totalMs:performance.now()-start,modelMs:predicted-prepared,backend,model},[bitmap]);
   }finally{x.dispose();for(const v of Object.values(outputs))v.dispose();}
  }
 }catch(e){self.postMessage({type:'error',message:e.message});}
};
