# ꘅ SD Turbo generator

Remixes an image or follows Canny, depth or pose guidance using the migrated one-step Core ML engine. Stable ID: GeneretiSDTurboGenerate.

## Inputs, outputs and controls

Inputs: model_path, prompt, mode, seed, preprocess, strength, influence (control_scale), invert, movement and optional image. Outputs: image and metrics. Preprocess extracts Canny/depth; disable it for a prepared guide. Strength is image-remix noise (0.05–1), not guidance. Movement rotates seeded noise in Live; zero holds it.

## Small example

Open **11 - Livecode to SD Turbo** or **12 - Drawing to SD Turbo**. Use ↓ to download the public 256px + 512px bundle, choose image mode and strength 0.95, then press ▶. Optional Canny needs separately sourced control weights. Use Queue plus Comfy Run for a single frame.

## Requirements and limits

macOS 14+ Apple silicon and optional image dependencies required. ↓ explicitly downloads the verified public bundle; no HF login or conversion is needed. Guide modes need control_<mode> and turbo_residual_unet beside encoder/decoder/base UNet. Depth preprocessing requires its separately cached pinned model. Pose accepts a prepared guide and starts no device. Preview freeze/minimize does not stop inference. Pause prevents new requests and drops stale completion; it cannot interrupt an already running Core ML call. 512px image and Canny were tested locally on one Mac; broader parity and older OS validation remain pending. Powered by Stability AI; upstream use terms apply.

## Blank input during performance

Enable **Blank input** to use a second prompt when the connected image is a uniform background. The chevron shows or hides its field; collapsing does not disable the option. It starts disabled and is saved with the workflow. This works in Live and Comfy Queue. Detection happens before guide preprocessing or inversion and requires every pixel to be nearly the same color; even a small contrasting mark keeps the normal prompt. Text mode has no image to check.

Choose **Alternate prompt** to generate an empty scene (the default is “closeup flat white blank paper space pristine smooth emptiness”). Models may still invent shadows or texture. Choose **Solid white** for an exact white frame without inference while the input is blank. Drawing again automatically resumes the main prompt. The main prompt and held draft remain unchanged.

The bottom color dot shows the current state in its hover tip. Clicking it hides or shows the timings beside it. Timings are rounded averages updated once a second; errors remain visible.

## Credits and licenses

[Published bundle, upstream credits and complete license notices](https://huggingface.co/languel/genereticore-sd-turbo-coreml/blob/fd78b21b29cec891fb09d87c76233ddb44c6edb3/Notice.txt). SD Turbo by Stability AI; TAESD by madebyollin; CLIP and OpenCLIP contributors. Powered by Stability AI. The bundle preserves upstream license notices and source backlinks.

## Native sizes

Choose `256/unet.mlpackage` (SDXS) or `256/turbo_unet.mlpackage` (Turbo) for the faster 256px version. The corresponding `512/` path keeps 512px. Both use the same node; the explicit bundle download installs both size folders and shared text assets. 256px reuses the original 512-trained weights with smaller fixed shapes, so appearance can differ. Both resolutions were exercised on this Mac.

Live timings: Total includes input capture, the local request, inference, image decoding and publication. The FPS estimate is 1000 divided by average Total milliseconds; the delay between requests and screen refresh are excluded. Model measures the native pipeline, including prompt encoding and image decoding. Values are averaged and refreshed once per second.
