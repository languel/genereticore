"""Copy public image repos to an authenticated destination account.

Never reads credential values. Sources are preserved; retirement is separate.
Uses a recent huggingface_hub SDK with model-repository duplication support.
"""
import argparse
import hashlib
import json
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd


def migrate(source_owner, target_owner, output):
    api = HfApi()
    if api.whoami().get('name') != target_owner:
        raise RuntimeError(f'Run hf auth login --force as {target_owner} first')
    entries = []
    for family in ('sdxs', 'sd-turbo'):
        name = f'genereticore-{family}-coreml'
        source, target = f'{source_owner}/{name}', f'{target_owner}/{name}'
        original = api.repo_info(source)
        if original.private:
            raise ValueError('Migration expects the reviewed public release')
        repo = api.duplicate_repo(source, target, repo_type='model', private=False)
        copied = api.repo_info(target)
        source_files = set(api.list_repo_files(source, revision=original.sha))
        if set(api.list_repo_files(target, revision=copied.sha)) != source_files:
            raise ValueError('Destination file inventory differs')
        original_manifest = Path(hf_hub_download(source, 'manifest.json', revision=original.sha, token=False)).read_bytes()
        copied_manifest = Path(hf_hub_download(target, 'manifest.json', revision=copied.sha, token=False)).read_bytes()
        if original_manifest != copied_manifest:
            raise ValueError('Destination manifest differs')
        manifest = json.loads(copied_manifest)
        readme = Path(hf_hub_download(target, 'README.md', revision=copied.sha, token=False)).read_text().replace(source, target).encode()
        for item in manifest['files']:
            if item['path'] == 'README.md':
                item.update(bytes=len(readme), sha256=hashlib.sha256(readme).hexdigest())
        manifest_bytes = (json.dumps(manifest, indent=2)+'\n').encode()
        commit = api.create_commit(target, operations=[
            CommitOperationAdd(path_in_repo='README.md', path_or_fileobj=readme),
            CommitOperationAdd(path_in_repo='manifest.json', path_or_fileobj=manifest_bytes)],
            commit_message='Use languel publisher links and refresh checksums', parent_commit=copied.sha)
        entries.append(dict(family=family, repo=target, revision=commit.oid, private=False,
            size=512, sizes=[256,512], modes=manifest['modes'],
            download_bytes=sum(item['bytes'] for item in manifest['files']),
            manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
            status='public evaluation bundle; upstream use terms retained'))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({'format':1,'bundles':entries}, indent=2)+'\n')
        print(f'Copied {source} to {target} at {commit.oid}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-owner', default='liuboto')
    parser.add_argument('--to-owner', default='languel')
    parser.add_argument('--output', type=Path, required=True, help='External provisional catalog; verify before publishing')
    args = parser.parse_args()
    migrate(args.from_owner, args.to_owner, args.output)
