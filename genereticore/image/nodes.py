from __future__ import annotations
import importlib
import json
import platform
import threading
from pathlib import Path
from time import perf_counter
import numpy as np
import torch
from PIL import Image
import folder_paths

_LOCK = threading.RLock()
_ENGINE = None
_ENGINE_KEY = None
# Honor explicit legacy model-folder configuration. Reuse the old directory if present.
try:
    configured_paths = folder_paths.get_folder_paths('genereti_coreml')
except KeyError:
    configured_paths = []
if not configured_paths:
    legacy = Path(folder_paths.models_dir) / 'genereti'
    folder_paths.add_model_folder_path('genereti_coreml', str(legacy if legacy.exists() else Path(folder_paths.models_dir) / 'genereticore/images'))


def model_root():
    return Path(folder_paths.get_folder_paths('genereti_coreml')[0])


def sizes():
    root = model_root()
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir() and p.name.isdigit()
        and all((p / f'{name}.mlpackage').exists() for name in ('unet', 'encoder', 'decoder')))


def model_paths():
    result = {}
    root = model_root()
    resolver = local_module('model_resolution')
    for size in sizes():
        installed = {p.stem for p in (root / size).glob('*.mlpackage')}
        for filename, family, style, candidates in (
            ('unet', 'sdxs', 'base', ('text', 'sketch')),
            ('anime_unet', 'sdxs', 'anime', ('text', 'sketch')),
            ('turbo_unet', 'sd_turbo', 'base', ('image', 'canny', 'depth', 'pose'))):
            if filename not in installed:
                continue
            modes = [m for m in candidates if resolver.required_models(m, style).issubset(installed)]
            result[f'{size}/{filename}.mlpackage'] = dict(size=size, family=family, style=style, modes=modes)
    return result


def local_module(name):
    return importlib.import_module('.' + name, __package__)


def tensor_image(image):
    if image is None:
        return None
    pixels = (image[0].detach().cpu().numpy().clip(0, 1) * 255).astype(np.uint8)
    picture = Image.fromarray(pixels)
    if picture.mode == 'RGBA':
        picture = Image.alpha_composite(Image.new('RGBA', picture.size, 'white'), picture)
    return picture.convert('RGB')


def get_engine(root, size):
    global _ENGINE, _ENGINE_KEY
    key = (str(Path(root).resolve()), int(size))
    with _LOCK:
        if _ENGINE_KEY != key:
            engine = local_module('engine').Engine(int(size), model_root=root, threads=None)
            _ENGINE = engine
            _ENGINE_KEY = key
        return _ENGINE


def generate(model_path, prompt, mode, seed=42, control_scale=1., invert=False,
             movement=0., image=None, preprocess=False, strength=.65, noise_phase=0., family=None, blank_prompt_enabled=False,
             blank_prompt='closeup flat white blank paper space pristine smooth emptiness', blank_action='prompt'):
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise RuntimeError('GeneretiCore image inference requires macOS 14+ on Apple silicon.')
    if int(platform.mac_ver()[0].split('.')[0]) < 14:
        raise RuntimeError('GeneretiCore image inference requires macOS 14 or later.')
    profile = model_paths().get(model_path)
    if not profile or (family and profile['family'] != family):
        raise ValueError('Choose an installed model package for this generator family.')
    if mode not in profile['modes']:
        raise ValueError(f"{model_path} supports: {', '.join(profile['modes'])}. Select a supported mode.")
    start = perf_counter()
    with _LOCK:
        picture = None if mode == 'text' else tensor_image(image)
        if mode != 'text' and picture is None:
            raise ValueError('This mode requires an IMAGE input.')
        blank = bool(blank_prompt_enabled and picture is not None and local_module('blank').is_blank(picture))
        if blank and blank_action == 'solid':
            size = int(profile['size'])
            result = torch.ones((1, size, size, 3), dtype=torch.float32)
            return result, json.dumps({'inference_ms':0, 'size':size, 'blank_input':True,
                'blank_action':'solid', 'backend':'Solid white', 'model_path':model_path,
                'family':profile['family'], 'node_ms':round((perf_counter()-start)*1000,2)})
        if blank:
            prompt = blank_prompt
        engine = get_engine(model_root(), int(profile['size']))
        if preprocess and mode in ('canny', 'depth'):
            if not hasattr(engine, '_genereti_guides'):
                engine._genereti_guides = local_module('guides').GuideProcessor()
            picture = engine._genereti_guides.process(picture, mode, engine.size)
        if picture is not None and invert:
            from PIL import ImageOps
            picture = ImageOps.invert(picture)
        output, metrics = engine.generate(prompt, image=picture, mode=mode, style=profile['style'],
            seed=seed, strength=strength, control_scale=control_scale, noise_phase=noise_phase)
        result = torch.from_numpy(np.asarray(output.convert('RGB'), dtype=np.float32).copy() / 255)[None]
        return (result, json.dumps({**metrics, 'backend':'Core ML in Comfy',
            'size':engine.size, 'blank_input':blank, 'blank_action':blank_action if blank else None, 'model_path':model_path, 'family':profile['family'],
            'node_ms':round((perf_counter()-start)*1000,2)}))


