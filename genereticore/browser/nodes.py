from comfy_api.latest import io

class GeneretiCoreBrowserUpscale(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(node_id='GeneretiCoreBrowserUpscale',display_name='ꘅ ONNX upscale',category='GeneretiCore / Browser',description='Experimental local browser worker. Explicit verified download, WebGPU or WASM selection and Start. 2–256px IMAGE sources; no cloud inference or automatic camera start. Queue requires the native upscaler instead.',inputs=[io.Image.Input('image'),io.Combo.Input('model',options=['animevideo','general'],default='animevideo'),io.Combo.Input('backend',options=['webgpu','wasm'],default='webgpu'),io.Combo.Input('scale',options=['source','2x','4x'],default='2x')],outputs=[io.Image.Output(display_name='image')],is_experimental=True)
    @classmethod
    def execute(cls,image,model,backend,scale):
        raise RuntimeError('ONNX upscale runs in an active browser on Live delivery. For queued IMAGE processing use Real-ESRGAN upscale (native).')
