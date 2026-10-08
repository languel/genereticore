import hashlib
from pathlib import Path
import tempfile
import unittest
from genereticore.artifacts import ArtifactVerifier

class ArtifactTests(unittest.TestCase):
    def test_detects_corruption_and_path_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'org/model/pin'
            root.mkdir(parents=True)
            path = root / 'weights.bin'
            path.write_bytes(b'abc')
            entry = {'repo':'org/model','revision':'pin','files':[{'path':'weights.bin','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}]}
            verifier = ArtifactVerifier()
            verifier.verify(directory, entry)
            path.write_bytes(b'xyz')
            with self.assertRaisesRegex(RuntimeError,'checksum'): verifier.verify(directory,entry)
            entry['files'][0]['path'] = '../outside'
            with self.assertRaisesRegex(RuntimeError,'Unsafe'): verifier.verify(directory,entry)
    def test_rejects_symlink_outside_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'org/model/pin'; root.mkdir(parents=True)
            outside = Path(directory) / 'outside'; outside.write_bytes(b'abc')
            (root / 'file').symlink_to(outside)
            entry = {'repo':'org/model','revision':'pin','files':[{'path':'file','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}]}
            with self.assertRaisesRegex(RuntimeError,'outside'): ArtifactVerifier().verify(directory,entry)

if __name__ == '__main__': unittest.main()
