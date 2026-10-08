# First milestones

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

Liquid D1's October 5 announcement describes text/image decisions in one forward pass, without token generation, and currently provides API access. It announces future open weights; do not assume D1 can be downloaded or converted today. Hosted APIs are not a current priority and are outside the initial milestones. Recheck for newer open-weight announcements before concluding availability; prioritize downloadable local Liquid models. Any later hosted adapter needs explicit user opt-in.

## 6. Distribution readiness

MIT original code, third-party notices, model-specific licenses; package lightweight runtime dependencies; bundle native helper if used; UI model downloads; demos in example_workflows; preserving saved user workflows. Test Manager installation before Registry publication.

## Research references (checked October 7, 2026)

- https://github.com/john-rocky/coreai-model-zoo — recipes, per-model validation and samples.
- https://github.com/john-rocky/coreai-kit — reusable Swift SDK, download/cache and task APIs.
- https://github.com/apple/coreai-models — official export/runtime utilities; macOS/Xcode 27 requirements.
- https://huggingface.co/mlboydaisuke/FLUX.2-klein-4B-CoreAI — author reports ~17s cold-inclusive 1024 image on M4 Max; not a measured live loop here.
- https://huggingface.co/mlboydaisuke/Qwen3-VL-2B-CoreAI — candidate for analysis; token throughput is not full response latency.
- https://huggingface.co/mlboydaisuke/RGBA-Image-2.1-CoreAI — research-license candidate, not default redistribution; substantially slower generation.
- https://www.liquid.ai/blog/d1-decision-model — currently hosted text/image decision model; future open weights announced.
- https://huggingface.co/docs/hub/en/models-uploading — standard publishing flow.

Read current licenses and releases before adopting any dependency or distributing weights.
