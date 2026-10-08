"""Contributor build; never invoked automatically by Comfy or an inference node."""
from pathlib import Path
import platform
import os
import tempfile
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
if platform.system() != "Darwin" or platform.machine() != "arm64" or int(platform.mac_ver()[0].split('.')[0]) < 27:
    raise SystemExit("Requires macOS 27+ Apple silicon and Xcode 27")
subprocess.run(["swift", "build", "-c", "release", "--package-path", str(root / "native")], check=True)
bin_path = subprocess.check_output(["swift", "build", "-c", "release", "--package-path", str(root / "native"), "--show-bin-path"], text=True).strip()
destination = root / "native/bin/genereticore-helper"
destination.parent.mkdir(parents=True, exist_ok=True)
# Never overwrite the inode of a mapped signed Mach-O. macOS caches its signature.
with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as temporary:
    staged = Path(temporary.name)
try:
    shutil.copy2(Path(bin_path) / "genereticore-helper", staged)
    subprocess.run(["codesign", "--verify", str(staged)], check=True)
    os.replace(staged, destination)
finally:
    staged.unlink(missing_ok=True)
print(f"Built {destination}")
