"""Prepare, upload, or install checksum-pinned local image bundles.

Contributor tool. Uses the Hugging Face SDK's existing login without reading or
printing credential values. Model assets and generated manifests stay outside Git.
"""
import argparse
import json
from pathlib import Path
import shutil

SOURCES = {
    'sdxs': ('IDKiro/sdxs-512-dreamshaper', '76f720262bb051da75666b22c902a78c8e16c763'),
    'sd-turbo': ('stabilityai/sd-turbo', 'b261bac6fd2cf515557d5d0707481eafa0485ec2'),
}

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from genereticore.image.bundles import digest, verify, install

def prepare(root, destination, family):
    from huggingface_hub import snapshot_download
    if destination.exists():
        raise FileExistsError(f'Refusing to replace existing bundle: {destination}')
    destination.mkdir(parents=True)
    names = ['unet', 'encoder', 'decoder'] + (['controlled_unet'] if family == 'sdxs' else ['turbo_unet'])
    for name in names:
        shutil.copytree(root / '512' / (name + '.mlpackage'), destination / '512' / (name + '.mlpackage'))
    sources = ['sdxs'] + (['sd-turbo'] if family == 'sd-turbo' else [])
    for name in sources:
        repo, revision = SOURCES[name]
        source = Path(snapshot_download(repo, revision=revision, local_files_only=True))
        for part in ['tokenizer', 'text_encoder']:
            shutil.copytree(source / part, destination / 'assets' / name / part)
        for notice in source.glob('*'):
            if notice.is_file() and (notice.name == 'README.md' or notice.name.startswith('LICENSE')):
                target = destination / 'notices' / name / notice.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(notice, target)
    if family == 'sdxs':
        sketch = Path(snapshot_download('IDKiro/sdxs-512-dreamshaper-sketch', revision='cd341678087336ed72c05660ac84d765896b48e7', local_files_only=True))
        target = destination / 'notices/sdxs-sketch';target.mkdir(parents=True)
        shutil.copyfile(sketch / 'README.md', target / 'README.md')
    modes = ['text', 'sketch'] if family == 'sdxs' else ['image']
    provenance = {'family': family, 'size': 512, 'modes': modes, 'sources': {name: dict(zip(['repo','revision'], SOURCES[name])) for name in sources},
        'status': 'private contributor staging; public redistribution audit pending',
        'conversion': 'Genereti archived fixed-shape FP16 converters; macOS14 target; coremltools8.3.0/torch2.5.1',
        'sketch_revision': 'cd341678087336ed72c05660ac84d765896b48e7' if family == 'sdxs' else None,
        'excluded': ['compiled caches','credentials','Canny/depth/pose weights','user media']}
    (destination / 'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    (destination / 'README.md').write_text(f'''---
license: other
tags: [coreml, apple-silicon, genereticore]
---
# GeneretiCore {family} · 512px · private staging

Complete local package for {', '.join(modes)} modes. Includes converted FP16
Core ML packages, tokenizer and text encoder. Requires macOS14+ Apple silicon.
Native compilation happens on first use; students do not convert PyTorch weights.
Tested on one macOS27 Apple silicon Mac; older OS versions remain untested.

This private staging release is not cleared for public redistribution. SDXS and
sketch upstream cards declare OpenRAIL++; SD Turbo retains its Stability AI
Community License. Tiny VAE originates in madebyollin/taesd (MIT). See notices
and provenance for original cards, exact upstream revisions and terms. These
components are not relicensed under the GeneretiCore code license. Converted
weights retain their upstream use restrictions. Changes: fixed 512px tensor
shapes, FP16 conversion and, for sketch, fused controller/denoiser.

Canny weights are excluded because their upstream licensing is ambiguous.
No cloud inference, captures, credentials or machine-specific compiler caches
are included. Manifest files record exact byte sizes and SHA-256 checksums.
''')
    files = [{'path': str(path.relative_to(destination)), 'bytes': path.stat().st_size, 'sha256': digest(path)}
             for path in sorted(destination.rglob('*')) if path.is_file()]
    manifest = {'format': 1, 'family': family, 'size': 512, 'modes': modes, 'files': files}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'bundle': str(destination), 'files': len(files), 'bytes': sum(f['bytes'] for f in files)}))

def upload(directory, repo, public=False):
    from huggingface_hub import HfApi
    verify(directory);api=HfApi()
    if not api.repo_info(repo).private and not public:
        raise ValueError('Public updates require explicit --public and retained licenses/notices')
    if public and not ((directory/'Notice.txt').is_file() and (directory/'notices/licenses/sources.json').is_file()):
        raise ValueError('Public bundles must retain credits and license sources')
    result=api.upload_folder(repo_id=repo, folder_path=directory, commit_message='Add verified 512px local image staging bundle')
    print(json.dumps({'repo': repo, 'revision': result.oid}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('prepare');p.add_argument('root',type=Path);p.add_argument('destination',type=Path);p.add_argument('--family',choices=list(SOURCES),required=True)
    p=sub.add_parser('upload');p.add_argument('directory',type=Path);p.add_argument('repo');p.add_argument('--public', action='store_true')
    p=sub.add_parser('install');p.add_argument('repo');p.add_argument('revision');p.add_argument('destination',type=Path)
    args=parser.parse_args()
    if args.action=='prepare':prepare(args.root,args.destination,args.family)
    elif args.action=='upload':upload(args.directory,args.repo,args.public)
    else:install(args.repo,args.revision,args.destination)
