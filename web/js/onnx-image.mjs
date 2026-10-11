// Match native compact SRVGG: RGB NCHW, white alpha, right/bottom reflection.
export function reflect(index,length){const period=2*(length-1);const x=index%period;return x<length?x:period-x;}
export function packImage(rgba,width,height,tile=266){
 if(!Number.isInteger(width)||!Number.isInteger(height)||Math.min(width,height)<2||Math.max(width,height)>256||rgba.length!==width*height*4)throw Error('Resize the input explicitly to 2–256px per side.');
 const area=tile*tile,out=new Float32Array(area*3);
 for(let y=0;y<tile;y++)for(let x=0;x<tile;x++){
  const i=(reflect(y,height)*width+reflect(x,width))*4,a=rgba[i+3]/255,j=y*tile+x;
  for(let c=0;c<3;c++)out[c*area+j]=(rgba[i+c]*a+255*(1-a))/255;
 }
 return out;
}
export function unpackImage(data,width,height,tile=1064){
 const out=new Uint8ClampedArray(width*height*4),area=tile*tile;
 for(let y=0;y<height;y++)for(let x=0;x<width;x++){
  const i=(y*width+x)*4,j=y*tile+x;
  for(let c=0;c<3;c++)out[i+c]=Math.round(Math.max(0,Math.min(1,data[c*area+j]))*255);out[i+3]=255;
 }
 return out;
}
