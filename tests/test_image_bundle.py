"""Verify downloaded bytes and preserve existing student installations."""
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('image_bundle', Path(__file__).parents[1] / 'scripts/image_bundle.py')
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)

class ImageBundleTests(unittest.TestCase):
    def fixture(self, root):
        entries = []
        for name in ['512/unet.mlpackage/data', 'assets/sdxs/tokenizer/config.json']:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'original')
            entries.append({'path': name, 'bytes': 8, 'sha256': bundle.digest(path)})
        manifest = {'format': 1, 'family': 'sdxs', 'files': entries}
        (root / 'manifest.json').write_text(json.dumps(manifest))
        return manifest

    def test_rejects_tampering_and_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = self.fixture(root)
            bundle.verify(root)
            (root / manifest['files'][0]['path']).write_bytes(b'changed!')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                bundle.verify(root)
            manifest['files'][0]['path'] = '../escape'
            (root / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                bundle.verify(root)

    def test_preflights_conflicts_and_allows_identical_retry(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'download'; source.mkdir()
            self.fixture(source)
            dest = root / 'installed'
            conflict = dest / 'assets/sdxs/tokenizer/config.json'
            conflict.parent.mkdir(parents=True); conflict.write_bytes(b'my version')
            sdk = SimpleNamespace(snapshot_download=lambda *a, **kw: str(source))
            with patch.dict('sys.modules', {'huggingface_hub': sdk}):
                with self.assertRaises(FileExistsError):
                    bundle.install('owner/model', 'a' * 40, dest)
                self.assertFalse((dest / '512').exists())
                self.assertEqual(conflict.read_bytes(), b'my version')
                conflict.write_bytes(b'original')
                bundle.install('owner/model', 'a' * 40, dest)
                bundle.install('owner/model', 'a' * 40, dest)
                self.assertEqual((dest / '512/unet.mlpackage/data').read_bytes(), b'original')
                with self.assertRaisesRegex(ValueError, 'pinned'):
                    bundle.install('owner/model', 'main', dest)

class DownloadManagerTests(unittest.TestCase):
    def test_anonymous_download_retains_notices_and_detects_missing_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=root/'hub'; source.mkdir(); destination=root/'installed'
            manifest=ImageBundleTests().fixture(source)
            notice=source/'Notice.txt'; notice.write_text('Credits and source terms')
            manifest['files'].append({'path':'Notice.txt','bytes':notice.stat().st_size,'sha256':bundle.digest(notice)})
            (source/'manifest.json').write_text(json.dumps(manifest))
            entry={'family':'sdxs','repo':'owner/test','revision':'b'*40,'private':False,
                   'download_bytes':sum(x['bytes'] for x in manifest['files']),
                   'manifest_sha256':bundle.digest(source/'manifest.json')}
            calls=[]
            def download(repo,path,**kwargs):
                calls.append((repo,path,kwargs));return str(source/path)
            from genereticore.image import bundles
            manager=bundles.DownloadManager(lambda:destination)
            with patch.object(bundles,'catalog',return_value=[entry]),patch.dict('sys.modules',{'huggingface_hub':SimpleNamespace(hf_hub_download=download),'tqdm.auto':SimpleNamespace(tqdm=object)}):
                manager._run(entry)
                self.assertEqual(manager.snapshot()[0]['phase'],'complete')
                self.assertTrue(manager.installed(entry))
                self.assertTrue(all(c[2]['token'] is False and c[2]['revision']==entry['revision'] for c in calls))
                self.assertEqual((destination/'licenses/sdxs'/entry['revision']/'Notice.txt').read_text(),notice.read_text())
                (destination/'512/unet.mlpackage/data').unlink()
                self.assertFalse(manager.installed(entry))

    def test_manifest_pin_blocks_download_and_catalog_limits_start(self):
        from genereticore.image import bundles
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder); ImageBundleTests().fixture(source)
            entry={'family':'sdxs','repo':'owner/test','revision':'c'*40,'private':False,'download_bytes':16,'manifest_sha256':'0'*64}
            manager=bundles.DownloadManager(lambda:source/'installed')
            sdk=SimpleNamespace(hf_hub_download=lambda *a,**kw:str(source/'manifest.json'))
            with patch.object(bundles,'catalog',return_value=[entry]),patch.dict('sys.modules',{'huggingface_hub':sdk,'tqdm.auto':SimpleNamespace(tqdm=object)}):
                manager._run(entry)
                self.assertEqual(manager.snapshot()[0]['phase'],'error')
                self.assertFalse((source/'installed').exists())
                with self.assertRaises(ValueError):manager.start('https://untrusted.example/model')
                manager.active='sdxs'
                with self.assertRaises(RuntimeError):manager.start('sdxs')

    def test_repairs_corrupt_download_cache_without_overwriting_install(self):
        from genereticore.image import bundles
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder);manifest=ImageBundleTests().fixture(source)
            bad=source/manifest['files'][0]['path'];bad.write_bytes(b'corrupt!')
            entry={'family':'sdxs','repo':'owner/test','revision':'d'*40,'private':False,'download_bytes':16,'manifest_sha256':bundle.digest(source/'manifest.json')}
            repairs=[]
            def download(repo,path,**kw):
                if kw.get('force_download'):
                    repairs.append(path);(source/path).write_bytes(b'original')
                return str(source/path)
            manager=bundles.DownloadManager(lambda:source/'installed')
            with patch.dict('sys.modules',{'huggingface_hub':SimpleNamespace(hf_hub_download=download),'tqdm.auto':SimpleNamespace(tqdm=object)}):
                manager._run(entry)
            self.assertEqual(repairs,[manifest['files'][0]['path']])
            self.assertEqual(manager.states['sdxs']['phase'],'complete')
            self.assertEqual((source/'installed'/manifest['files'][0]['path']).read_bytes(),b'original')

    def test_256_packages_install_beside_512_and_are_required_by_receipt(self):
        from genereticore.image import bundles
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'source';source.mkdir()
            manifest=ImageBundleTests().fixture(source)
            model=source/'256/unet.mlpackage/data';model.parent.mkdir(parents=True);model.write_bytes(b'small-model')
            manifest['sizes']=[256,512]
            manifest['files'].append({'path':'256/unet.mlpackage/data','bytes':model.stat().st_size,'sha256':bundle.digest(model)})
            (source/'manifest.json').write_text(json.dumps(manifest))
            destination=Path(folder)/'models'
            bundles.copy_verified(source,destination,bundles.verify(source),'e'*40)
            self.assertEqual((destination/'256/unet.mlpackage/data').read_bytes(),b'small-model')
            self.assertTrue((destination/'512/unet.mlpackage/data').exists())
            manager=bundles.DownloadManager(lambda:destination);entry={'family':'sdxs','revision':'e'*40}
            self.assertTrue(manager.installed(entry))
            (destination/'256/unet.mlpackage/data').unlink()
            self.assertFalse(manager.installed(entry))
