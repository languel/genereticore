"""Anonymous metadata inspection only: no model download, login or inference.

python scripts/inspect_perception_candidates.py --output /tmp/perception-candidates.json
Metadata is evidence for research, not a production asset allowlist or license approval.
"""
import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request

REPOS = ('onnx-community/grounding-dino-tiny-ONNX', 'Xenova/slimsam-77-uniform',
         'facebook/sam3', 'facebook/dinov2-small')


def read(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode('utf-8')


def inspect():
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'anonymous upstream metadata; no weights or runtime validation', 'models': []}
    for repo in REPOS:
        url = 'https://huggingface.co/api/models/' + repo + '?blobs=true'
        data = json.loads(read(url))
        artifacts = []
        for entry in data.get('siblings', []):
            name = entry['rfilename']
            if not name.endswith(('.onnx', '.safetensors', '.json')):
                continue
            artifact = {'path': name, 'bytes': entry.get('size')}
            if entry.get('lfs', {}).get('sha256'):
                artifact['sha256'] = entry['lfs']['sha256']
            artifacts.append(artifact)
        report['models'].append({'repo': repo, 'revision': data['sha'], 'source': url,
                                 'gated': data.get('gated'),
                                 'declared_license': data.get('cardData', {}).get('license'),
                                 'artifacts': artifacts})
    # Inspect official Python declarations with AST; never execute upstream code.
    commit_url = 'https://api.github.com/repos/roboflow/rf-detr/commits/develop'
    revision = json.loads(read(commit_url))['sha']
    base = 'https://raw.githubusercontent.com/roboflow/rf-detr/' + revision + '/'
    path = 'src/rfdetr/assets/model_weights.py'
    source = read(base + path)
    weights = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id != 'ModelWeightAsset' or len(node.args) < 3:
            continue
        if not all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in node.args[:3]):
            continue
        name, url, digest = (a.value for a in node.args[:3])
        if name in ('rf-detr-nano.pth', 'rf-detr-seg-nano.pt'):
            weights.append({'path': name, 'url': url, 'upstream_md5': digest})
    report['rfdetr'] = {'revision': revision, 'branch': 'develop', 'weights_source': base + path,
                        'license_source': base + 'LICENSE', 'weights': weights,
                        'note': 'Develop snapshot; pin an installable release and add SHA-256 before conversion.'}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    data = json.dumps(inspect(), indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
        print('Saved anonymous metadata report to', args.output)
    else:
        print(data, end='')


if __name__ == '__main__':
    main()
