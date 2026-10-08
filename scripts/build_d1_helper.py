"""Explicit contributor build of the macOS 15+ Core ML decision helper."""
from pathlib import Path
import os
import platform
import shutil
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
if platform.system() != 'Darwin' or platform.machine() != 'arm64' or int(platform.mac_ver()[0].split('.')[0]) < 15:
    raise SystemExit('Requires macOS 15+ Apple silicon and a Swift 6 toolchain')
package = root / 'native/d1'
subprocess.run(['swift','build','-c','release','--package-path',str(package)],check=True)
bin_path = subprocess.check_output(['swift','build','-c','release','--package-path',str(package),'--show-bin-path'],text=True).strip()
destination = root / 'native/bin/genereticore-d1-helper'
destination.parent.mkdir(parents=True,exist_ok=True)
with tempfile.NamedTemporaryFile(dir=destination.parent,delete=False) as temporary:
    staged = Path(temporary.name)
try:
    shutil.copy2(Path(bin_path) / destination.name,staged)
    subprocess.run(['codesign','--verify',str(staged)],check=True)
    os.replace(staged,destination)
finally:
    staged.unlink(missing_ok=True)
print(f'Built {destination}')
