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
        manifest = {'family': 'sdxs', 'files': entries}
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
