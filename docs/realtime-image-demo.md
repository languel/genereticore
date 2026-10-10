# Realtime image demos

Four graphs in `example_workflows` combine Genereti creative inputs with
GeneretiCore's migrated native image generators:

| Workflow | Input | Generator mode |
| --- | --- | --- |
| 08 - Livecode to SDXS | Authored moving p5 sketch | SDXS sketch |
| 09 - Drawing to SDXS | Interactive drawing | SDXS sketch |
| 10 - Livecode to SD Turbo | Authored moving p5 sketch | SD Turbo Canny |
| 11 - Drawing to SD Turbo | Interactive drawing | SD Turbo Canny |

These are model-free workflow files, not cloud-tested inference demos. The
migration preserves the archived engine's operations, IDs and package layout;
local Mac parity and performance must still be checked. No realtime rate is
promised. The image preview keeps the last completed frame during inference.

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
companions. The engine also reads previously cached tokenizer/text encoder assets
for `IDKiro/sdxs-512-dreamshaper` at revision
`76f720262bb051da75666b22c902a78c8e16c763` and, for Turbo,
`stabilityai/sd-turbo` at `b261bac6fd2cf515557d5d0707481eafa0485ec2`.
Those reads use `local_files_only=True`; there is no implicit download. Reuse the
working archive's cache and bundles. This change does not provide a complete
bundle downloader or establish redistribution rights. Conversion instructions and
model provenance remain in Genereti's `integrations/legacy-generator/docs/models.md`.

Restart Comfy after Python changes; refresh the frontend after browser changes.
Samples install into Workflows → GeneretiCore while preserving edited copies.
They can also be opened directly from this repository.

## Running and displaying

Select an installed model package. Livecode evaluates its authored drawing
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
