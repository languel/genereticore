# Clean realtime image enlargement

Research checkpoint: October 10, 2026. This is an implementation proposal,
with two native model smoke benchmarks, not a shipped upscale node or a new
published model bundle.

The goal is clean enlarged pixels and stable edges, even at the cost of fine
texture. Treat spatial cleanup, enlargement and temporal stabilization as
separate controls. An upscaler cannot reliably recover a thin line already
missing from the source. Sharpening can amplify the speckle and stair steps in
low-resolution generator output.

## What the original version did

The archived `integrations/legacy-generator/coreml_upscaler.py` in the companion
wrapped two Core ML Real-ESRGAN exports: AnimeVideo and General. Both took a
fixed 522px input tile, with reflection padding around inputs up to 512px,
and produced 4x output cropped to the source dimensions. Even a 256px image
was padded to the same model size. Benchmark purpose-built 266px exports
(256 + 10px padding) before adopting that inherited performance floor.

`postprocess.py` offered 1–4 recursive upscale passes: upscale, downsample to
source size with Lanczos, blend with the original, then upscale again. This
was same-image refinement; it did not average successive video frames.
`engine.py` separately blended previous predicted latents for image-mode
feedback. Neither is motion-compensated temporal reconstruction.

Current public Genereti already has `top.filter` blur and `top.feedback` /
`top.feedbackref`. The feedback nodes support screen/add/over compositing and
creative trails. They are not normalized temporal denoisers: screen/add can
brighten the picture, and opaque input can hide over-composited history.
Use a dedicated averaging/rejection path for clean stabilization.

## Options and ownership

| Option | What it helps | Main tradeoff | Home |
| --- | --- | --- | --- |
| Bilinear/bicubic enlargement | Softens enlarged pixel blocks; useful baseline | No edge reconstruction; softer lines | Genereti |
| Edge-preserving bilateral smoothing + bicubic enlargement | Reduces local grain while retaining strong boundaries | Weak/thin lines may disappear; tune color threshold | Genereti |
| FXAA-style postprocess | Reduces visible high-contrast stair steps and subpixel aliasing | Does not reconstruct missing detail or remove all texture noise | Genereti |
| SMAA 1x | Spatial edge/pattern detection for anti-aliasing | More passes and lookup textures than a simple filter | Genereti |
| FSR 1 EASU + optional RCAS | Edge-adaptive spatial enlargement, controllable sharpening | Port shader code to WGSL; weak source edges stay weak | Genereti |
| Change-aware temporal averaging | Reduces shimmer across new generated images | Motion/change can ghost; needs rejection and reset | Genereti |
| Real-ESRGAN AnimeVideo-v3 | Small model candidate for clean stylized edges | Alters texture; test temporal flicker and thin lines | GeneretiCore |
| Real-ESRGAN General-x4v3 / WDN variant | Small general restoration model, denoise-strength option upstream | More native work; may add unwanted detail | GeneretiCore |
| RealESRNet-x4plus | MSE-trained model explicitly described upstream as over-smooth | Larger/slower candidate; secondary comparison | GeneretiCore |

FXAA is a single-image anti-aliasing method, not an upscaler. FSR 1 is a useful
spatial upscale candidate for an RGB-only image pipeline. FSR 2 requires depth,
motion vectors and jittered rendering inputs. Generated RGB frames do not
supply those buffers; an optical-flow approximation would add work and different
failure modes. Describe our eventual implementation by its actual technique,
rather than calling it DLSS or claiming equivalent reconstruction.

These recommendations are hypotheses for the shown stylized images. No
side-by-side quality verdict or shader timing was measured in this checkpoint.

## Native smoke measurements on the current Mac

Downloaded the same checksum-pinned preconverted v1.0.0 exports used by the
archived download script, outside Git. Used the archived wrapper with
coremltools 9.0, CPU + GPU. Synthetic RGB circle fixture; one first call then
four warm calls per input size, synchronous PIL-to-PIL timing. These include
array preparation, native prediction, crop and output pixel conversion. They
exclude Comfy request/transfer/display and are not a benchmark with inference
and creative rendering isolated from all other activity.

| Model | Input → output | First call | Warm median (4 samples) |
| --- | --- | ---: | ---: |
| AnimeVideo | 256 → 1024 | 69.48 ms | 18.84 ms |
| AnimeVideo | 512 → 2048 | 37.61 ms | 35.42 ms |
| General | 256 → 1024 | 58.69 ms | 25.80 ms |
| General | 512 → 2048 | 41.54 ms | 42.02 ms |

