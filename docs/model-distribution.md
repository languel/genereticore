# Student model downloads

The supported student path should be: install the extension, choose a compatible
model, click Download, then run locally. Students should not convert weights,
run conversion scripts or build Swift helpers with Xcode. This is the target in
[plan.md](plan.md), not a completed clean-install promise.

## What works today

The text/vision/decision catalog points to pinned upstream Hugging Face packages.
Explicit downloads verify the manifest's sizes and SHA-256 checksums and store
assets outside Git. Qwen Core AI packages require Apple silicon and macOS 27;
the text-only d1 Core ML package targets Apple silicon and macOS 15+. The older
macOS target still needs testing. The native helpers currently need a contributor
build; distributing a supported helper binary remains release work.

d1 is already converted upstream at
[FluidInference/d1-omni-600m-coreml](https://huggingface.co/FluidInference/d1-omni-600m-coreml).
Its first local run compiles the downloaded Core ML package and caches the result.
That automatic on-device compilation is different from converting PyTorch weights.
No separate Genereti hosting is needed for the existing upstream catalog entries.

SDXS and SD Turbo now have complete **private contributor bundles** on Hugging
Face: [SDXS](https://huggingface.co/liuboto/genereticore-sdxs-coreml) and
[SD Turbo](https://huggingface.co/liuboto/genereticore-sd-turbo-coreml). Both include
512px converted Core ML packages, tokenizer and text encoder. SDXS supports text
and sketch; Turbo supports image-to-image. The repositories do not run inference.
No Space or hosted endpoint is needed. Each bundle contains provenance, upstream
notices and a byte-size/SHA-256 manifest. Pinned releases are recorded in
[image-bundles.json](image-bundles.json).

Use a Python environment with `huggingface-hub==0.36.2` and an existing SDK login
that can read these private repositories. From this checkout, install both into
Comfy's model directory (substitute your actual Comfy path):

```sh
python scripts/image_bundle.py install liuboto/genereticore-sdxs-coreml c33a8705b08d5ebc30b7274da731f5ed3771fd7f /path/to/ComfyUI/models/genereticore/images
python scripts/image_bundle.py install liuboto/genereticore-sd-turbo-coreml 7f6fae19e26d8194d9a1867f55b6c7d95b0d92db /path/to/ComfyUI/models/genereticore/images
```

The installer validates the entire download before copying and refuses conflicting
existing files. Repeating the command reuses byte-identical files and the SDK's
download cache. Downloads are about 2.14GB and 3.55GB respectively; some assets
are shared in the installed root. Keep adequate space for downloads, installation
and first-run compiler caches. Choose `512/unet.mlpackage` or
`512/turbo_unet.mlpackage` in the generator. Students **do not convert weights**;
first use compiles native packages locally and subsequent runs reuse that cache.
No token belongs in a workflow, source file or command argument.

Public redistribution clearance and an image-node Download button remain release
work. SDXS/sketch upstream cards declare OpenRAIL++; Turbo includes its upstream
Stability AI Community License. The Tiny VAE and all transitive dependencies need
a complete notice audit before public publication. Canny weights were converted
and tested locally but are excluded from hosting because the upstream terms are
ambiguous. Turbo samples now default to image mode so they match the hosted bundle.
See [realtime-image-demo.md](realtime-image-demo.md) for optional control packages.
Native inference requires macOS 14+ Apple silicon; older supported OS versions
have not been tested on this machine.

## Distribution work next

1. Extend the verified private 512px SDXS/Turbo bundles only after any added modes
   have complete dependencies, license clearance and local tests.
2. Audit every component's redistribution terms and retain licenses, notices,
   upstream revisions, conversion recipe, supported sizes and local measurements.
3. After license clearance, publish our converted bundles in versioned Hugging Face **model repositories**.
   An organization is useful for shared ownership but not mandatory. These are
   downloadable files used for local inference; a Space or hosted inference
   endpoint is unnecessary. Hugging Face supports custom package files:
   [upload documentation](https://huggingface.co/docs/hub/models-uploading).
4. Add pinned bundle manifests and explicit image-node Download controls, with
   progress, useful missing-component errors and recovery after interruption.
   Cache compilation on the student's machine rather than shipping one machine's
   compiler cache as universally portable.
5. Package supported native helper binaries and verify installation, download,
   first compilation, warm inference and restart on a clean student installation.

If a component requires upstream access approval, make that requirement visible
instead of embedding credentials or bypassing it through a mirror. All inference
stays local; downloading a model does not upload student drawings or prompts.
