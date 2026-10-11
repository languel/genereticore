# GeneretiCore perception investigation

Checked October 10, 2026. Research and one local synthetic ONNX probe; no new
Comfy perception node or production model bundle is shipped. MediaPipe work is
being implemented separately in Genereti. This investigation does not modify it.

## Recommended first providers

Start with **RF-DETR Nano detection and Seg Nano instance segmentation** for
fixed-label processing, and **Grounding DINO Tiny** for text-driven detection.
Use **SlimSAM** as a small point/box-prompted mask experiment. Keep SAM 3 as a
separate advanced provider investigation, not the first student download.

| Candidate | Useful capability | Verified evidence | Next test |
| --- | --- | --- | --- |
| RF-DETR Nano | Detect known object classes | Official Nano checkpoint and Apache designation; documented ONNX export; default 384px model input | Export fixed batch 1; inspect ONNX operators; compare decoded detections with PyTorch; measure browser and native |
| RF-DETR Seg Nano | Instance masks associated with detected objects | Official Seg Nano checkpoint and Apache designation; default 312px model input | Validate mask decoding, source-space alignment and threshold behavior |
| Grounding DINO Tiny | Detect objects described in text | Existing ungated Apache-declared Transformers.js ONNX conversion, with tokenizer and processor | Test pinned FP32/FP16 or a supported quantized export in a worker; assess prompt accuracy and latency |
| SlimSAM 77-uniform | Point/box-prompted masks | Existing ungated Apache-declared split ONNX encoder/decoder; local quantized CPU probe passed | Test real images, non-square coordinate transforms, cached image embeddings and browser backend coverage |
| DINOv2 Small | Visual embeddings/features | Ungated Apache-declared source checkpoint | Only add for a demonstrated matching/feature use case; embeddings alone do not provide object labels or persistent tracks |
| SAM 3 / 3.1 | Concept/prompt segmentation and advanced video tracking | Official custom SAM License, gated SAM 3 checkpoint and CUDA-focused upstream setup | Review exact variant, access/redistribution requirements and feasible Apple/browser export before integration |

