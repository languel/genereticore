# Optional browser models and realtime perception

Agreed direction, October 10, 2026. Next focus: MediaPipe, segmentation and tracking, followed by evaluation of SAM 3, RF-DETR, DINO-family models and Roboflow integration. These perception capabilities and the pumpkin workflow remain planned.
The first ONNX browser upscaler milestone is documented in browser-onnx.md;
it is not included in the previously published 0.1.0 Registry archive.

Genereti stays a lightweight realtime framework and owns the assistant UI,
workspace tools, review/apply/undo, thresholds, smoothing, event routing,
palette controls and prompt connections. GeneretiCore owns optional model
catalogs, downloads, license/provenance records and execution, whether native
Core ML/Core AI or browser inference. Lightweight MediaPipe tasks and their
interaction nodes are candidates for Genereti, alongside model-free tracking
and image processing. MediaPipe still uses model assets: treat the download,
license, worker cost and memory footprint explicitly, and keep these features
optional. Larger or specialized downloadable models belong in GeneretiCore.
Choose the package by dependency and operational cost, not merely whether a
file contains weights or the runtime runs in the browser. Keep the base Genereti
install and its default demos independent of optional model downloads.

## Runtime choices by task

1. Evaluate Transformers.js for supported vision analysis, embeddings, speech and text
   pipelines; WebGPU acceleration or an explicitly supported WASM CPU path.
2. ONNX Runtime Web directly for custom image pipelines such as our compact
   Real-ESRGAN and segmentation, with controlled preprocessing/postprocessing.
3. Evaluate MediaPipe Tasks for lightweight specialized hands/pose/face/segmentation workflows.
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

## Next implementation sequence

1. Define a common perception result and live-input contract before adding more
   model nodes. Reuse the shared IMAGE subscription and worker lifecycle already
   exercised by browser upscaling. Keep borrowed-frame copying synchronous and
   one inference request plus the newest waiting frame per consumer.
2. Build one optional lightweight MediaPipe demo in Genereti: landmarks or
   person segmentation from the updated 2D stream, then webcam started by the
   user. Output normalized observations or a mask, not only a painted overlay.
   Measure whether it remains responsive alongside creative rendering.
3. Add one detection and one segmentation provider in GeneretiCore. Pick actual
   checkpoints only after reviewing licenses, available exports, operator
   support, download sizes and measured device performance. Start with the
   existing ONNX/WebGPU worker foundation; add native adapters where practical.
4. Add tracking as a separate stage with persistent IDs, lost-track timeout,
   reset and optional temporal stabilization. Distinguish simple association
   or optical flow from model-based tracking and promptable video segmentation.
5. Connect observations to Genereti rules and events. Complete stable object
   presence → palette change → one prompt on entry before assistant interpretation.
6. Evaluate larger promptable segmentation and open-vocabulary models after
   the shared outputs, performance measurements and cancellation paths work.

| Candidate | Evaluation purpose | Intended home |
| --- | --- | --- |
| MediaPipe Tasks | Lightweight landmarks, pose/face/hands and segmentation | Optional Genereti features when measured cost is suitable |
| Model-free tracking, association, thresholds and smoothing | Stable controls and entry/exit events | Genereti |
| SAM 3 | Promptable segmentation and tracking candidate | GeneretiCore model provider |
| RF-DETR | Object detection and applicable segmentation checkpoints | GeneretiCore model provider |
| DINO family | Evaluate specific detection/embedding models; DINO, Grounding DINO and DINOv2 are distinct candidates | GeneretiCore model provider |
| Roboflow | Evaluate export/tooling integration and checkpoint provenance | Core for model execution; Genereti for routing and controls |

This table is an evaluation backlog, not a claim that these models have working
browser or Apple-native exports here. Review each exact checkpoint separately.
Roboflow integration does not imply hosted inference or user-media uploads;
local exports are the default, with hosted use requiring explicit authorization.

## Perception and tracking contract

Use a versioned structured result with source identity/revision, frame timestamp,
source width/height, coordinate convention, model/backend, timings and result age.
Detections include labels, confidence and boxes. Segmentation exposes an actual
mask plus class/object association; overlays are optional views. Landmarks
include confidence/visibility and named coordinate space. Tracking adds track
IDs and acquisition/update/lost events. Do not imply stable tracking from a
per-frame detection index.

Keep image, mask and structured observations available through normal ports.
Define how a slower result maps to the source frame; clear tracks and history
on source replacement or geometry changes. Confidence thresholds, hysteresis,
entry/exit duration and cooldowns belong in Genereti's decision/control layer.
Reset, pause, removal and unload must release subscriptions and model resources.

Acceptance for each provider: direct stream and preview-mediated input; explicit
webcam start/stop; masks/boxes aligned on non-square input; source-change stale
result rejection; bounded memory/queue; cold download/load and warm timing;
render responsiveness; pause/restart/unload; documented license and anonymous
installation where permitted. Test WebGPU, WASM, Core ML and Core AI only when
that exact export/backend is supported. Never silently switch backend or cloud.

Perception model selection, download, conversion, hosting and implementation
remain future work; none is claimed as complete in this checkpoint. The existing browser ONNX upscaler and native image routes remain usable.

## Investigation checkpoint

See [perception-investigation.md](perception-investigation.md) for exact candidate
revisions, license/export findings and the first local SlimSAM CPU contract probe.
RF-DETR Nano/Seg Nano and Grounding DINO are the proposed first Core providers;
MediaPipe implementation remains in the separate Genereti session. No new
perception node, public model bundle or browser benchmark is claimed.
