# ꘅ SDXS generator

Generates images locally from text or a sketch with the migrated one-step Core ML engine. The node ID stays GeneretiSDXSGenerate for saved graphs.

## Inputs, outputs and controls

Inputs: model_path, prompt, mode (text/sketch), seed, influence (control_scale), invert, movement and optional image. Outputs: image and metrics. Model path sets native size and base/anime variant. Live/Comfy Queue chooses delivery; ▶ starts inference, Ⅱ pauses it. Prompt ϟ applies while typing; ↑ or Cmd/Ctrl+Enter commits a held draft.

## Small example

Open **09 - Livecode to SDXS** or **10 - Drawing to SDXS**. Choose an installed package, leave sketch selected, then press ▶. A connected ꘇ image preview holds the latest completed frame while the next computes.

## Requirements and limits

macOS 14+ Apple silicon and preexisting converted model bundles are required. Sketch needs controlled_unet; anime needs its own controlled package. Only the first queued IMAGE is used; alpha composites on white. In-flight native work completes after pause; stale results are discarded. Live inference is loopback-only, bounded to one request at a time. No cloud fallback or model downloads on workflow load. Local parity after migration remains unverified.
