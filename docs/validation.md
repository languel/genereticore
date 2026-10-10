# Local validation — October 7, 2026

## Desktop merge verification (October 9, 2026)

The cloud Help/UI/image migration was merged locally into the contributor
checkout and tested with Comfy Desktop on port 8188. Shared Help navigation,
unsent guide-context drafts, validator recovery, viewer modes/freeze/minimize
and all four migrated image graphs were exercised in the browser. A fresh browser
session after the server restart was needed to register the migrated native nodes.
All four graphs loaded without missing-node placeholders. Native image inference
remains unverified: no complete image bundle is installed in this instance, and
Start reported `Invalid model path.` without an implicit download.

The arcade's explicit d1 Download button installed and verified the pinned
769,088,919-byte package outside Git. Actual local d1 playback reached 35 pieces;
one warm placement request reported 23.3 ms prediction / 24.9 ms end-to-end and a
music request 9.2 / 10.1 ms. These are individual observations with canvas
rendering active and audio off, not a throughput or decision-quality benchmark.
The first run compiled locally; its complete cold timing was not captured.
The run exposed a one-candidate edge case, now handled by taking the sole legal
placement without calling a model that requires at least two options.
Browser replay verified the sole placement was taken and the game stopped normally
at top-out after 36 pieces. It cleared zero rows on this seed, so successful
inference does not establish good gameplay. Rotation is chosen before each drop;
the current demo does not animate turning or lateral movement.

26 Python tests and the existing client/layout JavaScript checks passed.
Comfy startup/asset console warnings were present, so this is not a clean-console
claim. Clean student installation, helper distribution and image bundle downloads
remain outstanding; see [model-distribution.md](model-distribution.md).

Hardware: Apple silicon, 128 GiB unified memory. macOS 27.0.1 (26A434), Xcode 27.0 (27A266a). CoreAIKit 0.7.3, commit f32626037741222c17042cd1bc0301185c077e8e. ComfyUI 0.39.2, frontend 1.53.10, Python 3.12.11. Test Comfy ran on 127.0.0.1:8003 with an isolated `/tmp/genereticore-comfy-test` base; the companion and existing Comfy installations were not modified.

## Actual inference

The pinned upstream ChatDemo CLI built and ran locally, returning Tokyo. GeneretiCore's release helper then ran text, decision and vision tasks through process pipes. All model assets stayed in the external SDK cache; no media was uploaded. The vision fixture was a generated 256×256 orange circle on blue, not user media.

Representative single samples; these are not statistical benchmarks or shared-rendering tests:

| Task | First helper session | Warm session | Evidence/limit |
| --- | ---: | ---: | --- |
| Text, 11-token answer | 1,838 ms | 52 ms | Tokyo on this prompt; helper footprint about 399/420 MB |
| Decision, two labels | 342 ms | 15 ms | Finite normalized scores; wrong semantic choice on this fixture |
| Vision, 64-token cap | 7,773 ms | 1,111 ms | Correctly described the orange circle on blue both times |

“First” means a new model session in a new helper process with downloaded weights. Text had already been loaded by the official smoke test, so the OS compilation cache was warm. These are helper task wall times, including native load; earlier samples precede the final Python `end_to_end_ms` instrument. They do not include download, Python artifact hashing or queue waiting. A final fresh-helper text run measured 735 ms end-to-end (421 ms native) and 51 ms warm end-to-end (49 ms native), with the already-warmed OS cache. The final adapter reports end-to-end backend latency separately; queue-wait latency is an event. `first_response_ms` measures first emitted answer text, not first internal thinking token. No near-realtime claim follows from these samples.

The SDK download path completed Qwen3-VL's pinned decoder + vision tower in about 62 seconds; the catalog records 3,278,324,251 bytes for 14 files, including tokenizer and metadata. Qwen3 0.6B records 351,561,081 bytes for 11 files. All manifest SHA-256 values were obtained from pinned upstream LFS identifiers or hashed small files. Subsequent local verification passed. These exact manifest totals supersede model-card/catalog size estimates.

Quality is a real limit: one queued Qwen text test incorrectly answered Osaka as Japan's capital. The starter decision test selected orange despite an instruction for blue. Guided JSON generation also failed on the small model; the implemented decision path instead uses the SDK's `TypedDecisions` answer-slot logits and validates its typed scores. That fixes output structure, not decision accuracy. The returned distributions are uncalibrated. A better decision model and a task-quality fixture suite are required before presenting this as a reliable creative director.

## Integration and regression checks

