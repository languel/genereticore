# ꘅ SDXS generator

Generates images locally from text or a sketch with the migrated one-step Core ML engine. The node ID stays GeneretiSDXSGenerate for saved graphs.

## Inputs, outputs and controls

Inputs: model_path, prompt, mode (text/sketch), seed, influence (control_scale), invert, movement and optional image. Outputs: image and metrics. Model path sets native size and base/anime variant. Live/Comfy Queue chooses delivery; ▶ starts inference, Ⅱ pauses it. Prompt ϟ applies while typing; ↑ or Cmd/Ctrl+Enter commits a held draft.

## Small example

Open **09 - Livecode to SDXS** or **10 - Drawing to SDXS**. Use ↓ to download the public 256px + 512px bundle, leave sketch selected, then press ▶. A connected ꘇ image preview holds the latest completed frame while the next computes.

## Requirements and limits

macOS 14+ Apple silicon and optional image dependencies are required. ↓ explicitly downloads the verified public bundle; no HF login or conversion is needed. Sketch needs controlled_unet; anime needs its own controlled package. Only the first queued IMAGE is used; alpha composites on white. In-flight native work completes after pause; stale results are discarded. Live inference is loopback-only, bounded to one request at a time. No cloud fallback or model downloads on workflow load. 512px text/sketch and the live bridge were tested locally on one Mac; broader parity and older OS validation remain pending.

## Blank input during performance

Enable **Blank input** to use a second prompt when the connected image is a uniform background. The chevron shows or hides its field; collapsing does not disable the option. It starts disabled and is saved with the workflow. This works in Live and Comfy Queue. Detection happens before guide preprocessing or inversion and requires every pixel to be nearly the same color; even a small contrasting mark keeps the normal prompt. Text mode has no image to check.

Choose **Alternate prompt** to generate an empty scene (the default is “closeup flat white blank paper space pristine smooth emptiness”). Models may still invent shadows or texture. Choose **Solid white** for an exact white frame without inference while the input is blank. Drawing again automatically resumes the main prompt. The main prompt and held draft remain unchanged.

The bottom color dot shows the current state in its hover tip. Clicking it hides or shows the timings beside it. Timings are rounded averages updated once a second; errors remain visible.

## Credits and licenses

[Published bundle, upstream credits and complete license notices](https://huggingface.co/languel/genereticore-sdxs-coreml/blob/86f20169b7f8d1855994ae9b98ab0b28557c7efe/Notice.txt). SDXS by IDKiro; teacher Stable Diffusion 2.1 by Stability AI; TAESD by madebyollin; CLIP and OpenCLIP contributors. The bundle preserves upstream license notices and source backlinks.

## Native sizes

Choose `256/unet.mlpackage` (SDXS) or `256/turbo_unet.mlpackage` (Turbo) for the faster 256px version. The corresponding `512/` path keeps 512px. Both use the same node; the explicit bundle download installs both size folders and shared text assets. 256px reuses the original 512-trained weights with smaller fixed shapes, so appearance can differ. Both resolutions were exercised on this Mac.
