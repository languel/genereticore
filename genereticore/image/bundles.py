"""Explicit, allowlisted image downloads. No inference or credentials are uploaded."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading

CATALOG = Path(__file__).with_name('bundles.json')

class ChecksumError(ValueError):
    def __init__(self, relative):
        self.relative = str(relative)
        super().__init__(f'Bundle checksum failed: {relative}')

def catalog():
    return json.loads(CATALOG.read_text())['bundles']

def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()

def verify(directory, progress=lambda *_: None):
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest.get('format') != 1 or manifest.get('family') not in ('sdxs', 'sd-turbo', 'esrgan'):
        raise ValueError('Unsupported bundle manifest')
    seen = set()
    files = manifest['files']
    if not files:
        raise ValueError('Empty bundle manifest')
    total = sum(entry['bytes'] for entry in files)
    done = 0
    for entry in files:
        relative = Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts or not relative.parts or str(relative) in seen:
            raise ValueError('Unsafe bundle path')
        seen.add(str(relative))
        path = directory / relative
        if not path.is_file() or path.stat().st_size != entry['bytes'] or digest(path) != entry['sha256']:
            raise ChecksumError(relative)
        done += entry['bytes']; progress('verify', done, total)
    return manifest

def copy_verified(source, destination, manifest, revision):
    family = manifest['family']
    notices = destination / 'licenses' / family / revision
    targets = []
    for entry in manifest['files']:
        relative = Path(entry['path'])
        target = destination / relative if relative.parts[0] in ('256', '512', 'assets', 'upscalers') else notices / relative
        targets.append((entry, target))
        if target.exists() and (not target.is_file() or digest(target) != entry['sha256']):
            raise FileExistsError(f'Conflicting installed file: {target}')
    # Preflight every conflict before changing the installation; publish each
    # copied file atomically so interruption cannot leave a truncated final file.
    for entry, target in targets:
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.genereticore-', delete=False) as stream:
                temporary = Path(stream.name)
                with (source / entry['path']).open('rb') as original:
                    shutil.copyfileobj(original, stream)
            if target.exists():
                if digest(target) != entry['sha256']:
                    raise FileExistsError(f'Conflicting installed file: {target}')
            else:
                os.replace(temporary, target)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    notices.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / 'manifest.json', notices / 'manifest.json')
    receipt = {'family': family, 'revision': revision, 'files': manifest['files']}
    marker = destination / f'.genereticore-{family}.json'
    temp_marker = marker.with_suffix('.part')
    temp_marker.write_text(json.dumps(receipt)); os.replace(temp_marker, marker)

def install(repo, revision, destination):
    from huggingface_hub import snapshot_download
    if len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
        raise ValueError('Use a full pinned Hugging Face commit SHA')
    source = Path(snapshot_download(repo, revision=revision))
    manifest = verify(source)
    copy_verified(source, destination, manifest, revision)
    print(json.dumps({'installed': manifest['family'], 'root': str(destination), 'revision': revision}))

class DownloadManager:
    def __init__(self, root):
        self.root = root
        self.lock = threading.Lock()
        self.active = None
        self.states = {}

    def installed(self, entry):
        root = self.root()
        marker = root / f".genereticore-{entry['family']}.json"
        try:
            receipt = json.loads(marker.read_text())
            if receipt['revision'] != entry['revision']:
                return False
            return all((root / item['path']).is_file() and (root / item['path']).stat().st_size == item['bytes']
                       for item in receipt['files'] if item['path'].startswith(('256/', '512/', 'assets/', 'upscalers/')))
        except (OSError, ValueError, KeyError):
            return False

    def snapshot(self):
        with self.lock:
            return [{**entry, 'installed': self.installed(entry),
                     **self.states.get(entry['family'], {'phase': 'idle', 'done': 0, 'total': entry['download_bytes']})}
                    for entry in catalog()]

    def start(self, family):
        entry = next((item for item in catalog() if item['family'] == family), None)
        if entry is None or entry['private']:
            raise ValueError('Choose a published image bundle')
        with self.lock:
            if self.active is not None:
                raise RuntimeError('Another image download is running')
            self.active = family
            self.states[family] = {'phase': 'download', 'done': 0, 'total': entry['download_bytes']}
        threading.Thread(target=self._run, args=(entry,), daemon=True).start()

    def _update(self, family, phase, done, total):
        with self.lock:
            self.states[family] = {'phase': phase, 'done': done, 'total': total}

    def _run(self, entry):
        family = entry['family']
        try:
            from huggingface_hub import hf_hub_download
            from tqdm.auto import tqdm
            # Anonymous public reads: students need no HF login or token.
            path = Path(hf_hub_download(entry['repo'], 'manifest.json', revision=entry['revision'], token=False))
            if digest(path) != entry['manifest_sha256']:
                path = Path(hf_hub_download(entry['repo'], 'manifest.json', revision=entry['revision'], token=False, force_download=True))
            if digest(path) != entry['manifest_sha256']:
                raise ValueError('Pinned manifest checksum failed')
            manifest = json.loads(path.read_text())
            if manifest['family'] != family:
                raise ValueError('Wrong bundle family')
            total = entry['download_bytes']; done = 0
            manager = self
            class Progress(tqdm):
                def update(self, amount=1):
                    result = super().update(amount)
                    if getattr(self, 'unit', '') == 'B':
                        manager._update(family, 'download', min(done + self.n, total), total)
                    return result
            source = path.parent
            # Download only paths from our checksum-pinned manifest. Validate
            # names before using any as Hub paths; never accept caller URLs.
            for item in manifest['files']:
                relative = Path(item['path'])
                if relative.is_absolute() or '..' in relative.parts or not relative.parts:
                    raise ValueError('Unsafe bundle path')
                hf_hub_download(entry['repo'], item['path'], revision=entry['revision'], token=False, tqdm_class=Progress)
                done += item['bytes']; self._update(family, 'download', done, total)
            try:
                checked = verify(source, lambda phase, current, size: self._update(family, phase, current, size))
            except ChecksumError as corrupt:
                # Repair a bad cached file once rather than indefinitely reusing
                # corrupt bytes on Retry. Never delete or overwrite installed files.
                self._update(family, 'download', 0, total)
                hf_hub_download(entry['repo'], corrupt.relative, revision=entry['revision'], token=False,
                                force_download=True, tqdm_class=Progress)
                checked = verify(source, lambda phase, current, size: self._update(family, phase, current, size))
            self._update(family, 'install', 0, total)
            copy_verified(source, self.root(), checked, entry['revision'])
            self._update(family, 'complete', total, total)
        except Exception as error:
            # Do not echo SDK exception details which could contain environment
            # data. Conflicts and corrupt downloads have actionable local errors.
            detail = 'Existing model files differ; choose a clean model folder.' if isinstance(error, FileExistsError) else 'Download or verification failed. Retry; cached files are reused.'
            with self.lock:
                self.states[family] = {'phase': 'error', 'detail': detail, 'done': 0, 'total': entry['download_bytes']}
        finally:
            with self.lock:
                self.active = None
