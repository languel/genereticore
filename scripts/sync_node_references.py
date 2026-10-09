"""Bundle authored native help for the shared Genereti Help catalog."""
import argparse
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
expected = json.dumps({p.stem:p.read_text() for p in sorted((root/'help/docs').glob('*.md'))}, ensure_ascii=False, indent=2) + '\n'
target = root/'web/node-references.json'
if args.check:
    if not target.exists() or target.read_text() != expected:
        raise SystemExit('References stale: run python scripts/sync_node_references.py')
else:
    target.write_text(expected)
# Comfy native Info discovers Markdown in the extension's web/docs directory.
for source in sorted((root/'help/docs').glob('*.md')):
    destination=root/'web/docs'/source.name
    if args.check:
        if not destination.exists() or destination.read_text()!=source.read_text():
            raise SystemExit('Native web docs stale: run python scripts/sync_node_references.py')
    else:
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(source.read_text())
