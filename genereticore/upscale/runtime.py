from collections import OrderedDict
import hashlib
from pathlib import Path
import platform
import threading
from time import perf_counter
import numpy as np
from PIL import Image

_LOCK=threading.RLock()
_MODELS=OrderedDict()

def validate(model,scale,passes,feedback):
    if model not in ('animevideo','general'):raise ValueError('Choose AnimeVideo or General.')
    if scale not in ('source','2x','4x'):raise ValueError('Choose source, 2x or 4x output.')
    if isinstance(passes,bool) or passes not in (1,2):raise ValueError('Choose one or two refinement passes.')
    if isinstance(feedback,bool) or not isinstance(feedback,(int,float)) or not np.isfinite(feedback) or not 0<=feedback<=1:raise ValueError('Refinement feedback must be between zero and one.')

def refine(image,predict,scale='4x',passes=1,feedback=.75):
    base=image.convert('RGB');current=base
    for i in range(passes):
        output=predict(current)
        if i+1<passes:current=Image.blend(base,output.resize(base.size,Image.Resampling.LANCZOS),feedback)
    factor={'source':1,'2x':2,'4x':4}[scale];size=(base.width*factor,base.height*factor)
    return output if output.size==size else output.resize(size,Image.Resampling.LANCZOS)

class Model:
    def __init__(self,path,cache,size):
        import coremltools as ct
        self.tile=size+10
        signature='|'.join(f'{p.relative_to(path)}:{p.stat().st_size}:{p.stat().st_mtime_ns}' for p in sorted(path.rglob('*')) if p.is_file())
        key=hashlib.sha256((ct.__version__+signature).encode()).hexdigest()[:16]
        compiled=cache/f'{path.parent.name}-{size}-{key}.mlmodelc';cache.mkdir(parents=True,exist_ok=True)
        if not compiled.exists():ct.models.utils.compile_model(str(path),destination_path=str(compiled))
        self.model=ct.models.CompiledMLModel(str(compiled),compute_units=ct.ComputeUnit.CPU_AND_GPU)
    def predict(self,image):
        x=np.asarray(image.convert('RGB'),dtype=np.float32)/255
        h,w=x.shape[:2]
        x=np.pad(x,((0,self.tile-h),(0,self.tile-w),(0,0)),mode='reflect')
        result=self.model.predict({'image':x.transpose(2,0,1)[None]})['output'][0].transpose(1,2,0)[:h*4,:w*4]
        return Image.fromarray(np.rint(np.clip(result,0,1)*255).astype(np.uint8))

def upscale(image,root,model='animevideo',scale='2x',passes=1,feedback=.75):
    validate(model,scale,passes,feedback)
    if platform.system()!='Darwin' or platform.machine()!='arm64' or int(platform.mac_ver()[0].split('.')[0] or 0)<14:raise RuntimeError('Core ML upscaling requires macOS 14+ Apple silicon.')
    if min(image.size)<2 or max(image.size)>512:raise ValueError('Upscaler accepts images from 2 to 512 pixels per side; resize larger inputs explicitly.')
    size=256 if max(image.size)<=256 else 512;root=Path(root);path=root/'upscalers'/model/f'{size}.mlpackage'
    if not path.is_dir():raise ValueError('Download the Real-ESRGAN bundle with ↓ first.')
    started=perf_counter()
    with _LOCK:
        key=(str(path.resolve()),size)
        if key not in _MODELS:
            loaded=Model(path,root/'compiled/upscalers',size);_MODELS[key]=loaded
            if len(_MODELS)>2:_MODELS.popitem(last=False)
        _MODELS.move_to_end(key);loaded=_MODELS[key];ready=perf_counter()
        output=refine(image,loaded.predict,scale,passes,feedback)
    return output,{'model':model,'native_size':size,'input_size':list(image.size),'output_size':list(output.size),'passes':passes,'feedback':feedback,'load_wait_ms':round((ready-started)*1000,2),'inference_ms':round((perf_counter()-ready)*1000,2),'total_ms':round((perf_counter()-started)*1000,2)}
