import hashlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from genereticore.browser import assets
class BrowserAssetsTests(unittest.TestCase):
 def test_verified_install_and_missing_payload_invalidation(self):
  data=b'fixture';catalog={'model.onnx':{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'url':'https://example.test/pinned'}}
  with tempfile.TemporaryDirectory() as d,patch.object(assets,'CATALOG',catalog),patch.object(assets.urllib.request,'urlopen',return_value=io.BytesIO(data)):
   assets.download(d);self.assertTrue(assets.installed(d));(Path(d)/'model.onnx').unlink();self.assertFalse(assets.installed(d))
 def test_checksum_rejection_never_marks_install_complete(self):
  catalog={'model.onnx':{'bytes':3,'sha256':'0'*64,'url':'https://example.test/pinned'}}
  with tempfile.TemporaryDirectory() as d,patch.object(assets,'CATALOG',catalog),patch.object(assets.urllib.request,'urlopen',return_value=io.BytesIO(b'bad')):
   with self.assertRaisesRegex(ValueError,'checksum'):assets.download(d)
   self.assertFalse(assets.installed(d));self.assertFalse((Path(d)/'model.onnx').exists())
 def test_corrupt_receipt_and_changed_catalog_invalidate(self):
  with tempfile.TemporaryDirectory() as d,patch.object(assets,'CATALOG',{}):
   (Path(d)/'verified.json').write_text('{');self.assertFalse(assets.installed(d))
if __name__=='__main__':unittest.main()