- Four nodes registered in a real isolated Comfy server; no legacy Core ML IDs registered.
- Comfy queued text and decision execution completed with normal outputs and UI results.
- Browser node discovery, compact toolbar and explicit asynchronous submission visibly worked; status reached `ready` after completion. Workflow load started no task.
- `scripts/smoke_comfy.py` passed latest-wins suppression, explicit active cancellation, helper restart and queued decision execution.
- Unit tests cover queue bounds/order, pending replacement, stale active suppression, cancellation, bounded event retention, revision checks, decision labels/nonfinite scores, corruption/path traversal/symlink rejection and loopback/same-origin guards.
- JS test covers current/next holding, bar versus beat triggers, phase promotion and old-result rejection.
- Helper build and code-signature verification succeeded. The contributor build now atomically replaces its executable rather than overwriting a mapped signed inode; overwriting had caused macOS signature rejection during development, and the atomic replacement passed subsequent vision/integration tests.

## Initial milestone limitations (before the d1 integration below)

No Manager install, Registry publication, clean student setup without Xcode, redistributed helper/model bundle, Core ML migration, live SDXS shader loop, rendering/audio contention benchmark, FLUX, Liquid d1, hosted provider, physical capture or cloud inference was tested. Native framework errors remain native errors; no fallback disguises them.

## Beginner workflow verification (2026-10-08)

All six teaching graphs completed local Comfy executions on the isolated port-8003 instance. Samples 00–03 were queued through the API; 04/05 were queued from their loaded browser graphs with Genereti public linked. Browser verification showed the model-free connected results, an orange shape on blue with a matching vision description, and a decision of `orange` mapped to 30 driving the live p5 artwork. Both authored learner guides opened; Previous/Next navigation was checked. The node help button opened the served offline getting-started page.

18 Python unit tests passed, including safe managed workflow updates/retirement, edited-copy preservation, graph links and lesson targets, and finite palette mappings. Client boundary/phase/stale-result checks and frontend module syntax passed. Captures remain ignored local evidence under `captures/`. These runs establish contributor samples on this machine, not clean student installation or model decision quality.

## d1 integration and beginner viewer (2026-10-08)

Pinned FluidInference d1 text assets (769,088,919 bytes including tokenizer/config/license) downloaded outside Git and passed manifest SHA-256 verification. The separate Swift 6 helper built from two unmodified MIT upstream source files at FluidUse e55561ab. Tested on this Mac's macOS 27.0.1 Apple silicon; the macOS 15 deployment target is not an older-OS test result.

First compilation/loading: load 25,027.8ms, prediction 15.1ms, complete request 25,461.4ms. Next same-helper requests: predictions 5.4/4.9ms and complete requests 6.3/5.5ms. Cached-package first load in the Comfy service: load 1,077.9ms, prediction 11.2ms, complete request 1,380.2ms. Compute units: CPU + Neural Engine. d1 reported zero generated tokens. These are short-input local measurements, not creative-load throughput guarantees.

A moonlit lake selected blue. A scene explicitly composed of orange lights/walls/sunset selected orange (0.998). An energetic warm festival still selected blue (0.680), demonstrating a creative-quality limitation. Temperature scaling does not certify this task. A 1,021-token request was rejected against the 256-token bucket limit. The API catalog and existing decision node route to the model-selected backend without cloud fallback.

Browser checks verified the d1 graph's queued decision reaching its connected JSON result, numeric palette mapping and live p5 output. Tree scores collapse independently; Minified has one line and Pretty has indented lines; mode switching preserves the same data. Parameters contains node_type and Info contains the conceptual description. The original user graph with its DAT table was saved separately before frontend updates. The automated suite now has 20 passing Python tests including text-only capability/choice limits and backend routing/release, plus existing client boundary/phase/stale-result tests.

Remaining release work includes older macOS testing, wider decision quality/parity evaluation, cancellation/timeout cases specific to d1, and longer benchmarks alongside creative rendering. The current examples are contributor demonstrations, not a student-ready binary release.

Final queued artwork check: the moonlit scene returned blue (0.9986), then editing only the state to the explicit orange fixture returned orange (0.9992) and visibly changed both p5 previews. The second request ran alongside the live circle: 20.9ms prediction / 23.3ms end-to-end; this single observation is not a contention benchmark. The final graph separates the learner guide below the result row. Tutorial 0 opened through its book button and rendered the theory locally.

Graceful validator check: mismatched selected labels and malformed JSON both completed the Comfy queue without an execution-error dialog. Inline feedback explained the correction; downstream GeneretiCore viewers replaced stale answers with “Not updated”. Correcting the fixture restored normal output in the same graph. 23 Python tests pass, including silent blocker behavior and recovery.

Compact viewer UI: node_type is metadata only, with no widget row. The native main-dot/Info description starts with the saved class name. Tree/Pretty/Minified uses a 30px themed native customizable select: selected outline glyph and chevron when closed, glyph plus label in its menu, accessible name and selected-mode hover tip. Older browsers retain a labeled native select. Mode persistence and read-only data remain unchanged.
