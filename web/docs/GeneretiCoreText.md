# ꘅ Local Text

Writes text from a prompt using local Qwen3 0.6B.

## Inputs, outputs and controls

Inputs: model, prompt, max_tokens (generation budget), temperature (sampling randomness, 0–2). Outputs: text and metrics (JSON timings). ↓ explicitly downloads pinned artifacts; ▷ queues the connected workflow; ϟ previews here only; □ cancels an active local preview/download.

## Small example

Use “Describe a playful generative art scene in one sentence. /no_think”. Connect text to ꘅ Text / JSON Viewer and press Comfy Run.

## Requirements and limits

Requires the macOS 27+ Core AI helper. Small models can be incorrect. The preview button does not update wires. Cancel only targets this node’s separate preview request, not a queued Comfy Run.
