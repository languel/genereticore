# New-session handoff

Repository: /Users/liuboto/dev/genereticore
Companion: **/Users/liuboto/dev/genereti-public** (user-confirmed).

## Objective and current state

Build an optional local inference companion for Comfy/Genereti while shaders, particles and audio continue independently. The repository now contains a runnable experimental contributor milestone: Core AI text, vision and scored decisions; standard Comfy nodes; isolated warm Swift helper; bounded asynchronous scheduler; explicit model downloads with pinned SHA-256 artifact verification; local same-origin API; compact glyph controls; CLI and example workflows.

Read [implementation.md](implementation.md), [validation.md](validation.md), [architecture.md](architecture.md) and [plan.md](plan.md). This is **not** completion of the entire distribution roadmap. No Manager/Registry/student-install or image-generation migration claims are warranted.

## Verified local setup

macOS 27.0.1, Xcode 27.0 (27A266a), 128 GiB Apple silicon. CoreAIKit exact 0.7.3 was cloned into `/tmp/genereticore-coreai-kit-073`; its official ChatDemo succeeded. The native helper builds via `python3 scripts/build_helper.py`; generated binary `native/bin/genereticore-helper` is ignored. Keep atomic executable replacement to avoid macOS rejecting updates to a mapped signed inode.

Qwen3 0.6B and Qwen3-VL 2B pinned artifacts are downloaded into `~/Library/Application Support/CoreAIKit/Models` for experiments. Default standalone cache is instead `~/Library/Application Support/GeneretiCore/models`; Comfy uses its configured `models/genereticore`. Use `--model-dir` or `GENERETICORE_MODEL_DIR` to reuse the verified test cache.

Isolated Comfy test base: `/tmp/genereticore-comfy-test`, node symlink to this checkout, loopback port 8003. It uses the installed Comfy Python at `/Users/liuboto/Documents/ComfyUI/.venv/bin/python` and source `/Users/liuboto/ComfyUI-Installs/ComfyUI/ComfyUI`. Existing production Comfy and companion checkouts were preserved. Tests: Comfy Python `-m unittest discover -s tests -v`; `node tests/test_client.mjs`; explicit live server `python3 scripts/smoke_comfy.py`.

## Key limitations

Small Qwen text and decision quality was poor on some fixtures, even though inference/structured output works. Do not equate runnable inference with correct reasoning. Current decisions use typed answer-slot softmax, explicitly uncalibrated. Vision correctly described the synthetic shape fixture; model tests are limited.

Legacy native Core ML lives in the public companion under `integrations/legacy-generator`. It retains `GeneretiSDXSGenerate` and `GeneretiSDTurboGenerate`; this pack does not duplicate them. Core ML migration and a real drawing → generation → shader demo remain next steps, with local model bundle/license audit before distribution. Do not remove the old working backend.

## Remaining work

Finish incremental Core ML migration with stable IDs and verified parity; audit/prepare complete SDXS bundles; benchmark alongside creative rendering; implement the actual shader transition demo; evaluate local Liquid d1 runtime/license and quality; ship a verified native helper release with complete SDK/transitive notices; test clean Manager installation and downloads/restart recovery before publication. Hosted providers and uploads remain separately authorized later work. No credentials were read or copied; no cloud inference or user-media upload was performed.

## Beginner samples and walkthroughs

Six numbered graphs now install into each existing Comfy profile under Workflows → GeneretiCore. The installer preserves edits and backs up replaced/retired unchanged samples. `docs/getting-started.md` and `web/getting-started.html` teach top Run versus local preview. Node ▷ queues the connected graph; ϟ submits a separate local preview. Inference and new `GeneretiCoreResult` sinks show read-only answers. `GeneretiCoreChoiceValue` maps allowed labels to finite numeric controls.

The isolated port-8003 test now also links public Genereti. Samples 04/05 contain four-step authored lesson nodes with manual startup. p5 artwork starts on open, but inference starts only on explicit Run. Use `paletteHue`, not p5's built-in `hue` name. The user's original graph was preserved as `My GeneretiCore experiment` in that test profile.

