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

SDXS and SD Turbo currently expect existing converted packages and locally cached
tokenizer/text-encoder assets. They have no complete bundle download control yet.
See [realtime-image-demo.md](realtime-image-demo.md) for the exact current contract.
The image runtime requires macOS 14+ Apple silicon; that is a platform requirement,
not confirmation of inference on every supported OS.

## Distribution work next

1. Prepare and test one complete SDXS bundle, including all dependencies needed by
   its shipped sample. Include tokenizer/text encoder assets in the download
   contract; a UNet package alone is insufficient. Add Turbo and optional controls
   only after their complete bundles are tested.
2. Audit every component's redistribution terms and retain licenses, notices,
   upstream revisions, conversion recipe, supported sizes and local measurements.
3. Publish our converted bundles in versioned Hugging Face **model repositories**.
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
