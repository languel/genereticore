"""Exercise migrated package discovery and request boundaries without Torch/models."""
import importlib
import json
from pathlib import Path
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

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
        from aiohttp import web
        self.live.local_only(SimpleNamespace(remote='127.0.0.1',headers={'Origin':'http://127.0.0.1:8188'},host='127.0.0.1:8188'))
        for remote,origin in [('192.0.2.1',None),('127.0.0.1','https://example.com')]:
            with self.assertRaises(web.HTTPForbidden):
                self.live.local_only(SimpleNamespace(remote=remote,headers={'Origin':origin} if origin else {},host='127.0.0.1:8188'))
