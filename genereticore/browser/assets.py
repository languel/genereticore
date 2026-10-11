"""Allowlisted, pinned downloads only; user frames never reach these routes."""
import asyncio,hashlib,json,threading,urllib.request
from pathlib import Path
from aiohttp import web
CATALOG=json.loads(Path(__file__).with_name('assets.json').read_text())
_LOCK=threading.Lock()
_TASKS=set()
_STATE={'phase':'idle','done':0,'total':sum(a['bytes'] for a in CATALOG.values())}

def cache_root():
    import folder_paths
    return Path(folder_paths.models_dir)/'genereticore/browser'

def installed(root=None):
    root=Path(root) if root else cache_root()
    try:return all((root/n).is_file() and (root/n).stat().st_size==a['bytes'] for n,a in CATALOG.items()) and (root/'verified.json').is_file() and json.loads((root/'verified.json').read_text())==CATALOG
    except (OSError,ValueError):return False

def download(root=None):
    root=Path(root) if root else cache_root();root.mkdir(parents=True,exist_ok=True)
    _STATE.update(phase='download',done=0,detail='')
    try:
        for name,a in CATALOG.items():
            dest=root/name
            if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==a['sha256']:_STATE['done']+=a['bytes'];continue
            tmp=root/(name+'.part');digest=hashlib.sha256();size=0
            with urllib.request.urlopen(a['url'],timeout=60) as response,tmp.open('wb') as f:
                while chunk:=response.read(65536):
                    size+=len(chunk)
                    if size>a['bytes']:raise ValueError('Artifact exceeds declared size')
                    f.write(chunk);digest.update(chunk);_STATE['done']+=len(chunk)
            if size!=a['bytes'] or digest.hexdigest()!=a['sha256']:raise ValueError('Artifact checksum mismatch: '+name)
            tmp.replace(dest)
        (root/'verified.json').write_text(json.dumps(CATALOG));_STATE.update(phase='ready')
    except Exception as e:_STATE.update(phase='error',detail=str(e));raise

def register_routes(routes):
    from ..image.live import local_only
    @routes.get('/genereticore/browser/status')
    async def status(request):
        local_only(request);return web.json_response({**_STATE,'installed':installed(),'runtime':'onnxruntime-web 1.24.3','license':'BSD-3-Clause models; MIT runtime'})
    @routes.post('/genereticore/browser/download')
    async def install(request):
        local_only(request)
        if not _LOCK.acquire(blocking=False):return web.json_response({'detail':'Download already running'},status=409)
        async def task():
            try:await asyncio.to_thread(download)
            except Exception:pass
            finally:_LOCK.release()
        job=asyncio.create_task(task());_TASKS.add(job);job.add_done_callback(_TASKS.discard)
        return web.json_response({'started':True},status=202)
    @routes.get('/genereticore/browser/assets/{name}')
    async def asset(request):
        local_only(request);name=request.match_info['name']
        if name not in CATALOG or not installed():raise web.HTTPNotFound()
        path=cache_root()/name
        if hashlib.sha256(await asyncio.to_thread(path.read_bytes)).hexdigest()!=CATALOG[name]['sha256']:
            (cache_root()/'verified.json').unlink(missing_ok=True)
            raise web.HTTPConflict(text='Artifact changed; download again')
        response=web.FileResponse(path)
        response.content_type='application/wasm' if name.endswith('.wasm') else 'text/javascript' if name.endswith('.mjs') else 'application/octet-stream'
        response.headers['Cache-Control']='no-cache';return response
