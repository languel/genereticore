import asyncio,base64,io,json
from aiohttp import web
from PIL import Image
from ..image.live import local_only,_BUSY
from ..image.nodes import model_root
from .runtime import upscale,validate

def render(data):
    validate(data.get('model','animevideo'),data.get('scale','2x'),data.get('passes',1),data.get('feedback',.75))
    source=data.get('image')
    if not isinstance(source,str) or len(source)>2_800_000:raise ValueError('Invalid or oversized input image.')
    raw=base64.b64decode(source.split(',',1)[-1],validate=True)
    with Image.open(io.BytesIO(raw)) as image:
        if min(image.size)<2 or max(image.size)>512:raise ValueError('Input must be 2–512px per side.')
        if image.mode=='RGBA':image=Image.alpha_composite(Image.new('RGBA',image.size,'white'),image)
        result,metrics=upscale(image.convert('RGB'),model_root(),data.get('model','animevideo'),data.get('scale','2x'),data.get('passes',1),data.get('feedback',.75))
    buffer=io.BytesIO();result.save(buffer,'PNG',compress_level=1)
    return buffer.getvalue(),metrics

def register_routes(routes):
    @routes.post('/genereticore/coreml/upscale')
    async def process(request):
        local_only(request)
        if _BUSY.locked():return web.json_response({'detail':'Native worker busy; waiting.'},status=429)
        raw=bytearray()
        async for chunk in request.content.iter_chunked(65536):
            raw.extend(chunk)
            if len(raw)>3_000_000:raise web.HTTPRequestEntityTooLarge(max_size=3_000_000,actual_size=len(raw))
        try:
            data=json.loads(raw)
            if not isinstance(data,dict):raise ValueError('Expected a JSON object.')
        except (TypeError,ValueError) as error:return web.json_response({'detail':str(error)},status=400)
        if _BUSY.locked():return web.json_response({'detail':'Native worker busy; waiting.'},status=429)
        async with _BUSY:
            task=asyncio.create_task(asyncio.to_thread(render,data))
            try:png,metrics=await asyncio.shield(task)
            except asyncio.CancelledError:
                await task
                raise
            except (ValueError,FileNotFoundError) as error:return web.json_response({'detail':str(error)},status=400)
            except Exception:return web.json_response({'detail':'Native upscaling failed; check local Comfy logs.'},status=500)
        return web.Response(body=png,content_type='image/png',headers={'X-Inference-Ms':str(metrics['inference_ms']),'X-Output-Width':str(metrics['output_size'][0]),'X-Output-Height':str(metrics['output_size'][1])})