## d1 and theory-first lessons (2026-10-08)

Text-only d1 Core ML is now integrated via a separate macOS 15+ helper (`python3 scripts/build_d1_helper.py`), independent of the macOS 27 Core AI helper. Two unmodified MIT FluidUse source files are pinned to PR 27 commit e55561ab, with license in the source tree. Weights are revision 8ae382b1, six checksum-pinned assets including LICENSE, stored outside Git. The catalog/router, existing Decision node and CLI support `d1-omni-600m`, 2–8 options, a separate question and 256 combined input tokens. Prediction defaults to CPU + Neural Engine. Restart the isolated server after Python edits; refresh frontend for viewer edits.

Read `docs/tutorial-0.md` for the student introduction, rendered locally at `web/tutorial-0.html` by `scripts/build_guide.py`. Eight numbered examples replace the old six; managed unchanged retired files are backed up and edited copies preserved. The user's edited old sample with a DAT table is separately saved as `GeneretiCore/My decision lesson experiment.json` in the test profile. The new d1 demo is 07; its lesson node belongs below the result row at y1480. Node types appear in real-type titles and the Parameters `node_type` field. Info tab has conceptual descriptions. JSON views are local Tree/Pretty/Minified with collapse state and saved mode.

The first d1 local compile/load took 25.0s, first full request 25.46s, warm complete requests 5.5–6.3ms on this Mac. Compiled-cache reload was ~1.08s model load / 1.38s complete first request. A moonlit-lake input selected blue. A warm-festival input still selected blue (0.68); do not promise a color switch or correct artistic judgment. Long-input rejection was verified (1021 vs 256 tokens). Further creative quality/cancellation/loading and older-macOS testing remain before release claims.

Validator input errors now return inline UI feedback and silent `ExecutionBlocker(None)` outputs. The strict model contract remains unchanged. The frontend marks downstream GeneretiCore JSON viewers as not updated to avoid presenting a previous answer as current. Correcting JSON restores ordinary outputs on the next Run.

Compact viewer UI: node_type is metadata only, with no widget row. The native main-dot/Info description starts with the saved class name. Tree/Pretty/Minified uses a 30px themed native customizable select: selected outline glyph and chevron when closed, glyph plus label in its menu, accessible name and selected-mode hover tip. Older browsers retain a labeled native select. Mode persistence and read-only data remain unchanged.

Visible node families use ꘅ for GeneretiCore and ꘇ for Genereti. Class names/catalog identifiers remain Latinized. Always list actual node labels in tutorial notes and name the target label in each walkthrough step. Sample titles map companion classes to ꘇ livecode, ꘇ image preview and ꘇ lesson; saved legacy family titles are compacted on configure, while authored custom titles remain intact.

The public companion shared node-label formatter now recognizes GeneretiCore as a distinct family and collapses repeated ꘇ/ꘅ prefixes to the correct single glyph. Both formatters are idempotent so configure/reload cannot accumulate prefixes.

## Cloud help/UI and image workflow handoff (2026-10-09)

Authored help now lives in `help/docs`, with synchronized native web Markdown and a bundled catalog. Core registers it with the updated public Genereti shared Help bridge. See `docs/help-ui-integration.md` for the API and cloud checks. Compact controls, header help and viewer freeze/minimize are adopted; presentation reordering retains positional save values.

The archived native image source is ported into `genereticore/image` with stable `GeneretiSDXSGenerate`/`GeneretiSDTurboGenerate` IDs and Core-family labels. An active legacy `genereti_comfy_coreml` installation is rejected before routes are registered. Existing bundle roots and explicit model paths are reused; the archive is untouched. Core routes use `/genereticore/coreml`. Four new samples 08–11 cover livecode/drawing with SDXS/Turbo. See `docs/realtime-image-demo.md`. No cloud models, weights or native inference were run. Mac parity, full Comfy UI checks, complete bundle distribution and current/next shader transitions remain unverified.
