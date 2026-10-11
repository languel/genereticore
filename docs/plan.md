# First milestones

Implementation update: the Core AI contributor path and Comfy task/API interface are running locally. Read [implementation.md](implementation.md) and [validation.md](validation.md) for verified scope, model-quality failures and remaining work. These milestones are a roadmap, not all completed.

## 0. Establish evidence and boundaries

Inventory the existing native Core ML pack and its engine imports in Genereti. Record model sizes, preprocessing, node IDs, dependencies, license provenance and current benchmarks. Avoid carrying conversion-only Torch/Diffusers pins into Comfy's runtime requirements. Check disk space before model downloads.

## 1. Upstream Core AI smoke test

Use a pinned CoreAIKit release (0.7.3 is the current research candidate; verify before use). Run its small qwen3-0.6b chat example locally, then test vision with Qwen3-VL 2B. Capture cold load, first response, warm latency, memory, cancellation behavior and complete image-to-answer latency. No model-card throughput claims count as local results.

## 2. Runnable extension and backend separation

Add a minimal installable Comfy pack and one independently usable task node. Implement a backend capability interface and helper lifecycle. Migrate the existing Core ML SDXS backend incrementally, preserving IDs and preventing duplicate registration. Keep the original Genereti installation working throughout.

## 3. Model distribution

Prepare one complete SDXS bundle locally; audit redistribution terms for every component before uploading. Create Hugging Face model cards with upstream revisions, conversion recipe, license notices, model contract and tested hardware. Validate downloads and restart recovery using a clean Comfy installation. No scripts or Xcode build should be required from students for a distributed supported runtime.

See [model-distribution.md](model-distribution.md) for today's download behavior,
automatic local compilation versus developer conversion, and remaining release work.

## 4. Realtime image demo

October 9 cloud update: four editable livecode/drawing → SDXS/Turbo → preview graphs and a stable-ID image-runtime source migration are now authored. See [realtime-image-demo.md](realtime-image-demo.md). Mac parity/performance and the complete current/next shader transition remain unverified.

Genereti drawing/p5 source -> inference -> current/next image pair -> shader transition -> output. Hold the previous image during inference; emit completion and support immediate/beat/bar transitions. Start with SDXS, then benchmark FLUX.2 klein at supported sizes. Do not promise near realtime before measurement.

## 5. Analysis and decisions

VLM image analysis -> structured controls; small local language model -> scene decisions. Evaluate Liquid local models and their individual licenses/runtime support. Make the decision task accept probabilities, choices and scores so it can accommodate specialist models and constrained LLM/VLM responses.

Liquid released downloadable d1-3B and experimental d1-omni-600M on October 7, 2026. Prioritize local decision experiments: text/image state -> choice probabilities or scores -> creative controls. d1-omni also supports text/audio. Inspect the official runtime, model-specific Liquid license and MPS compatibility before choosing an adapter or converting to Apple formats. Published Jetson timings are not Mac measurements. The October 5 hosted d1 announcement predates these open-weight releases.

Hosted APIs are optional later work, not a current priority. Free provider routes may be useful but availability, limits and data transmission must be explicit; no automatic cloud fallback.

## 6. Distribution readiness

MIT original code, third-party notices, model-specific licenses; package lightweight runtime dependencies; bundle native helper if used; UI model downloads; demos in example_workflows; preserving saved user workflows. Test Manager installation before Registry publication.

## Research references (checked October 7, 2026)

