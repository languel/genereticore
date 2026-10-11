# Browser ONNX milestone

The first browser backend is an experimental compact Real-ESRGAN upscaler. It establishes explicit optional downloads and worker execution against an existing native comparison. Detection, segmentation, SDXS/Turbo and the assistant provider are separate future integrations; this node does not implement them.

Use **15 - Browser ONNX upscaling** with updated Genereti sources/previews. The 2D stream explicitly resizes to 256×256; load local media and start playback. ↓ downloads about 34.7 MB; ↑ loads and warms; ▶ starts; Ⅱ pauses; × unloads. WebGPU and WASM CPU are explicit alternatives, with no silent backend/cloud fallback. Browser artifacts are served by local Comfy but frames stay inside the browser worker and never go to HF or the Python inference endpoints. The viewing device runs inference, independently of the Comfy server platform.

The browser-only V3 node preserves all existing native IDs and queued behavior. Attempting to queue the browser node gives an explicit instruction to use the native Real-ESRGAN node. A currently open browser and shared live IMAGE source are required. A headless browser provider/assistant adapter has not been shipped.

## Model and runtime contract

Real-ESRGAN AnimeVideo-v3 (16 compact convolution blocks) and General-x4v3 (32), independently exported from official reviewed weights. BSD-3-Clause credits and upstream links remain in model notices and documentation. ONNX opset 17, float32 RGB NCHW, fixed 266×266 padded input and 1064×1064 output. Inputs accept 2–256px per side with repeated reflection to the fixed tensor; alpha composites on white. Crop to 4x actual source dimensions, then high-quality canvas resampling for source/2x. Canvas resampling differs from native Lanczos. No temporal history or recursive refinement is included.

The corresponding existing HF repository now has `onnx/{animevideo,general}/256.onnx`, `onnx/LICENSE`, `onnx/provenance.json` and `onnx/README.md`, pinned revision `300be594b8faf75dc297799c57950f763422bc89`. Core ML folders/revisions are untouched. Anonymous fresh downloads passed file-size and SHA-256 checks. Student accounts and conversion are unnecessary.

ONNX Runtime Web 1.24.3 is pinned to the npm artifact bytes, including its Asyncify module/WASM dependency. Assets are lazily downloaded outside Git under Comfy's `models/genereticore/browser`, with a catalog-bound verification receipt and per-serve checksum checks. The runtime MIT license is retained in `licensing/ONNX-Runtime-LICENSE.txt`. The local allowlisted asset routes reject foreign origins and arbitrary paths. No user-defined URLs, credentials, or images are accepted by the asset installer.

Sources: [official runtime deployment](https://onnxruntime.ai/docs/tutorials/web/deploy.html), [WebGPU setup](https://onnxruntime.ai/docs/tutorials/web/ep-webgpu.html), [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN), [published ONNX provenance](https://huggingface.co/languel/genereticore-upscalers-coreml/tree/300be594b8faf75dc297799c57950f763422bc89/onnx).

## Scheduling and lifecycle

Borrowed live frames are copied synchronously into one owned canvas. The worker receives at most one active inference; newer source frames replace the waiting canvas. Preparation, inference and output reconstruction happen in the worker. Main-thread work is frame copy, one pixel readback per request and output publication. Source changes/dimensions/pauses invalidate old results; pause releases subscriptions, unload terminates the worker, and removal/pagehide unload automatically. No camera is started by subscribing. Explicit load compiles/warms the first prediction and reports cold time. GPU contention with creative rendering remains possible even with a worker.

Total measures worker round-trip including preprocessing and output; Model measures `session.run`, including runtime-managed transfers; it is not a GPU-kernel timer. FPS is 1000/mean Total and excludes input cadence and display refresh. These are timing estimates, not claims of classroom speed. No 512px exports, tiling, automatic memory/device recovery, long-running soak or cross-browser parity is claimed yet.

## Contributor conversion and publishing

Use a separate environment with Torch, ONNX 1.20.0 and ONNX Runtime 1.24.3. The current recipe imports the existing compact architecture and requires the optional Core ML conversion dependencies as well. Keep all outputs outside Git:

```
python scripts/convert_upscalers_onnx.py --output-root /absolute/path/outside-git/exports
hf auth whoami
hf upload your-account/your-upscaler-repository /absolute/path/outside-git/exports/onnx onnx
```

If an environment `HF_TOKEN` overrides the intended saved login, unset that override for the publishing command and verify the account again. Do not put tokens in source or workflows. Record the resulting immutable revision and regenerate reviewed asset hashes/URLs before distribution. The recipe asserts official source checksums, validates the graph and compares actual ONNX CPU predictions against PyTorch before publication.

Both exports passed FP32 numerical parity, RMSE 0.00000069/0.00000070 respectively. This verifies conversion on a deterministic fixture, not perceptual quality or every browser GPU implementation. See handoff.md for measured browser results and remaining validation.

## Local browser measurements (October 10, 2026)

Codex in-app Chromium browser, Apple M5 Max, 128 GiB unified memory, macOS 27.0; simultaneous Genereti stream/source/result previews. Inputs explicitly 256×256, 2x output:

| Model/backend | Cold load + warmup | Warm Total | Warm Model | Inverse-Total estimate |
|---|---:|---:|---:|---:|
| AnimeVideo / WebGPU | 680 ms | 154 ms | 148 ms | 6.5 FPS |
| General / WebGPU | 590 ms | 271–308 ms | 265–302 ms | 3.2–3.7 FPS |
| AnimeVideo / WASM CPU | 1833 ms | 1641 ms | 1634 ms | 0.6 FPS |

These are representative displayed window averages, not controlled cross-device benchmarks or measured display FPS. The graph remained responsive during inference. Native Core ML is substantially faster on this Mac; browser portability does not establish realtime speed. A synthetic animated GIF also passed direct 128×96 → 256×192 and 512×384 output, exercising replacement of waiting frames. Source-sized output, pause/restart and unload were checked. General WASM, exact GPU pixel parity, 512px browser models, FP16/quantized optimization and broader rendering-contention/soak tests remain pending.
