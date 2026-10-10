# ꘅ Real-ESRGAN upscale

Clean and enlarge low-resolution images locally with compact AnimeVideo or General Real-ESRGAN models. Try AnimeVideo for smooth graphic edges, and General for textured images; compare both on your source.

## Inputs, outputs and controls

IMAGE input; IMAGE output and JSON metrics. **model** chooses AnimeVideo or General. **scale** selects source-size cleanup, 2x or 4x output. Both models predict 4x internally; smaller output sizes use Lanczos downsampling. **passes** selects one prediction or two-pass same-image refinement. **feedback** blends the downsampled first result with the original before the second prediction (0 keeps the original; 1 uses the first result). It has no effect with one pass and stores no previous-frame history.

## Small example

Open **14 - Real-ESRGAN cleanup comparison**. Use each node's ↓ to download SDXS and the upscalers, then explicitly start SDXS and upscale with ▶. Compare the original 256px frame with the cleaned 512px frame. The dot toggles timings and shows state in its hover tip. Ⅱ pauses new processing and holds the last completed output. Models never start or download on workflow load.

For one queued frame, pause both inference nodes, choose Comfy Queue delivery on the source, generator and upscaler, then use Comfy Run. Queued metrics include load/wait, inference and total time. Live Total includes the local request, model, PNG encoding and browser decoding; FPS estimates 1000 / average Total and is not measured screen FPS.

## Requirements and limits

macOS 14+ Apple silicon, optional image dependencies and the Genereti companion for live delivery. ↓ installs both 256px and 512px model packages from the pinned public bundle. No student HF login or conversion is needed. Inputs must be 2–512px per side, including non-square images; larger input needs an explicit resize upstream. The appropriate package is selected automatically. Alpha composites on white. Queued batches are limited to four images. Live inputs require a bitmap IMAGE source; GPU-only textures need a conversion before this node.

Only one live native request runs at a time across generators and upscalers. Waiting frames are replaced by the newest input. Pause lets an active native call finish and discards its stale output. First use can compile/load the model and take noticeably longer. Two passes cost another prediction. No cloud inference fallback.

## Credits and licenses

[Public bundle, conversion provenance and complete notices](https://huggingface.co/languel/genereticore-upscalers-coreml). Real-ESRGAN by Xintao Wang and contributors, [official source](https://github.com/xinntao/Real-ESRGAN) and [official weights](https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.5.0). BSD 3-Clause notices are retained. These are independently converted compact SRVGG models, not the much larger RRDB RealESRGAN_x4plus. General uses its ordinary weights; the optional upstream WDN interpolation is not included.