- https://github.com/john-rocky/coreai-model-zoo — recipes, per-model validation and samples.
- https://github.com/john-rocky/coreai-kit — reusable Swift SDK, download/cache and task APIs.
- https://github.com/apple/coreai-models — official export/runtime utilities; macOS/Xcode 27 requirements.
- https://huggingface.co/mlboydaisuke/FLUX.2-klein-4B-CoreAI — author reports ~17s cold-inclusive 1024 image on M4 Max; not a measured live loop here.
- https://huggingface.co/mlboydaisuke/Qwen3-VL-2B-CoreAI — candidate for analysis; token throughput is not full response latency.
- https://huggingface.co/mlboydaisuke/RGBA-Image-2.1-CoreAI — research-license candidate, not default redistribution; substantially slower generation.
- https://www.liquid.ai/blog/d1-decision-model — October 5 hosted release.
- https://huggingface.co/blog/LiquidAI/open-d1 — October 7 open-weight release.
- https://huggingface.co/LiquidAI/d1-3B
- https://huggingface.co/LiquidAI/d1-omni-600M
- https://huggingface.co/docs/hub/en/models-uploading — standard publishing flow.

Read current licenses and releases before adopting any dependency or distributing weights.

October 10 checkpoint: complete private 512px SDXS text/sketch and Turbo image
bundles are uploaded, revision-pinned and validated through fresh downloads and
offline local inference. Live Comfy source/generator/preview was exercised. See
model-distribution.md and validation.md. Public notice/license clearance and an
image-node Download UI are next; Canny hosting remains blocked by unclear terms.

October 10 public-access update: SDXS/Turbo bundles are public with retained upstream
terms and attribution; anonymous pinned downloads now have an explicit image-node
control. Canny is not mirrored; original-source setup and compatible alternatives
are documented. Verify broad student installation and interrupted downloads on a
separate machine next. Never infer a legal prohibition merely from private staging;
use the source-by-source published terms in image-license-review.md.

Realtime cleanup/upscaling research: see [realtime-upscaling.md](realtime-upscaling.md).
Start with a model-free Genereti cleanup/upscale comparison, then add optional
change-aware temporal smoothing and benchmark compact native models. Separate
same-image recursive refinement from previous-frame smoothing. Publish only
reviewed converted bundles with complete provenance and anonymous verification.

October 10 compact-upscaler milestone: shipped the V3 GeneretiCoreUpscale node,
explicit public verified downloads for independent AnimeVideo/General Core ML
256/512 exports, source/2x/4x output and same-image refinement. Native, queued,
anonymous installation and live browser comparison were exercised locally.
See esrgan.md and handoff.md for actual measurements/limits. Next Genereti work
is model-free spatial cleanup and separately resettable temporal smoothing;
see genereti-cleanup-handoff.md. Segmentation/MediaPipe remains planned research,
not a shipped capability.

## Browser perception and provider direction (2026-10-10)

See browser-perception-plan.md for the agreed package boundary and perception → decision → action pipeline. Genereti owns interaction, assistant/tools and routing; Core owns optional model downloads, licenses and browser/native execution. Start with object detection, segmentation and structured vision analysis; pumpkin presence selects a Halloween palette and sends a prompt once on stable entry. Use deterministic rules before adding interpretive decision models. These browser features are planned and excluded from the 0.1.0 early-alpha Registry release. See release-0.1.0.md for shipped scope and platform/helper limitations.

Browser ONNX milestone: a separate browser-only compact Real-ESRGAN node now uses explicit verified runtime/model downloads and a WebGPU/WASM worker. It exercises shared live stream/preview connections without changing native queued nodes. See browser-onnx.md and handoff.md for actual tests and measurements; perception and assistant integration remain next.


## Next focus: realtime perception and tracking

Use [browser-perception-plan.md](browser-perception-plan.md) as the implementation
backlog and package boundary. Prioritize optional lightweight MediaPipe in
Genereti, shared masks/landmarks/detections, then downloadable detection and
segmentation providers in GeneretiCore. Evaluate SAM 3, RF-DETR, specific DINO
family checkpoints and Roboflow local exports without assuming runtime or
license compatibility. Genereti owns lightweight tracking, control rules and
visualization; model-dependent tracking belongs in Core. Browser WebGPU/ONNX
and native Core ML/Core AI are adapters to the same result contract, subject to
actual supported exports and measured performance. No new perception capability
or Registry release has been implemented by this documentation update.
