"""Contributor-only: pin exact upstream file sizes and SHA-256; never downloads weights."""
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
path = root / 'genereticore/catalog.json'
catalog = json.loads(path.read_text())
for model in catalog['models']:
    files = []
    for subtree in model['paths']:
        url = f"https://huggingface.co/api/models/{model['repo']}/tree/{model['revision']}/{quote(subtree, safe='/')}?recursive=true&expand=false"
        while url:
            with urlopen(url, timeout=30) as response:
                entries = json.load(response)
                links = response.headers.get('Link', '')
            url = None
            for link in links.split(','):
                if 'rel="next"' in link:
                    url = link.split('<')[1].split('>')[0]
            for entry in entries:
                if entry['type'] != 'file':
                    continue
                if entry.get('lfs'):
                    digest = entry['lfs']['oid']
                else:
                    if entry['size'] > 10_000_000:
                        raise RuntimeError('Refusing un-hashed large non-LFS artifact')
                    source = f"https://huggingface.co/{model['repo']}/resolve/{model['revision']}/{quote(entry['path'], safe='/')}"
                    with urlopen(source, timeout=30) as response:
                        digest = hashlib.sha256(response.read()).hexdigest()
                files.append({'path': entry['path'], 'bytes': entry['size'], 'sha256': digest})
    model['files'] = sorted(files, key=lambda f: f['path'])
    model['bytes'] = sum(f['bytes'] for f in files)
    print(model['id'], len(files), model['bytes'])
path.write_text(json.dumps(catalog, indent=2) + '\n')
