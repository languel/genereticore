"""Local d1 Core ML helper, with explicit pinned downloads and no cloud fallback."""
import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import time
from urllib.request import urlopen
from urllib.parse import quote
from .backend import CoreAIBackend
from .catalog import MODELS, model_entry
from .contracts import Capability

class CoreMLBackend(CoreAIBackend):
    def __init__(self, model_dir=None, helper=None):
        super().__init__(model_dir, helper or os.environ.get('GENERETICORE_D1_HELPER', Path(__file__).resolve().parents[1] / 'native/bin/genereticore-d1-helper'))

    def capability(self):
        reason = ''
        if platform.system() != 'Darwin' or platform.machine() != 'arm64' or int(platform.mac_ver()[0].split('.')[0] or 0) < 15:
            reason = 'd1 Core ML requires macOS 15+ Apple silicon'
        elif not self.helper.is_file() or not os.access(self.helper, os.X_OK):
            reason = 'd1 helper missing. Contributor setup: python3 scripts/build_d1_helper.py'
        return Capability('coreml', ('decision.evaluate','model.download'), False, 'terminate_helper', True, not reason, reason)

    def _start(self, canceled):
        with self._process_lock:
            if canceled(): raise RuntimeError('Request canceled before helper start')
            if self._process is None or self._process.poll() is not None:
                if self._process is not None:
                    self._process.wait(timeout=10); self._process.stdin.close(); self._process.stdout.close()
                entry = model_entry('d1-omni-600m')
                directory = self.model_dir / entry['repo'] / entry['revision']
                self._process = subprocess.Popen([str(self.helper), str(directory)], stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding='utf-8', bufsize=1)
            return self._process

    def execute(self, request, emit, canceled=lambda: False):
        entry = model_entry(request.model, request.task)
        if entry['backend'] != 'coreml': raise ValueError('Unsupported Core ML model')
        if request.task != 'model.download': return super().execute(request, emit, canceled)
        start = time.perf_counter()
        root = self.model_dir / entry['repo'] / entry['revision']
        root.mkdir(parents=True, exist_ok=True)
        total = sum(f['bytes'] for f in entry['files'])
        if shutil.disk_usage(root).free < total + 1_000_000_000: raise RuntimeError('Not enough disk space (including 1 GB reserve)')
        done = 0
        for artifact in entry['files']:
            if canceled(): raise RuntimeError('Download canceled')
            target = root / artifact['path']; target.parent.mkdir(parents=True, exist_ok=True)
            # Reuse only a complete, checksum-verified file.
            if target.is_file() and target.stat().st_size == artifact['bytes']:
                digest_state = hashlib.sha256()
                with target.open('rb') as stream:
                    while chunk := stream.read(1024*1024):
                        if canceled(): raise RuntimeError('Download canceled')
                        digest_state.update(chunk)
                digest = digest_state.hexdigest()
                if digest == artifact['sha256']:
                    done += artifact['bytes']; continue
            url = f"https://huggingface.co/{entry['repo']}/resolve/{entry['revision']}/{quote(artifact['path'])}"
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as staged: temporary = Path(staged.name)
            try:
                digest = hashlib.sha256(); size = 0
                with urlopen(url, timeout=30) as response, temporary.open('wb') as stream:
                    while chunk := response.read(1024*1024):
                        if canceled(): raise RuntimeError('Download canceled')
                        size += len(chunk)
                        if size > artifact['bytes']: raise RuntimeError('Artifact exceeds pinned size')
                        digest.update(chunk); stream.write(chunk)
                        emit('download_progress', {'fraction':(done + size)/total})
                if size != artifact['bytes'] or digest.hexdigest() != artifact['sha256']:
                    raise RuntimeError('Downloaded artifact does not match pinned manifest')
                temporary.replace(target)
            finally: temporary.unlink(missing_ok=True)
            done += artifact['bytes']
        self._verifier.verify(self.model_dir, entry, emit, canceled)
        return {'backend':'coreml','content':{'installed':True},'timings':{'total_ms':(time.perf_counter()-start)*1000}}

class LocalBackend:
    """Model-selected routing inside the existing bounded single-worker queue."""
    def __init__(self, model_dir=None, helper=None):
        self.backends = {'coreai':CoreAIBackend(model_dir,helper), 'coreml':CoreMLBackend(model_dir)}
        self.active = None
    def capability(self):
        caps = [b.capability() for b in self.backends.values()]
        return Capability('local', tuple(sorted(set(t for c in caps for t in c.tasks))), True,
            'terminate_helper', True, any(c.available for c in caps), '; '.join(c.reason for c in caps if not c.available))
    def catalog(self):
        return [{**m,'installed':self.backends[m['backend']].installed(m),
                 'available':self.backends[m['backend']].capability().available,
                 'unavailable_reason':self.backends[m['backend']].capability().reason} for m in MODELS.values()]
    def installed(self, entry):
        return self.backends[entry["backend"]].installed(entry)
    def execute(self, request, emit, canceled=lambda:False):
        selected = self.backends[model_entry(request.model,request.task)['backend']]
        # Preserve the one-resident-backend policy when switching runtimes.
        for backend in self.backends.values():
            if backend is not selected: backend.close()
        self.active = selected
        try: return self.active.execute(request,emit,canceled)
        finally: self.active = None
    def cancel(self):
        return self.active.cancel() if self.active else False
    def close(self):
        for backend in self.backends.values(): backend.close()
