"""Verify release-pinned artifacts before any native model is loaded."""
import hashlib
from pathlib import Path, PurePosixPath

class ArtifactVerifier:
    def __init__(self):
        self._verified = {}

    def verify(self, model_dir, entry, emit=lambda *_: None, canceled=lambda: False):
        root = (Path(model_dir) / entry['repo'] / entry['revision']).resolve()
        files = entry.get('files')
        if not files:
            raise RuntimeError('Model has no pinned artifact manifest')
        total, done = sum(f['bytes'] for f in files), 0
        for artifact in files:
            relative = PurePosixPath(artifact['path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise RuntimeError('Unsafe artifact path')
            path = (root / str(relative)).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise RuntimeError('Model artifact missing or outside its bundle')
            stat = path.stat()
            fingerprint = (stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
            key = (str(path), artifact['sha256'])
            if stat.st_size != artifact['bytes']:
                raise RuntimeError(f"Model artifact size mismatch: {relative}")
            if self._verified.get(key) != fingerprint:
                digest = hashlib.sha256()
                with path.open('rb') as stream:
                    while chunk := stream.read(4 * 1024 * 1024):
                        if canceled():
                            raise RuntimeError('Artifact verification canceled')
                        digest.update(chunk)
                if digest.hexdigest() != artifact['sha256']:
                    raise RuntimeError(f"Model artifact checksum mismatch: {relative}")
                self._verified[key] = fingerprint
            done += artifact['bytes']
            emit('verify_progress', {'fraction': done / total if total else 1})
