import json
import numpy as np
import torch
from comfy_api.latest import io
from ..image.nodes import model_root,tensor_image
from .runtime import upscale

class GeneretiCoreUpscale(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(node_id='GeneretiCoreUpscale',display_name='ꘅ Real-ESRGAN upscale',category='GeneretiCore / Native Core ML',description='Local compact Real-ESRGAN on macOS 14+ Apple silicon. Explicit download and live Start. Inputs up to 512px; choose 2x, 4x or same-size cleanup. Refinement is same-image processing, not temporal feedback.',inputs=[io.Image.Input('image'),io.Combo.Input('model',options=['animevideo','general'],default='animevideo'),io.Combo.Input('scale',options=['source','2x','4x'],default='2x'),io.Int.Input('passes',default=1,min=1,max=2,tooltip='Two passes upscale, downsample, blend and upscale again; costs another prediction.'),io.Float.Input('feedback',default=.75,min=0,max=1,step=.05,tooltip='Same-image refinement blend, used only with two passes. No previous-frame history.')],outputs=[io.Image.Output(display_name='image'),io.String.Output(display_name='metrics')])
    @classmethod
    def execute(cls,image,model,scale,passes,feedback):
        if len(image)>4:raise ValueError('Upscale at most four queued images per batch.')
        outputs=[];metrics=[]
        for item in image:
            result,info=upscale(tensor_image(item[None]),model_root(),model,scale,passes,feedback)
            outputs.append(torch.from_numpy(np.asarray(result,dtype=np.float32).copy()/255));metrics.append(info)
        return io.NodeOutput(torch.stack(outputs),json.dumps(metrics[0] if len(metrics)==1 else metrics))
