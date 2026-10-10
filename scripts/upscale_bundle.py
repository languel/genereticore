"""Prepare a public upscaler bundle from reviewed contributor exports."""
import argparse,hashlib,json,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('exports',type=Path);p.add_argument('destination',type=Path);args=p.parse_args()
root=Path(__file__).resolve().parents[1];dest=args.destination.resolve()
if root in (dest,*dest.parents):raise ValueError('Keep model bundles outside Git')
if dest.exists():raise ValueError('Choose a new staging directory')
dest.mkdir(parents=True)
shutil.copytree(args.exports/'upscalers',dest/'upscalers')
for name in ('LICENSE','sources.json','parity.json'):shutil.copyfile(args.exports/name,dest/name)
(dest/'README.md').write_text('''---
license: bsd-3-clause
library_name: coreml
tags: [image-to-image, super-resolution, coreml, genereticore]
---
# GeneretiCore compact Real-ESRGAN

Local macOS 14+ Apple silicon evaluation bundle. No hosted inference.
AnimeVideo-v3 and General-x4v3 by Xintao Wang and Real-ESRGAN contributors.
[Official source, credits and model downloads](https://github.com/xinntao/Real-ESRGAN).
BSD-3-Clause full terms are retained in LICENSE. Converted from official
v0.2.5.0 weights; source URLs, revisions and SHA-256 values are in sources.json.
Not a mirror of a third-party Core ML converter or binary.

Four fixed FP16-compute ML Program packages: upscalers/{animevideo,general}/{256,512}.mlpackage.
Inputs use float32 RGB NCHW in [0,1], padded on the right/bottom by reflection
up to 266 or 522 pixels. Outputs are float32 NCHW, 4x padded dimensions;
crop to 4x actual source size before output. No temporal model/state.
General is the ordinary general-x4v3 checkpoint; adjustable WDN interpolation
is not part of this bundle. 2x/source outputs downsample the 4x prediction.

Conversion: scripts/convert_upscalers.py in GeneretiCore with coremltools 8.3.0,
torch 2.5.1, macOS14 target, CPU + GPU. Contributor conversion stays outside Git.
Numerical comparison to PyTorch is recorded in parity.json; this does not
establish artistic fidelity, temporal stability or performance on other Macs.
Students use explicit anonymous checksum-verified downloads, without conversion.
Compiled models are created locally on first use. Model weights are not code.
''')
(dest/'Notice.txt').write_text('Real-ESRGAN: Copyright (c) 2021 Xintao Wang. BSD-3-Clause.\nSource: https://github.com/xinntao/Real-ESRGAN\nGeneretiCore fixed-size export and runtime; model behavior and upstream terms retained.\nNo endorsement by upstream authors is implied. Read LICENSE and sources.json.\n')
files=[]
for path in sorted(dest.rglob('*')):
 if path.is_file():files.append({'path':str(path.relative_to(dest)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
manifest={'format':1,'family':'esrgan','sizes':[256,512],'models':['animevideo','general'],'files':files}
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'download_bytes':sum(f['bytes'] for f in files),'manifest_sha256':hashlib.sha256((dest/'manifest.json').read_bytes()).hexdigest()}))
