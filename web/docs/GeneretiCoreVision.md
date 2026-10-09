# ꘅ Local Vision

Describes one supplied image using local Qwen3-VL 2B.

## Inputs, outputs and controls

Inputs: model, image (IMAGE), prompt, max_tokens. Outputs: text and metrics. ↓ downloads the pinned model; ▷ runs the connected graph. This node has no separate image preview inference button.

## Small example

Connect ꘇ livecode image to image, ask “Describe the image briefly”, connect text to the viewer and press Run. Rendering continues independently of analysis.

## Requirements and limits

macOS 27+ Core AI helper required. One image per observation; batches are rejected. The image is resized to at most 1024 pixels per side. This is queued analysis, not continuous per-frame inference.
