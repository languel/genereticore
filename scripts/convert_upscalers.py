"""Contributor-only fixed-shape Real-ESRGAN export; weights stay outside Git.

SRVGG architecture follows xinntao/Real-ESRGAN (BSD-3-Clause). Original
copyright: Xintao Wang, 2021. Retain upstream LICENSE with every export.
"""
import argparse, hashlib, json, urllib.request
from pathlib import Path
import numpy as np
import torch
from torch import nn
import coremltools as ct

RELEASE='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/'
REVISION='a4abfb2979a7bbff3f69f58f58ae324608821e27'
MODELS={'animevideo':('realesr-animevideov3.pth',16,'b8a8376811077954d82ca3fcf476f1ac3da3e8a68a4f4d71363008000a18b75d'),'general':('realesr-general-x4v3.pth',32,'8dc7edb9ac80ccdc30c3a5dca6616509367f05fbc184ad95b731f05bece96292')}
class Compact(nn.Module):
    def __init__(self, layers):
        super().__init__()
        self.body=nn.ModuleList([nn.Conv2d(3,64,3,1,1),nn.PReLU(64)])
        for _ in range(layers):self.body.extend([nn.Conv2d(64,64,3,1,1),nn.PReLU(64)])
        self.body.append(nn.Conv2d(64,48,3,1,1))
    def forward(self,x):
        out=x
        for layer in self.body:out=layer(out)
        return torch.nn.functional.pixel_shuffle(out,4)+torch.nn.functional.interpolate(x,scale_factor=4,mode='nearest')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output-root',type=Path,required=True);a=p.parse_args()
    root=a.output_root.resolve()
    if Path(__file__).resolve().parents[1] in (root,*root.parents):raise ValueError('Use an output folder outside Git')
    root.mkdir(parents=True,exist_ok=True);torch.set_num_threads(6)
    commit=REVISION
    license_url=f'https://raw.githubusercontent.com/xinntao/Real-ESRGAN/{commit}/LICENSE'
    urllib.request.urlretrieve(license_url,root/'LICENSE')
    sources=[];parity=[]
    for name,(filename,layers,expected_hash) in MODELS.items():
        weights=root/filename;url=RELEASE+filename
        if not weights.exists():urllib.request.urlretrieve(url,weights)
        assert hashlib.sha256(weights.read_bytes()).hexdigest()==expected_hash, 'Source weight checksum mismatch'
        sources.append({'model':name,'url':url,'sha256':hashlib.sha256(weights.read_bytes()).hexdigest(),'architecture_revision':commit,'license':'BSD-3-Clause'})
        net=Compact(layers).eval();state=torch.load(weights,map_location='cpu',weights_only=True);net.load_state_dict(state.get('params_ema',state.get('params',state)),strict=True)
        for size in (256,512):
            tile=size+10;dest=root/'upscalers'/name/f'{size}.mlpackage';dest.parent.mkdir(parents=True,exist_ok=True)
            sample=torch.zeros(1,3,tile,tile)
            if not dest.exists():
                traced=torch.jit.trace(net,sample,check_trace=False)
                model=ct.convert(traced,inputs=[ct.TensorType(name='image',shape=sample.shape,dtype=np.float32)],outputs=[ct.TensorType(name='output',dtype=np.float32)],minimum_deployment_target=ct.target.macOS14,convert_to='mlprogram',compute_precision=ct.precision.FLOAT16,compute_units=ct.ComputeUnit.CPU_AND_GPU)
                model.save(str(dest))
            else:model=ct.models.MLModel(str(dest),compute_units=ct.ComputeUnit.CPU_AND_GPU)
            rng=np.random.default_rng(42);x=rng.random((1,3,tile,tile),dtype=np.float32)
            with torch.inference_mode():expected=net(torch.from_numpy(x)).numpy()
            actual=model.predict({'image':x})['output'];rmse=float(np.sqrt(np.mean((expected-actual)**2)))
            assert actual.shape==expected.shape and np.isfinite(actual).all() and rmse<.01,(name,size,rmse)
            row={'model':name,'size':size,'rmse':rmse,'output_shape':list(actual.shape)};parity.append(row);print(json.dumps(row),flush=True)
    (root/'sources.json').write_text(json.dumps(sources,indent=2));(root/'parity.json').write_text(json.dumps(parity,indent=2))
if __name__=='__main__':main()
