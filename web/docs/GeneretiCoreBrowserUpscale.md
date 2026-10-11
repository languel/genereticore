# ꘅ ONNX upscale

Experimental browser-only Real-ESRGAN worker: local image cleanup/upscaling on the viewing device. GeneretiCore owns optional downloads and execution; Genereti supplies streams and preview/output views.

## Start here

Open **15 - Browser ONNX upscaling**. Load a local image/video/GIF in the 2D stream and press its Play control. The sample explicitly resizes to 256×256. ↓ downloads about 34.7 MB of verified public ONNX models and runtime files; ↑ loads and warms the selected model/backend; ▶ starts inference; Ⅱ pauses; × unloads the worker and its GPU resources. Nothing downloads or runs on workflow load. No HF account or student conversion is needed.

Choose AnimeVideo for illustrated content or General for ordinary images. WebGPU and WASM CPU are separate explicit choices; unavailable/failed GPU execution reports an error, with no silent backend or cloud fallback. Browser/device support and speed vary. An active browser is required; this is not headless Python inference or an assistant provider.

## Input and output

Connect any shared live IMAGE source, directly or through Image Preview. Borrowed source frames are copied immediately. Keep delivery Live. Inputs must be 2–256px per side; larger sources need an explicit upstream resize. The worker predicts 4x, then high-quality canvas resizing gives source/2x/4x output. Alpha composites on white. Output retains the last completed image during loading, inference, pause and unload. A single pending frame replaces older waiting frames; pause/source changes discard stale results and release subscriptions. There is no previous-frame smoothing or recursive refinement yet.

Comfy Queue deliberately reports that an active browser is required. Use the separate native **Real-ESRGAN upscale** node for queued image processing. Browser output is a live IMAGE frame; it is not automatically an input to an arbitrary queued Python node.

The dot toggles timing text. Total measures worker round-trip including preparation and output; Model measures the ONNX session call, including runtime-managed transfers. The FPS estimate is 1000/mean Total, rather than measured display/source FPS. Cold load includes warmup. WebGPU work can compete with creative rendering even in a worker.

## Credits and provenance

[Model sources, checksums, tool versions and PyTorch parity](https://huggingface.co/languel/genereticore-upscalers-coreml/tree/300be594b8faf75dc297799c57950f763422bc89/onnx). Real-ESRGAN by Xintao Wang and contributors, [BSD-3-Clause full license](https://huggingface.co/languel/genereticore-upscalers-coreml/blob/300be594b8faf75dc297799c57950f763422bc89/onnx/LICENSE). Independently exported from official AnimeVideo-v3 and General-x4v3 weights; no upstream endorsement. ONNX Runtime Web 1.24.3 by Microsoft and contributors, MIT; full notice bundled in licensing/ONNX-Runtime-LICENSE.txt. Models and runtime binaries stay outside Git, with pinned hashes in the download catalog.

Cross-browser, classroom hardware, long-running motion quality and device-loss behavior need wider testing. SDXS/Turbo, detection, segmentation and assistant providers are separate future browser integrations.