class FamilyGenerator:
    CATEGORY = 'GeneretiCore / Native Core ML'
    FUNCTION = 'execute'
    RETURN_TYPES = ('IMAGE', 'STRING')
    RETURN_NAMES = ('image', 'metrics')
    DESCRIPTION = 'Local Core ML on macOS 14+ Apple silicon. Choose installed packages. Live starts explicitly; Queue uses Comfy Run. Download 512px models explicitly with ↓. Credits and license terms are in the node reference. No automatic inference on load.'
    family = None

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float('nan')

    @classmethod
    def INPUT_TYPES(cls):
        paths = [path for path, profile in model_paths().items() if profile['family'] == cls.family]
        turbo = cls.family == 'sd_turbo'
        required = {
            'model_path': (paths or ['not installed'], {'tooltip':'Installed denoiser path determines native size and variant; companion packages live beside it.'}),
            'prompt': ('STRING', {'default':'A luminous abstract performance stage made from hand-cut paper shapes, cobalt blue and orange light, energetic theatrical composition', 'multiline':True}),
            'mode': (['image','canny','depth','pose'] if turbo else ['text','sketch'], {'default':'image' if turbo else 'sketch'}),
            'seed': ('INT', {'default':42, 'min':0, 'max':4294967295, 'step':1, 'tooltip':'Click the number, select its text, type an integer and press Enter. Editable during Live; the next frame uses the new seed.'})}
        if turbo:
            required.update({
                'preprocess': ('BOOLEAN', {'default':True,'tooltip':'Extract Canny edges or depth; disable for prepared guides.'}),
                'strength': ('FLOAT', {'default':.65,'min':.05,'max':1.,'step':.01,'tooltip':'Image remix noise strength; guide modes use one fixed step.'})})
        required.update({
            'control_scale': ('FLOAT', {'default':1.,'min':0.,'max':65504.,'step':.05,'tooltip':'Guide influence.'}),
            'invert': ('BOOLEAN', {'default':False,'tooltip':'Invert after preprocessing.'}),
            'movement': ('FLOAT', {'default':0.,'min':0.,'max':100.,'step':.01,'tooltip':'Live seed-noise rotation speed. Zero holds noise fixed.'})})
        return {'required':required, 'optional':{'image':('IMAGE',)},
            'hidden':{'unique_id':'UNIQUE_ID', 'extra_pnginfo':'EXTRA_PNGINFO'}}

    @classmethod
    def execute(cls, **kwargs):
        unique_id = kwargs.pop('unique_id', None)
        metadata = kwargs.pop('extra_pnginfo', None) or {}
        for node in metadata.get('workflow', {}).get('nodes', []):
            if str(node.get('id')) == str(unique_id):
                props = node.get('properties', {})
                kwargs.update(blank_prompt_enabled=bool(props.get('genereticore_blank_enabled', False)),
                    blank_prompt=props.get('genereticore_blank_prompt', 'closeup flat white blank paper space pristine smooth emptiness'),
                    blank_action=props.get('genereticore_blank_action', 'prompt'))
                break
        return generate(**kwargs, family=cls.family)

class GeneretiSDXSGenerate(FamilyGenerator):
    family = 'sdxs'

class GeneretiSDTurboGenerate(FamilyGenerator):
    family = 'sd_turbo'

NODE_CLASS_MAPPINGS = {c.__name__:c for c in (GeneretiSDXSGenerate,GeneretiSDTurboGenerate)}
NODE_DISPLAY_NAME_MAPPINGS = {'GeneretiSDXSGenerate':'ꘅ SDXS generator','GeneretiSDTurboGenerate':'ꘅ SD Turbo generator'}
