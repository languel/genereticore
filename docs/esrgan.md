# Compact Real-ESRGAN cleanup

`GeneretiCoreUpscale` supplies AnimeVideo and General compact SRVGG inference on macOS 14+ Apple silicon. Both 256px and 512px input exports live in the same public bundle; the node automatically selects the appropriate one. No separate resolution nodes are needed.

## Student setup

Install the optional image dependencies described in realtime-image-demo.md and use the updated Genereti companion. Open **14 - Real-ESRGAN cleanup comparison**. Click the upscaler ↓ for the approximately 7.55 MB public bundle; SDXS has its own ↓. No student HF account, token or conversion is needed. The download uses anonymous access, a pinned revision, checksum verification, retained notices and conflict-preserving installation. It never downloads on workflow load.

Start the generator and then the upscaler explicitly with ▶. Default 2x turns 256px input into 512px output. `source` keeps original dimensions for cleanup; `4x` enlarges to four times each dimension. These models always predict 4x internally, followed by Lanczos downsampling for smaller output. Inputs are 2–512px per side. Non-square images are supported; larger inputs require an explicit upstream resize. Alpha composites on white. Live delivery accepts bitmap IMAGE sources, not GPU-only textures. Queued batches are bounded to four images.

Two passes provide the archived same-image refinement idea: predict, downsample, blend with original, predict again. Feedback controls the blend. It does not store previous frames or smooth motion over time. Use one pass first; two cost another prediction and may erase detail. There is no WDN interpolation in the General export.

All native live image requests share one busy gate. Each upscaler retains one newest waiting frame, retries busy responses and discards results after pause/removal/source change. Source subscriptions are released on pause. Inference occurs on a worker thread; active work completes before its busy slot is released. Last completed images remain visible. The dot toggles readable timings; credits belong in help.

## Provenance and publishing

[Public Core ML bundle](https://huggingface.co/languel/genereticore-upscalers-coreml), revision `101d1754bbdd0e9b5945699db1f535249923bff3`. Catalog pins manifest SHA256 `27f34ad49ecfb6b888f9841bda605129b0606eb7258cfdfd5b63702fcdbe1faf`. Package paths: `upscalers/animevideo/{256,512}.mlpackage` and `upscalers/general/{256,512}.mlpackage`.

Independent conversion of [official v0.2.5.0 weights](https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.5.0), architecture pinned to upstream commit `a4abfb2979a7bbff3f69f58f58ae324608821e27`. BSD 3-Clause Real-ESRGAN notices and full source backlinks are retained in the bundle and licensing/Real-ESRGAN-LICENSE.txt. General uses realesr-general-x4v3; AnimeVideo uses realesr-animevideov3. These are compact models, not RRDB RealESRGAN_x4plus. No third-party preconverted package is mirrored.

Contributor conversion uses Python 3.11, Torch 2.5.1, coremltools 8.3.0 and NumPy 1.26.4. The script verifies official weight hashes, performs strict state loading and records random-input Core ML/PyTorch parity. All four exports had RMSE below 0.0005 in this run. FP16 compute, float32 RGB NCHW input/output, macOS 14 target, CPU/GPU execution; static tiles 266/522 include padding. Runtime compiles outside Git and crops back to actual input geometry. Conversion/parity does not establish subjective restoration quality.

```sh
python scripts/convert_upscalers.py --help
python scripts/convert_upscalers.py --output-root /absolute/path/outside-git/exports
python scripts/upscale_bundle.py /absolute/path/outside-git/exports /absolute/path/outside-git/public-bundle
hf auth whoami
hf repo create your-account/genereticore-upscalers-coreml --repo-type model
hf upload your-account/genereticore-upscalers-coreml /absolute/path/outside-git/public-bundle .
```

Run these commands inside the pinned contributor environment above; keep all packages and caches outside Git. See hugging-face-publishing.md for local auth and upload procedure. After publishing, pin the new commit and manifest hash in both bundle catalogs and test a fresh anonymous installation before updating students.

## Local validation (October 10, 2026)

Measured on this Mac, synthetic edges, 2x output, one pass. Warm median of four calls after a first call, not model-card performance or guaranteed student FPS:

| Model | Input | First call, ms | Warm total, ms |
| --- | --- | ---: | ---: |
| AnimeVideo | 256² | 1223.02 | 16.66 |
| AnimeVideo | 512² | 91.54 | 51.72 |
| General | 256² | 42.93 | 15.88 |
| General | 512² | 99.52 | 65.27 |

First-call time includes load and may include compilation/cache setup; this was not a controlled empty-cache cold benchmark. Totals above include native conversion/output resize, but exclude live HTTP/PNG/browser overhead. Models occupy a bounded two-entry cache. Keep source resolution low for performance.

Actual checks passed: all four native exports, non-square 128×96 source/2x/4x two-pass outputs, real SDXS fixture processing, queued LoadImage → upscale → SaveImage, live endpoint output dimensions, foreign-origin rejection, invalid pass rejection and a fresh anonymous full-bundle install. Browser validation and remaining limitations are recorded in handoff.md. Broader student installation, older supported OS and motion-quality testing remain pending.
