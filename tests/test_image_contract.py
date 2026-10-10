"""Exercise migrated package discovery and request boundaries without Torch/models."""
import importlib
import json
from pathlib import Path
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch, Mock
from aiohttp import web

class ImageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=ModuleType('folder_paths')
        cls.folder.models_dir='/nonexistent/models'
        cls.folder.get_folder_paths=lambda name: ['/nonexistent/models/genereti']
        cls.folder.add_model_folder_path=lambda *a: None
        with patch.dict('sys.modules',{'torch':ModuleType('torch'),'folder_paths':cls.folder}):
            cls.nodes=importlib.import_module('genereticore.image.nodes')
            cls.live=importlib.import_module('genereticore.image.live')

    def test_discovery_excludes_incomplete_bundles_and_filters_guides(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);size=root/'256';size.mkdir()
            for name in ['unet','encoder','decoder','turbo_unet']:(size/f'{name}.mlpackage').mkdir()
            with patch.object(self.nodes,'model_root',return_value=root):
                profiles=self.nodes.model_paths()
                self.assertEqual(profiles['256/unet.mlpackage']['modes'],['text'])
                self.assertEqual(profiles['256/turbo_unet.mlpackage']['modes'],['image'])
                for name in ['controlled_unet','control_canny','turbo_residual_unet']:(size/f'{name}.mlpackage').mkdir()
                self.assertEqual(self.nodes.model_paths()['256/unet.mlpackage']['modes'],['text','sketch'])
                self.assertEqual(self.nodes.model_paths()['256/turbo_unet.mlpackage']['modes'],['image','canny'])
                (size/'decoder.mlpackage').rmdir()
                self.assertEqual(self.nodes.model_paths(),{})

    def test_preserved_ids_input_order_and_unsupported_platform(self):
        self.assertEqual(set(self.nodes.NODE_CLASS_MAPPINGS),{'GeneretiSDXSGenerate','GeneretiSDTurboGenerate'})
        with patch.object(self.nodes,'model_paths',return_value={}):
            self.assertEqual(list(self.nodes.GeneretiSDXSGenerate.INPUT_TYPES()['required']),['model_path','prompt','mode','seed','control_scale','invert','movement'])
            self.assertEqual(list(self.nodes.GeneretiSDTurboGenerate.INPUT_TYPES()['required']),['model_path','prompt','mode','seed','preprocess','strength','control_scale','invert','movement'])
        with patch.object(self.nodes.platform,'system',return_value='Linux'):
            with self.assertRaisesRegex(RuntimeError,'Apple silicon'):
                self.nodes.GeneretiSDXSGenerate.execute(model_path='256/unet.mlpackage',prompt='stage',mode='text')

    def test_live_validation_and_same_origin_loopback(self):
        with patch.object(self.live,'model_paths',return_value={'256/unet.mlpackage':{'family':'sdxs'}}):
            self.assertEqual(self.live.validate({'model_path':'256/unet.mlpackage'})['seed'],42)
            for invalid in [{'seed':True},{'noise_phase':float('nan')},{'image':'x'*2_800_001},{'family':'sd_turbo'},{'preprocess':'yes'}]:
                with self.assertRaises(ValueError):self.live.validate({'model_path':'256/unet.mlpackage',**invalid})
        self.live.local_only(SimpleNamespace(remote='127.0.0.1',headers={'Origin':'http://127.0.0.1:8188'},host='127.0.0.1:8188'))
        for remote,origin in [('192.0.2.1',None),('127.0.0.1','https://example.com')]:
            with self.assertRaises(web.HTTPForbidden):
                self.live.local_only(SimpleNamespace(remote=remote,headers={'Origin':origin} if origin else {},host='127.0.0.1:8188'))

    def test_blank_prompt_switches_back_to_main_prompt(self):
        import numpy as np
        from PIL import Image
        engine = Mock(size=16)
        engine.generate.return_value = (Image.new('RGB', (16,16), 'white'), {'inference_ms':1})
        picture = Image.new('RGB', (16,16), 'white')
        with patch.object(self.nodes.platform, 'system', return_value='Darwin'), \
             patch.object(self.nodes.platform, 'machine', return_value='arm64'), \
             patch.object(self.nodes.platform, 'mac_ver', return_value=('14.0', (), '')), \
             patch.object(self.nodes, 'model_paths', return_value={'16/unet.mlpackage':{'family':'sdxs','size':'16','modes':['sketch'],'style':'base'}}), \
             patch.object(self.nodes, 'get_engine', return_value=engine), \
             patch.object(self.nodes, 'tensor_image', return_value=picture), \
             patch.object(self.nodes.torch, 'from_numpy', side_effect=lambda x:x, create=True):
            args=dict(model_path='16/unet.mlpackage',prompt='ink wash',mode='sketch',blank_prompt_enabled=True,blank_prompt='empty white')
            result=self.nodes.generate(**args)
            self.assertEqual(engine.generate.call_args.args[0], 'empty white')
            self.assertTrue(json.loads(result[1])['blank_input'])
            picture.putpixel((8,8), (0,0,0))
            result=self.nodes.generate(**args)
            self.assertEqual(engine.generate.call_args.args[0], 'ink wash')
            self.assertFalse(json.loads(result[1])['blank_input'])

    def test_queue_reads_only_its_own_saved_blank_settings(self):
        metadata={'workflow':{'nodes':[{'id':7,'properties':{'genereticore_blank_enabled':True,'genereticore_blank_prompt':'empty','genereticore_blank_action':'solid'}},{'id':8,'properties':{'genereticore_blank_enabled':False}}]}}
        with patch.object(self.nodes, 'generate') as generate:
            self.nodes.GeneretiSDXSGenerate.execute(unique_id='7',extra_pnginfo=metadata,prompt='main')
            self.assertEqual(generate.call_args.kwargs['blank_prompt'], 'empty')
            self.assertEqual(generate.call_args.kwargs['blank_action'], 'solid')
            self.nodes.GeneretiSDXSGenerate.execute(unique_id='8',extra_pnginfo=metadata,prompt='main')
            self.assertFalse(generate.call_args.kwargs['blank_prompt_enabled'])
