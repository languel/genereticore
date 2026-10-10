# Help and UI integration

The October 9 Genereti handoff is adopted from public Genereti commit
`26d678139324baaffae6bb2d4fae0351588d8146`. Canonical source:
[genereticore-ui-handoff.md](https://github.com/languel/genereti/blob/main/docs/genereticore-ui-handoff.md).

Core authors native references in `help/docs/<NodeID>.md`. Run
`python scripts/sync_node_references.py` to bundle `web/node-references.json` and
native Info copies in `web/docs`; `--check` detects stale outputs. Every installed
Core node and both preserved native image IDs have an authored page. Welcome
states platform/runtime requirements and contributor limitations. Tutorial 0 is
also indexed as a reading guide.

The companion changes in Genereti expose two browser bridges:

- `window.generetiReference`: `registerDocuments(documents)`, `toggle(node,button)`
  and `showDocument(document)`. `genereti-reference-ready` announces availability;
  `genereti-reference-catalog-changed` refreshes Contents after registration.
- `window.generetiCompanion` version 1: `publishLive`, `attachExecutionMode`,
  `visualNodeControls`, `ensureControlStyle`. `genereti-companion-ready` announces
  availability. Core does not hardcode the other pack's extension URL aliases.

Core loads its catalog relative to its own browser module. Both load orders work:
it registers immediately when the bridge exists, or on the ready event. Header ?
uses the shared panel's same-button toggle, Escape, Auto selection following,
Contents and Assistant context. Asking prepares a draft without sending. Without
Genereti, ? uses a local Markdown dialog with Escape; it does not invent a second
assistant. Comfy's native Info can use the generated Markdown copies.

Custom controls use 20px buttons, 14px SVG or 12px text glyphs, 6px radii, zero flex
gap, host colors, native title tips, accessible names/states and visible focus.
Header ? has an 8px right inset. Result surfaces are transparent and frameless;
local freeze/minimize is independent of inference. Shared Alt-O controls preserve
the existing surface and port positions when the companion is available. Transport
comes before result preview, then parameters; positional serialized parameters
retain their established order. Port names and stable class IDs remain unchanged.

## Cloud validation (October 9, 2026)

- 26 Python unit tests: existing contracts/scheduler/download/route/examples plus
  image package discovery, installed mode filtering, stable schema input order,
  platform guard and loopback/same-origin boundaries. Torch/Comfy are stubbed for
  image contract tests; no model is loaded.
- JS client stale-result and transition tests, plus widget presentation/save/reload
  order tests.
- Genereti reference index, context, selection-following and family-label tests.
- Chromium with a lightweight Comfy host harness: Core catalog registration into
  the actual shared Help modules, searchable d1 reference, header size/inset,
  same-button close, reference context handoff without sending, Escape in the
  assistant composer, retained draft and local preview freeze/minimize.
- Python compilation, browser module syntax, workflow JSON/link integrity and both
  reference catalogs' synchronization checks.

This is not a full Comfy frontend exercise. In-place Alt-O movement, invisible
socket connections, zoom sizing, dynamic shader sockets and native Mac image
inference parity remain local validation work. No weights were downloaded, no
model workflows were run, and no student-install/distribution claim is made.
