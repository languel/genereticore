# ꘅ SD Turbo generator

Remixes an image or follows Canny, depth or pose guidance using the migrated one-step Core ML engine. Stable ID: GeneretiSDTurboGenerate.

## Inputs, outputs and controls

Inputs: model_path, prompt, mode, seed, preprocess, strength, influence (control_scale), invert, movement and optional image. Outputs: image and metrics. Preprocess extracts Canny/depth; disable it for a prepared guide. Strength is image-remix noise (0.05–1), not guidance. Movement rotates seeded noise in Live; zero holds it.

## Small example

Open **10 - Livecode to SD Turbo** or **11 - Drawing to SD Turbo**. Choose a matching installed package and Canny mode, enable preprocessing, then press ▶. Use Queue plus Comfy Run for a single frame.

## Requirements and limits

macOS 14+ Apple silicon and preexisting packages required. Guide modes need control_<mode> and turbo_residual_unet beside encoder/decoder/base UNet. Depth preprocessing requires its separately cached pinned model. Pose accepts a prepared guide and starts no device. Preview freeze/minimize does not stop inference. Pause prevents new requests and drops stale completion; it cannot interrupt an already running Core ML call. Migration parity has not been tested on Mac.
