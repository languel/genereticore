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

SDXS and SD Turbo now have complete **public evaluation bundles** on Hugging
Face: [SDXS](https://huggingface.co/languel/genereticore-sdxs-coreml) and
[SD Turbo](https://huggingface.co/languel/genereticore-sd-turbo-coreml). Both include
256px and 512px converted Core ML packages, tokenizer and text encoder. SDXS supports text
and sketch; Turbo supports image-to-image. The repositories do not run inference.
No Space or hosted endpoint is needed. Each bundle contains provenance, upstream
notices and a byte-size/SHA-256 manifest. Pinned releases are recorded in
[image-bundles.json](image-bundles.json).

Students can use the generator toolbar’s **↓ Download** action. It downloads the
matching 512px family, shows download/verification/install status, checks bytes and
SHA-256, retains licenses and refuses conflicting files. Workflow loading does not
start a download or inference. Press **▶ Start** after installation. **ⓘ** opens
credits, original sources and terms. No Hugging Face account or token is needed.

For contributor command-line setup, use a Python environment with
`huggingface-hub==0.36.2` (the existing Comfy Hub 1.30 also passed the download test). From this checkout, install both into
Comfy's model directory (substitute your actual Comfy path):

```sh
python scripts/image_bundle.py install languel/genereticore-sdxs-coreml 86f20169b7f8d1855994ae9b98ab0b28557c7efe /path/to/ComfyUI/models/genereticore/images
python scripts/image_bundle.py install languel/genereticore-sd-turbo-coreml fd78b21b29cec891fb09d87c76233ddb44c6edb3 /path/to/ComfyUI/models/genereticore/images
```

The installer validates the entire download before copying and refuses conflicting
existing files. Repeating the command reuses byte-identical files and the SDK's
download cache. Downloads are about 3.78GB and 5.92GB respectively; some assets
are shared in the installed root. Keep adequate space for downloads, installation
and first-run compiler caches. Choose `512/unet.mlpackage` or
`512/turbo_unet.mlpackage` in the generator. Students **do not convert weights**;
first use compiles native packages locally and subsequent runs reuse that cache.
No token belongs in a workflow, source file or command argument.

The published bundles retain upstream model cards, full license reference copies,
credits, backlinks and modification notices. See [image-license-review.md](image-license-review.md)
for the source-by-source review and retained restrictions. **Powered by Stability AI**:
Turbo retains its Community License, including its commercial-use conditions.
Canny is available in the local contributor test but is not mirrored because its
upstream terms are unclear. The license review links the original source and
conversion recipe; SDXS sketch and Turbo image work without that component.

Native inference requires macOS 14+ Apple silicon. Older supported OS versions and
broad clean Manager installations remain untested. First compilation and the model
cache need extra disk space beyond the download sizes.

## Distribution work next

1. Extend the verified public 512px SDXS/Turbo bundles only after any added modes
   have complete dependencies, license clearance and local tests.
2. Audit every component's redistribution terms and retain licenses, notices,
   upstream revisions, conversion recipe, supported sizes and local measurements.
3. Keep permitted converted bundles public in versioned Hugging Face **model repositories**.
   An organization is useful for shared ownership but not mandatory. These are
   downloadable files used for local inference; a Space or hosted inference
   endpoint is unnecessary. Hugging Face supports custom package files:
   [upload documentation](https://huggingface.co/docs/hub/models-uploading).
4. Keep download manifests revision-pinned and verify interrupted-download recovery
   on a separate student machine. The image-node Download control is now implemented.
   Cache compilation on the student's machine rather than shipping one machine's
   compiler cache as universally portable.
5. Package supported native helper binaries and verify installation, download,
   first compilation, warm inference and restart on a clean student installation.

If a component requires upstream access approval, make that requirement visible
instead of embedding credentials or bypassing it through a mirror. All inference
stays local; downloading a model does not upload student drawings or prompts.

Local publisher setup and account switching: [hugging-face-publishing.md](hugging-face-publishing.md). Choose resolution with the existing generator model path; no separate Comfy nodes are needed.
