# Implementation checkpoint

## Implemented

The Comfy custom-node entry point registers `GeneretiCoreText`, `GeneretiCoreVision`, `GeneretiCoreDecision`, `GeneretiCoreValidateDecision`, `GeneretiCoreResult`, `GeneretiCoreChoiceValue` and `GeneretiCoreTutorial`. Python runtime dependencies are supplied by Comfy; the standalone contracts, CLI, scheduler and backend use the standard library. CoreAIKit is a native dependency pinned to 0.7.3, with transitive revisions recorded in `native/Package.resolved`.

The Swift helper speaks JSON lines over private process pipes, not a public socket. It loads local pinned bundles only. Downloads are a separate explicit task using CoreAIKit's atomic staging and progress reporting. Release-pinned artifact manifests record every required file's size and SHA-256; the Python adapter validates them before loading and after download. It rejects the SDK's alternate-revision offline fallback. A missing helper or model produces an actionable error; there is no hosted adapter or cloud fallback.

One worker runs model work outside browser rendering/audio threads. It accepts four pending jobs: FIFO for queued work and latest-wins within each named live stream. New live observations suppress obsolete active results and replace pending observations, without claiming backend cancellation. Explicit cancellation kills the native helper, releasing its sessions. The next request restarts it. Requests, events, partial text, revisions, queue depth, result age and cold/warm timings are available through the loopback, same-origin Comfy API. At most 64 jobs and 128 events per job are retained.

The SDK models stay warm across independent observations; chat history resets between requests. At most one model task session is resident. Switching between text, decision and vision releases the previous session. Text returns STRING; vision accepts one queued IMAGE and returns STRING; decisions return a validated choice, scores and distributions. Specialist provider output can enter through the independent score-validation node. Scores never execute code. Qwen's decision distribution is an uncalibrated answer-slot softmax, not an accuracy guarantee.

Node toolbars use compact themed glyph actions with titles, accessible names, focus states and status feedback. No task, camera, microphone or screen capture starts when a workflow loads. Async text/decision results emit `genereticore:completed`. Connected Comfy outputs are delivered by Comfy Run. Live vision callers explicitly provide image bytes through the local API; a node toolbar does not silently capture its connected image.

`web/js/client.js` exports a small local API client and a tested current/next result pair. Beat/bar/manual transitions wait for an explicit trigger and renderer-driven phase. This is a bridge primitive, not a completed shader/image-generation demonstration.

## Preserved companion

The companion is `~/dev/genereti-public`. Its legacy generator is under `integrations/legacy-generator`; the lightweight public pack excludes its Core ML inference dependencies. Existing `GeneretiSDXSGenerate` and `GeneretiSDTurboGenerate` IDs remain owned by that pack. GeneretiCore does not register duplicates, remove its engine, change its checkout, or copy embedded Strudel.

The legacy engine imports NumPy, Pillow, Core ML tools, Torch, Transformers, huggingface_hub and its `postprocess` module. It uses local-only pinned SDXS tokenizer/text-encoder snapshots, `.mlpackage` encoder/decoder/denoiser companions and separate compiled caches. Text/sketch inputs are converted to fixed 256/384/512 sizes. Diffusers/PEFT are conversion tools and are not new runtime dependencies here. Its documented sizes/benchmarks remain historical measurements, not new GeneretiCore measurements.

## Remaining roadmap

This is a runnable contributor milestone, not completion of all six distribution milestones. Core ML migration, a complete redistributable SDXS bundle and license audit, actual Genereti drawing → inference → shader transition, shared rendering/inference benchmarking, FLUX tests, portable Liquid d1 adapters and broader quality evaluation remain. Hosted adapters, uploading weights and publishing Registry/Manager releases have not been performed. The helper currently needs a contributor build with Xcode 27; a verified bundled release is required before student distribution without Xcode. No Manager installation claim is made.

## Liquid runtime research

The official [d1-3B card](https://huggingface.co/LiquidAI/d1-3B) currently specifies Transformers >=5.14, repository custom code via `trust_remote_code=True`, and a device-selection example including MPS with bfloat16. Its task API is `system_one`, accepting named choice/score/yes-no questions rather than generated chat. Both [d1-3B](https://huggingface.co/LiquidAI/d1-3B) and [d1-omni-600M](https://huggingface.co/LiquidAI/d1-omni-600M) are marked `lfm1.0`, not MIT/Apache. Those are upstream statements, not local MPS validation. The existing legacy Transformers 4.51.3 environment must not be upgraded in place for this; a separate pinned worker environment and custom-code/license audit are prerequisites for the portable adapter. This portable Transformers path has not been executed here. The separate text-only d1 Core ML path is now integrated and locally tested; see below.

## d1 Core ML and teaching update

`LocalBackend` routes the selected catalog model to Core AI or the separate macOS 15+ d1 helper. Switching backends releases the previous helper; the bounded worker serializes heavy work. d1 uses unmodified upstream MIT manager/tokenizer sources pinned to FluidUse PR 27, `e55561ab32a43d9a70e6531bedc3a05a5e502201`. Its published multifunction package is pinned and checksum-verified, downloaded explicitly by original Python code. The native helper defaults to CPU + Neural Engine, keeping model prediction off the creative GPU path. Model load/compile, prediction and complete request timings are distinct.

The existing decision node adds d1 to its model selector and a separate question field. Output probabilities record `d1_temperature_scaled`; supplied-score and Qwen methods retain their different labels. Eight-options/256-input-token limits are explicit. There is no d1 vision/audio support in this conversion. Actual generation-token budget belongs to Qwen and is ignored by d1.

Eight numbered teaching graphs include Tutorial 0, a supplied-result exercise and a d1 artwork demo. Notes define what the system is doing; titles preserve real node types. Node Info gives descriptions, and `node_type` exposes the saved class in Parameters. The existing result sink now provides a safe local collapsible tree, pretty text and minified JSON; mode persists, arbitrary values use textContent and large trees are bounded. No JSON is sent to the referenced external viewer.
