# GeneretiCore 0.1.0 — early alpha

First Comfy Registry release. Optional local inference companion for Genereti
and ComfyUI. Includes native text/vision/decision interfaces, explicit verified
model downloads, preserved SDXS/SD Turbo generator IDs, compact Real-ESRGAN
upscaling, authored help and 15 teaching workflows.

Core ML image generation/upscaling requires macOS 14+ Apple silicon and optional
image dependencies. d1 requires macOS 15+ and a contributor-built helper;
experimental Core AI requires macOS 27+ and its contributor-built helper.
Native helpers and model weights are not bundled in this source release.
Install optional image dependencies using the active Comfy Python:
`python -m pip install -e '.[image]'` from the installed package directory.
Use explicit model downloads and start controls. Local compilation/loading may
be slow on first use. Do not enable the old genereti_comfy_coreml pack alongside
Core because it registers the same generator IDs.

Local validation: 40 Python tests, JS client/layout checks, synchronized help,
native upscaler parity, anonymous model installs, queued and live browser image
flows. This is not broad Manager installation or cross-platform inference
validation. Browser/ONNX providers, perception/segmentation and a Genereti
assistant provider are planned, not included. See browser-perception-plan.md.

Publishing is manual through comfy-registry.yml. Successful upload and Registry
processing status are distinct; do not claim Manager availability while pending.
