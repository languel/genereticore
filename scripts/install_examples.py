"""Install bundled samples in an explicitly selected Comfy profile's workflow directory."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from genereticore.examples import install
parser = argparse.ArgumentParser()
parser.add_argument('workflows', help='Comfy user/default/workflows directory')
args = parser.parse_args()
print(install(Path(__file__).resolve().parents[1] / 'example_workflows', args.workflows))
