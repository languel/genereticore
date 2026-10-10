"""Check release metadata and tracked assets without accessing credentials."""
import json
from pathlib import Path
import subprocess
import tomllib

root = Path(__file__).resolve().parents[1]
meta = tomllib.loads((root / 'pyproject.toml').read_text())
assert meta['project']['name'] == 'genereticore'
assert meta['project']['version'] == '0.1.0'
assert meta['project']['urls']['Repository'] == 'https://github.com/languel/genereticore'
assert meta['tool']['comfy']['PublisherId'] == 'liuboto'
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
for name in filter(None, tracked):
    path = Path(name)
    assert not any(p in {'models', 'captures', 'cache', 'artifacts', '.venv', 'bin'} for p in path.parts), name
    assert not name.startswith('.env'), name
    assert path.suffix not in {'.pth', '.pt', '.safetensors', '.gguf', '.onnx', '.mlmodel'}, name
    assert not any(p.endswith(('.mlpackage', '.mlmodelc', '.aimodel', '.aimodelc')) for p in path.parts), name
    assert not (root / path).is_symlink(), name
for required in ['__init__.py', 'genereticore/upscale/nodes.py', 'genereticore/upscale/runtime.py',
                 'web/js/upscale.js', 'web/node-references.json', 'licensing/Real-ESRGAN-LICENSE.txt',
                 'native/Package.resolved', 'native/d1/Sources/GeneretiD1Helper/Upstream/LICENSE']:
    assert required in tracked, required
assert json.loads((root / 'docs/image-bundles.json').read_text()) == json.loads((root / 'genereticore/image/bundles.json').read_text())
print(f"Release {meta['project']['version']}: {len(list(filter(None, tracked)))} tracked source files; no model/cache/credential payloads")
