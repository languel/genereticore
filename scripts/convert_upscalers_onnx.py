"""Contributor-only ONNX exports of reviewed official Real-ESRGAN weights."""
import argparse, hashlib, json, urllib.request
from pathlib import Path
import numpy as np
import torch
import onnx
import onnxruntime as ort
from convert_upscalers import Compact, MODELS, RELEASE, REVISION

def main():
    p=argparse.ArgumentParser();p.add_argument('--output-root',type=Path,required=True);a=p.parse_args();root=a.output_root.resolve()
    if Path(__file__).resolve().parents[1] in (root,*root.parents):raise ValueError('Keep exports outside Git')
    root.mkdir(parents=True,exist_ok=True);torch.set_num_threads(6);rows=[]
    urllib.request.urlretrieve(f'https://raw.githubusercontent.com/xinntao/Real-ESRGAN/{REVISION}/LICENSE',root/'LICENSE')
    for name,(filename,layers,sha) in MODELS.items():
        path=root/filename
        if not path.exists():urllib.request.urlretrieve(RELEASE+filename,path)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
        net=Compact(layers).eval();state=torch.load(path,map_location='cpu',weights_only=True);net.load_state_dict(state.get('params_ema',state.get('params',state)))
        dest=root/'onnx'/name/'256.onnx';dest.parent.mkdir(parents=True,exist_ok=True);x=torch.from_numpy(np.random.default_rng(42).random((1,3,266,266),dtype=np.float32))
        torch.onnx.export(net,x,dest,input_names=['image'],output_names=['output'],opset_version=17,dynamo=False)
        m=onnx.load(dest);onnx.checker.check_model(m);session=ort.InferenceSession(str(dest),providers=['CPUExecutionProvider'])
        with torch.inference_mode():expected=net(x).numpy()
        actual=session.run(None,{'image':x.numpy()})[0];rmse=float(np.sqrt(np.mean((actual-expected)**2)));assert np.isfinite(actual).all() and rmse<1e-5,rmse
        rows.append({'model':name,'path':f'onnx/{name}/256.onnx','sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size,'rmse':rmse,'shape':list(actual.shape),'source_url':RELEASE+filename,'source_sha256':sha,'architecture_revision':REVISION})
        print(json.dumps(rows[-1]),flush=True)
    (root/'onnx'/'provenance.json').write_text(json.dumps({'torch':torch.__version__,'onnx':onnx.__version__,'onnxruntime':ort.__version__,'opset':17,'license':'BSD-3-Clause','input':'float32 RGB NCHW [0,1], reflect-pad right/bottom to 266; crop output to 4x source; alpha on white','models':rows},indent=2)+'\n')
    (root/'onnx'/'LICENSE').write_bytes((root/'LICENSE').read_bytes())
    (root/'onnx'/'README.md').write_text('# Browser ONNX exports\n\nCompact Real-ESRGAN by Xintao Wang and contributors, BSD-3-Clause. [Upstream](https://github.com/xinntao/Real-ESRGAN). Independently exported from official reviewed weights. Credits/full terms in LICENSE; sources, checksums, tool versions and PyTorch/ONNX parity in provenance.json. Fixed 266px input accommodates 2–256px source images with reflected padding. Predicts 4x; smaller outputs downsample. No temporal history. Browser benchmarks are recorded in GeneretiCore docs/browser-onnx.md. No upstream endorsement.\n')
if __name__=='__main__':main()