RF-DETR evidence is pinned to upstream develop commit
`eca736acab9f6fe93f2cbc82a1d9f6edfb53f0ea`, not an installed release. The current
[official README](https://github.com/roboflow/rf-detr/blob/eca736acab9f6fe93f2cbc82a1d9f6edfb53f0ea/README.md)
designates Nano detection and Seg Nano as Apache 2.0. Plus detection variants
have different terms; do not infer a license from the RF-DETR family name.
Resolve an installable package/exporter version before conversion. No upstream
GPU speed claim is a measured GeneretiCore result.

The [official ONNX guide](https://rfdetr.roboflow.com/latest/exports/onnx/)
requires explicit output decoding: normalized center/width/height boxes and
unactivated class logits. Match `dets` and `labels` by name, apply sigmoid and
use the checkpoint's category/background mapping. Official sparse COCO classes
must not lose their final class by assuming the last logit is background.
Segmentation adds masks; threshold/crop/resample behavior must be validated.

The official RF-DETR COCO label map does **not** contain pumpkin. A fixed-label
COCO detector cannot implement the pumpkin example by relabeling an unrelated
class. Use a fine-tuned detector, or an open-vocabulary detector such as Grounding
DINO, and validate on actual scenes. See the
[pinned label map](https://github.com/roboflow/rf-detr/blob/eca736acab9f6fe93f2cbc82a1d9f6edfb53f0ea/src/rfdetr/assets/coco_classes.py).

## Native and browser paths

RF-DETR's [native Core ML](https://rfdetr.roboflow.com/latest/exports/coreml/)
and [Core AI](https://rfdetr.roboflow.com/latest/exports/coreai/) export guides
are marked experimental. This makes direct exports worth testing, not proven
working adapters here. Keep fixed shapes and batch 1. Core AI requires the actual
27+ runtime. Benchmark FP32 and FP16 separately, including cold compilation and
postprocessed detections/masks; ranking changes can affect near-threshold results.

For Grounding DINO, prefer the existing
[Transformers.js conversion](https://huggingface.co/onnx-community/grounding-dino-tiny-ONNX)
over reproducing its tokenizer and processor first. Query formatting and token
postprocessing matter. Start with one fixed candidate-label list, cache text
preparation where supported, and run semantic analysis less often than rendering.
It is a detector, not a captioner or decision model.

ONNX is not a backend-compatibility guarantee. The downloaded SlimSAM q8 graphs
contain `ConvInteger`, `DynamicQuantizeLinear` and `MatMulInteger`, absent from
the project's pinned [ORT 1.24.3 WebGPU operator table](https://github.com/microsoft/onnxruntime/blob/v1.24.3/js/web/docs/webgpu-operators.md).
This is a compatibility warning from graph inspection, not an observed browser
failure. Evaluate FP32/FP16 separately and report partitioning/CPU fallback where
applicable. Do not advertise a fully GPU path solely because `webgpu` is selected.

## Pinned artifact sizes

Anonymous HF API metadata, full revisions and upstream SHA-256 values are saved
in [research/perception-candidates-2026-10-10.json](research/perception-candidates-2026-10-10.json).
Sizes below are decimal MB of weights only, excluding configs, tokenizer,
runtimes and execution memory.

- Grounding DINO Tiny: FP32 718.8 MB; FP16 360.4 MB; q8 approximately 203.8 MB;
  q4f16 151.1 MB. Smaller file size does not establish operator coverage or speed.
- SlimSAM split encoder + decoder: FP32 39.8 MB; FP16 20.7 MB; q8 13.8 MB.
- DINOv2 Small source safetensors: 88.2 MB; that is not a browser export.
- SAM 3 source safetensors: 3,439.9 MB; gated and not a browser export.

All HF candidates' license labels are metadata, not a complete redistribution
review. Preserve original model cards, source license, conversion provenance and
notices before publishing any new bundle. SAM 3's
[license](https://huggingface.co/facebook/sam3/blob/main/LICENSE)
permits redistribution under conditions; gating alone is not a redistribution
ban. Keep upstream access/setup instructions until the intended distribution
flow is reviewed. The upstream [SAM 3 repository](https://github.com/facebookresearch/sam3)
also documents SAM 3.1; select and pin the exact variant rather than mixing
checkpoints and code. No SAM assets were downloaded or mirrored in this probe.

## Actual local SlimSAM probe

Downloaded the two q8 ONNX files anonymously at revision
`5850ab45f587c112167512ffef949107115e26a0`, verified their sizes and SHA-256
against HF metadata, and loaded them with ONNX Runtime 1.24.3 CPU on this Apple
silicon Mac, macOS 27.0.1, two intra-op threads. Model files remain outside Git.

The encoder takes RGB-normalized `[1,3,1024,1024]` and outputs image and positional
embeddings `[1,256,64,64]`. The decoder accepts point coordinates, int64 labels
and both embeddings, returning three candidate 256px mask logits and IoU scores.
A normalized synthetic square with a foreground center point produced finite
outputs with expected shapes. No visual quality or browser inference is claimed.

Measured model-only samples:

| Phase | Local measurement |
| --- | --- |
| Both sessions loaded | 145 ms |
| First encoder + decoder execution | 958 ms |
| Warm image encoding, 3 samples | 948 / 880 / 869 ms |
| Warm prompt/mask decoding, 3 samples | 17 / 16 / 15 ms |

See [research/slimsam-cpu-probe-2026-10-10.json](research/slimsam-cpu-probe-2026-10-10.json).
These samples exclude browser transfers, preprocessing, mask resampling and
creative rendering. They suggest caching embeddings for prompt changes on the
same image. They do not support a full-rate live segmentation claim: every new
image still needs encoding. SlimSAM does not provide temporal tracking state.

Reproduce against already downloaded files in a contributor environment with
NumPy and ONNX Runtime 1.24.3:

```sh
python scripts/probe_slimsam_onnx.py \
  --encoder /path/to/vision_encoder_quantized.onnx \
  --decoder /path/to/prompt_encoder_mask_decoder_quantized.onnx \
  --output /tmp/slimsam-probe.json
python scripts/inspect_perception_candidates.py --output /tmp/candidates.json
```

The metadata inspector is standard-library-only, anonymous and does not download
weights or execute upstream source. Its report is not a production model catalog.

## Core integration work before a public provider

1. Split the existing browser asset catalog into per-provider/per-variant
   manifests. It currently installs and verifies the entire upscaler catalog;
   extending that list would force unrelated models to download together.
   Shared runtime files may be reused, while readiness is model-specific.
2. Support the chosen processor/tokenizer/config files through strictly
   allowlisted local routes. For Transformers.js, disable remote model fetching
   in the runtime after explicit verified installation; downloading weights is
   distinct from uploading frames. Pin the JS library as well as ORT and model.
3. Keep each adapter's worker, request queue and load/start/stop/unload states.
   Copy borrowed live frames synchronously, infer on the newest waiting frame,
   discard stale results, and release embeddings/tensors on source changes.
4. Expose source-space observations and masks through ports. Rendering overlays,
   lightweight association/tracking, hysteresis, palette selection and prompt
   routing stay in Genereti. Model-based video tracking can keep provider state
   in Core, with explicit reset, memory limit and lost-track semantics.
5. Test the exact exported checkpoint with direct 2D stream and preview routing,
   non-square geometry, pause/restart, model switch/unload, GPU contention and
   warm/cold timing. Add queued native support only for validated native exports.

For coordination with the MediaPipe session, propose one versioned observation
shape: source ID/revision, frame timestamp, source dimensions, normalized `xyxy`
boxes, label/confidence, optional track ID, backend/model and timings. Masks need
source geometry and object association too; separate overlays from mask data.
This is a proposal to reconcile with that session's actual outputs, not a new
Genereti API. Do not silently convert per-frame detection indices into track IDs.

Roboflow is useful as the upstream RF-DETR project and optional custom-model
export/training tooling. It is not a mandatory hosted runtime for these local
providers. A Roboflow account/API key is not required for the inspected public
RF-DETR checkpoints. Review separately licensed tooling or custom datasets before
adding it; hosted inference and user-media upload remain explicitly opt-in.
