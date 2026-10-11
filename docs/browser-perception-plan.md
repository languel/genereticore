# Optional browser models and realtime perception

Agreed direction, October 10, 2026. Browser providers, perception nodes and the pumpkin workflow remain planned.
The first ONNX browser upscaler milestone is documented in browser-onnx.md;
it is not included in the previously published 0.1.0 Registry archive.

Genereti stays a lightweight realtime framework and owns the assistant UI,
workspace tools, review/apply/undo, thresholds, smoothing, event routing,
palette controls and prompt connections. GeneretiCore owns optional model
catalogs, downloads, license/provenance records and execution, whether native
Core ML/Core AI or browser inference. MediaPipe also needs model assets: its
interactive controls can belong in Genereti while optional asset management
and provider integration live in Core. Keep core Genereti demos model-free.

## Preferred runtime order

1. Transformers.js for supported vision analysis, embeddings, speech and text
   pipelines; WebGPU acceleration or an explicitly supported WASM CPU path.
2. ONNX Runtime Web directly for custom image pipelines such as our compact
   Real-ESRGAN and segmentation, with controlled preprocessing/postprocessing.
3. MediaPipe Tasks for specialized hands/pose/face/segmentation workflows.
4. Evaluate WebLLM for assistant chat after a browser provider seam works. Its
   OpenAI-style interface is useful, but MLC adds another model export/runtime.
5. Preserve native Core ML/Core AI options and truthful platform availability.

ONNX is a model format, Transformers.js is a higher-level pipeline library,
and WebGPU/WASM are execution technologies. A Core ML export does not become
browser-compatible by changing its suffix. Pin and validate each export.

Sources: https://huggingface.co/docs/transformers.js/index,
https://onnxruntime.ai/docs/tutorials/web/ep-webgpu.html,
https://webllm.mlc.ai/docs/index.html,
https://developers.google.com/edge/mediapipe/solutions/vision/image_segmenter/web_js.

## Shared outputs and example

Perception → decision → action is the priority; the assistant is one consumer.
Object detection returns labels/confidence/boxes; segmentation returns masks;
vision analysis returns captions or structured observations; decision returns
a choice/score/structured controls. Include source revision, timestamp, result
age, model/backend and processing timings. Consumers must reject stale results.

First complete demo: camera/image → detect pumpkin → stable presence threshold
→ select Halloween palette and, on entry, send a jack-o-lantern prompt to a
generator. Use a deterministic rule first, with optional decision-model
interpretation alongside it. A simple detection rule does not require an LLM.
Segmentation can restrict effects to the object; slower vision analysis can
suggest richer prompts. Do not send the prompt again on every detected frame.

Render continuously; process the newest waiting frame with a bounded queue.
Run heavy analysis less often or on scene change. Add confidence thresholds,
stable-presence duration, entry/exit events and cooldowns. Hold the latest valid
result with visible age; reset history on source/dimension/scene changes. Run
inference in workers and measure GPU contention alongside creative rendering:
workers protect the UI thread but do not isolate GPU resources. Explicit
load/start/stop/unload, memory budgets and device-loss recovery are required.

## Genereti assistant provider seam

Expose one optional GeneretiCore provider with model discovery, capabilities,
load, streamed requests, cancellation and disposal. Keep tool execution and
reviewed actions in Genereti. Native adapters call Core's local backend; browser
adapters call a worker. The current assistant forwards model requests through
Python to HTTP model servers, so adding a server URL alone cannot implement a
browser provider. Browser execution happens on the viewer's device and requires
an active browser; do not represent it as an always-running headless server.

## Models and distribution

Prioritize object detection, segmentation and structured vision analysis, then
decision integration. ONNX Real-ESRGAN offers a directly comparable existing
native/browser experiment. Quantized Qwen3-0.6B can test the chat adapter, but is
not a quality endorsement or a default assistant selection; larger models and
actual coding/tool-use evaluations are needed.

Lazy-load runtimes and explicitly download only the chosen model/backend.
Cache pinned artifacts with checksums and retained notices. Compatible ONNX
exports can share a corresponding HF repository in separate folders, without
moving existing Core ML paths. Model size/license/required device must be clear
before downloading. Mirror only when redistribution permits; otherwise point
to upstream setup/access requirements or offer a compatible alternative.
No silent cloud fallback, bundled credentials or automatic model execution.

The next phase requires benchmarks on actual target browsers and classroom
hardware. Library support does not establish realtime model performance.