Wrapper compile/load took 1304.94 ms for AnimeVideo and 65.83 ms for General
in that process. These are not clean-machine cold-compilation guarantees.
Coremltools warned that the installed Torch 2.12.1 exceeds its tested Torch
version; these measurements executed already-converted Core ML packages,
not a conversion using that Torch environment.

The small models are worth testing alongside 256px generation. Their cost
must be added to the generation/delivery budget; model-only timings do not
establish a combined realtime frame rate. Repeated refinement adds another
prediction per pass and should default to one pass.

## Proposed first implementation

Add a separate image cleanup/upscale node in Genereti with output size,
spatial method, smoothing and optional low sharpening. Keep the generator
unchanged; support live GPU frames through the existing source/subscription
and output-window contracts, with queued parity for supported spatial modes.
Start with bicubic and bilateral smoothing, then compare a licensed FXAA or
FSR 1 port. Retain actual output dimensions through downstream textures.

Add temporal smoothing independently: normalized previous/current blending,
per-pixel change rejection and neighborhood clamping, with a scene-change
reset. Advance history only when a new source frame arrives, not every display
tick while the generator holds the same image. Reset on source/model/size
changes, seek and explicit reset. Default history off; expose strength and
change sensitivity. This reduces shimmer but cannot promise blur-free motion.

Add an optional GeneretiCore model-upscale node after that comparison, with
one bounded worker, newest-frame replacement, held last result and explicit
start/pause. Benchmark 256 and 512 exports, 2x output by downsampling the
4x prediction, and 1 versus 2 refinement passes. Students download ready
packages; conversion remains a contributor task.

Compare clean lines, grain, haloing, missed thin strokes and motion trails on
both generated stills and a moving drawing. Record warm p50/p95, first load,
combined generator-plus-upscale time, actual completion FPS, memory and
visual rendering cadence. Shader GPU submission time alone is not execution
time; use timestamp queries where supported or a completed readback fixture.

## Public hosting and provenance

FSR 1 is MIT; SMAA uses a permissive MIT-style license. Retain their full
notices and backlinks when porting code or shipping lookup textures. Audit
the specific FXAA implementation's terms before copying it; the whitepaper
is a technical reference, not blanket permission for every third-party port.
Lightweight shaders ship with Genereti and need no HF model repository.

Real-ESRGAN upstream publishes BSD-3-Clause source and official model downloads.
The official AnimeVideo/General weights are the preferred conversion source.
Retain the upstream authors, full license, exact source revision and weight
hashes; review accompanying release notices before publishing derived exports.
The third-party Core ML export repository has no top-level license file in its
current file inventory. Use its artifacts only as an evaluation reference;
do not copy its converter or mirror its converted binaries on an assumed
license. Convert official weights with our own contributor recipe instead.

Publish approved models in a separate public `YOUR_ACCOUNT/genereticore-upscalers-coreml`
repo with folders for model and supported source sizes, a model card, notices,
conversion/runtime pins and checksum manifest. Pin the resulting commits in
an allowlisted download catalog and verify anonymous fresh installs and local
inference before enabling a student Download control. There is no new HF
upscaler publication in this checkpoint.

## Primary references

- [Real-ESRGAN source and BSD-3-Clause license](https://github.com/xinntao/Real-ESRGAN)
- [Official model zoo](https://github.com/xinntao/Real-ESRGAN/blob/master/docs/model_zoo.md)
- [AnimeVideo model details](https://github.com/xinntao/Real-ESRGAN/blob/master/docs/anime_video_model.md)
- [General model and denoising interpolation implementation](https://github.com/xinntao/Real-ESRGAN/blob/master/inference_realesrgan.py)
- [Core ML export evaluation source](https://github.com/hanxiao/real-esrgan-coreml)
- [AMD FSR 1 source and MIT license](https://github.com/GPUOpen-Effects/FidelityFX-FSR)
- [AMD FSR 2 input contract](https://github.com/GPUOpen-Effects/FidelityFX-FSR2#input-resources)
- [SMAA source and license](https://github.com/iryoku/smaa)
- [NVIDIA FXAA whitepaper](https://developer.download.nvidia.com/assets/gamedev/files/sdk/11/FXAA_WhitePaper.pdf)
