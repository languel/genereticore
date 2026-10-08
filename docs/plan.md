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

## 4. Realtime image demo

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
