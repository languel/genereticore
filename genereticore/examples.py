"""Install teaching workflows into Comfy profiles, preserving customized copies."""
import hashlib
import json
import logging
from pathlib import Path
import shutil
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install(examples, workflows):
    examples, workflows = Path(examples), Path(workflows)
    destination = workflows / 'GeneretiCore'
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = workflows.parent / '.genereticore-workflows.json'
    try:
        manifest = json.loads(manifest_path.read_text())
        if not isinstance(manifest, dict): manifest = {}
    except (OSError, ValueError):
        manifest = {}
    for source in sorted(examples.glob('*.json')):
        target = destination / source.name
        if target.exists():
            current = digest(target)
            if current == digest(source):
                manifest[source.name] = current
                continue
            if current != manifest.get(source.name):
                continue  # An authored or edited workflow is never overwritten.
            backup = workflows.parent / '.genereticore-workflow-backups' / current / source.name
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists(): shutil.copy2(target, backup)
        with tempfile.NamedTemporaryFile(dir=destination, delete=False) as staged:
            staged.write(source.read_bytes())
            temporary = Path(staged.name)
        temporary.replace(target)
        manifest[source.name] = digest(target)
    names = {p.name for p in examples.glob('*.json')}
    for name, checksum in list(manifest.items()):
        if not isinstance(name, str) or Path(name).name != name or not name.endswith('.json'):
            continue
        target = destination / name
        if name not in names and target.is_file() and digest(target) == checksum:
            backup = workflows.parent / '.genereticore-workflow-backups' / checksum / name
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists(): shutil.copy2(target, backup)
            target.unlink()  # Only unchanged managed samples; recoverable from the backup.
            manifest.pop(name, None)
    with tempfile.NamedTemporaryFile(mode='w', dir=manifest_path.parent, delete=False) as staged:
        json.dump(manifest, staged, indent=2)
        staged.write('\n')
        temporary = Path(staged.name)
    temporary.replace(manifest_path)
    return destination


def install_for_profiles(root):
    import folder_paths
    from server import PromptServer
    users = PromptServer.instance.user_manager.users
    for user_id in users:
        profile = folder_paths.get_public_user_directory(user_id)
        if profile:
            try:
                install(Path(root) / 'example_workflows', Path(profile) / 'workflows')
            except (OSError, ValueError) as error:
                logging.warning('GeneretiCore examples could not be installed: %s. Open example_workflows manually.', error)
