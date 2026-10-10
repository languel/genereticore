# ꘅ SD Turbo generator

Remixes an image or follows Canny, depth or pose guidance using the migrated one-step Core ML engine. Stable ID: GeneretiSDTurboGenerate.

## Inputs, outputs and controls

Inputs: model_path, prompt, mode, seed, preprocess, strength, influence (control_scale), invert, movement and optional image. Outputs: image and metrics. Preprocess extracts Canny/depth; disable it for a prepared guide. Strength is image-remix noise (0.05–1), not guidance. Movement rotates seeded noise in Live; zero holds it.

## Small example

Open **11 - Livecode to SD Turbo** or **12 - Drawing to SD Turbo**. Use ↓ to download the public 512px bundle, choose image mode and strength 0.95, then press ▶. Optional Canny needs separately sourced control weights. Use Queue plus Comfy Run for a single frame.

## Requirements and limits

macOS 14+ Apple silicon and optional image dependencies required. ↓ explicitly downloads the verified public bundle; no HF login or conversion is needed. ⓘ links credits, sources and license terms. Guide modes need control_<mode> and turbo_residual_unet beside encoder/decoder/base UNet. Depth preprocessing requires its separately cached pinned model. Pose accepts a prepared guide and starts no device. Preview freeze/minimize does not stop inference. Pause prevents new requests and drops stale completion; it cannot interrupt an already running Core ML call. 512px image and Canny were tested locally on one Mac; broader parity and older OS validation remain pending. Powered by Stability AI; upstream use terms apply.
