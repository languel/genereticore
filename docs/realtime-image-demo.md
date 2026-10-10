# Realtime image demos

Four graphs in `example_workflows` combine Genereti creative inputs with
GeneretiCore's migrated native image generators:

| Workflow | Input | Generator mode |
| --- | --- | --- |
| 09 - Livecode to SDXS | Authored moving p5 sketch | SDXS sketch |
| 10 - Drawing to SDXS | Interactive drawing | SDXS sketch |
| 11 - Livecode to SD Turbo | Authored moving p5 sketch | SD Turbo image |
| 12 - Drawing to SD Turbo | Interactive drawing | SD Turbo image |

The workflows contain no weights. On October 10, 512px SDXS sketch and Turbo
image/Canny produced visible images through the live Comfy bridge on one Apple
silicon Mac. Turbo samples default to image mode to match the public hosted
bundle; optional Canny still requires separate control weights. Broader parity,
older OS testing and sustained performance measurements remain pending. The image preview keeps the last completed frame during
inference.

## Contributor setup on the Mac

Use Genereti with the companion browser bridge and this GeneretiCore version in
Comfy's `custom_nodes`. Move the old `genereti_comfy_coreml` folder/symlink outside
`custom_nodes` before enabling Core: both own the same stable IDs
`GeneretiSDXSGenerate` and `GeneretiSDTurboGenerate`. Core rejects that duplicate
installation before registering routes. Keep the archive and your saved workflows
and models; no old backend files are removed.

Native image inference requires macOS 14+ Apple silicon. In Comfy's Python install
this checkout's optional image runtime (`python -m pip install -e '.[image]'`).
Comfy supplies Torch; do not replace its Torch build with conversion dependencies.
Core AI and d1 helpers are independent and are not needed for these image graphs.

Point Comfy's `genereti_coreml` extra model folder to your existing converted
Genereti bundle root. Explicit configured paths take precedence. Otherwise Core
reuses `ComfyUI/models/genereti` if present, or discovers
`ComfyUI/models/genereticore/images`. A bundle is a numeric size directory:

- Every usable size needs `unet.mlpackage`, `encoder.mlpackage`, `decoder.mlpackage`.
- SDXS sketch additionally needs `controlled_unet.mlpackage`; anime uses
  `anime_unet.mlpackage` and `anime_controlled_unet.mlpackage`.
- Turbo needs `turbo_unet.mlpackage`. Canny additionally needs
  `control_canny.mlpackage` and `turbo_residual_unet.mlpackage`.
- Depth/pose modes need their corresponding control packages; depth preprocessing
  also requires the pinned depth model already cached locally.

The denoiser dropdown shows relative installed package paths and filters modes by
companions. Complete bundles carry `assets/sdxs/{tokenizer,text_encoder}` and
`assets/sd-turbo/{tokenizer,text_encoder}` beside the numeric size directory. The
engine prefers those assets and supports previously cached tokenizer/text encoder
assets for `IDKiro/sdxs-512-dreamshaper` at revision
`76f720262bb051da75666b22c902a78c8e16c763` and, for Turbo,
`stabilityai/sd-turbo` at `b261bac6fd2cf515557d5d0707481eafa0485ec2`.
Those reads use `local_files_only=True`; there is no implicit download. For complete
pinned public downloads, use ↓ on the generator toolbar or the contributor
installer in [model-distribution.md](model-distribution.md). ⓘ opens retained
credits and terms. Canny is not mirrored; see [source setup and alternatives](image-license-review.md). Conversion instructions and
model provenance remain in Genereti's `integrations/legacy-generator/docs/models.md`.

Restart Comfy after Python changes; refresh the frontend after browser changes.
Samples install into Workflows → GeneretiCore while preserving edited copies.
They can also be opened directly from this repository.

## Running and displaying

Select an installed model package. Turbo image samples use strength 0.95 for a
visible transformation; 0.65 preserved much of the simple black-and-white input
in this test. Canny is the optional path for stronger silhouette guidance. Livecode evaluates its authored drawing
independently; drawing is immediately editable. Leave source, generator and viewer
in Live, then explicitly press the generator's play glyph. A new workflow never
starts inference. Queue mode uses Comfy Run for one frame and updates the metrics
viewer. Live timings appear on the generator itself.

The browser sends one request at a time to loopback-only
`/genereticore/coreml/generate`; the server returns busy for overlapping live work.
Queued and live calls share the same locked engine. Pause prevents new live work;
already-running native inference finishes and its stale result is discarded.
Models stay warm in the cached engine. The latest source is captured for the next
request; no growing frame queue is retained.

Prompt typing applies immediately by default. The lightning toggle holds a draft;
Send or Cmd/Ctrl+Enter commits it. Draft and applied prompt are saved separately.
Preview freeze/minimize, overlay and Alt-O belong to the separate Genereti viewer;
they change display without claiming to stop inference.

The migrated generator UI requires the updated Genereti browser bridge for Live.
Without it the Python nodes still support queued inference. The native node IDs
and input/output order are preserved; mode/package compatibility remains explicit.
The legacy live endpoint stays in the archive; Core uses its own route namespace.

Rebuild graphs without a running server:
`python scripts/build_image_demos.py /path/to/public/genereti`.


## Blank-canvas performance controls

Both generator nodes have a saved, initially disabled **Blank input** option.
Expand its chevron to choose an alternate prompt or **Solid white**. The option
checks the original composited IMAGE before guide processing/inversion: each RGB
channel must vary by no more than 3/255 over the whole frame. A contrasting mark,
even one pixel, restores the main prompt. Text mode bypasses this check.
Alternate-prompt generation can still add texture; Solid white bypasses inference
and publishes exact white at the selected native model size. The setting is
shared by Live payloads and queued workflow metadata; main/held prompts are kept.

Local verification: SDXS and SD Turbo, 512px, blank → alternate prompt, blank →
exact white (all output channels 255; zero model time), marked → main prompt.
Queued graphs also produced exact white using their saved node properties.
Browser verification covered the enabled option, action selector, collapsible
field, and inline dot/timings. Credits and license links live in each node's
reference documentation rather than its toolbar.
