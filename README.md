# GeneretiCore

Local asynchronous inference companion for [Genereti](https://github.com/languel/genereti) and ComfyUI.

**Status: runnable experimental contributor milestone.** Core AI text, vision and scored decisions are implemented. The optional archived SDXS/SD Turbo image runtime is now ported with stable IDs; 512px SDXS/Turbo inference and the live Comfy bridge have been exercised on one Mac. Public converted bundles now download through the generator toolbar without an HF login. Broad student installation, older macOS and the full shader-transition demo remain on the [roadmap](docs/plan.md). Read the [implementation checkpoint](docs/implementation.md) and [local validation record](docs/validation.md) for measured behavior and limits.

## Learn by running a sample

Read [Tutorial 0](docs/tutorial-0.md), or open **Workflows → GeneretiCore → 00 - Tutorial 0 - decision models** and click its book button. Thirteen installed samples explain the result contract, text generation, decisions, vision and Genereti walkthroughs. The d1 demo turns a scene description into an artwork palette through a bounded choice and authored numeric mapping. Each note defines its demo before giving instructions.

Read the [getting-started guide](docs/getting-started.md) for exact steps and troubleshooting. **▷ runs connected workflow outputs; ϟ previews locally inside the inference node.** The header **?** opens authored references in Genereti’s shared Help panel (Reference, Contents, Assistant), or a local reference without Genereti. Samples 05/06/07 use Genereti's p5 editor and step-by-step lesson player; samples 00–04 work without Genereti public.

## Contributor setup

Core AI requires macOS 27+ on Apple silicon. Building the helper requires Xcode 27. No models are bundled. Installation and model execution are independent; other platforms can import the pack and validate decision scores but cannot run Core AI.

Clone this repository into your test Comfy installation's `custom_nodes/genereticore`, then:

```sh
python3 scripts/build_helper.py
```

Restart Comfy. Search **Genereti / Inference** for `ꘅ Local Text`, `ꘅ Local Vision`, `ꘅ Local Decision`, and `ꘅ Decision Scores Validator`. On an inference node, click **↓** to explicitly download the selected pinned model from Hugging Face. Progress is shown in the toolbar. Use **Run** for connected Comfy outputs or **ϟ** for an independent async text/decision preview. **▷** queues the connected workflow. **□** cancels that async task. Comfy interrupt cancels queued execution. No capture or inference starts on workflow load.

Comfy models live under its configured `models/genereticore` path. Compiled Core AI artifacts are managed by the OS/SDK. Model files and helper binaries stay outside Git. A complete verified native release must replace the build step before student distribution through Manager.

## Standalone local tasks

From this checkout:

```sh
python3 -m genereticore.cli doctor
python3 -m genereticore.cli download --model qwen3-0.6b
python3 -m genereticore.cli text --prompt 'Describe a calm scene. /no_think' --repeat 2
python3 -m genereticore.cli decision --prompt 'Choose a palette for a calm scene.' --choices '["blue", "orange"]'
python3 -m genereticore.cli download --model qwen3-vl-2b
python3 -m genereticore.cli vision --image /absolute/path/image.png
```

Standalone model storage defaults to `~/Library/Application Support/GeneretiCore/models`. Set `GENERETICORE_MODEL_DIR` / `--model-dir` to use an existing cache. Set `GENERETICORE_HELPER` / `--helper` for a built helper outside this checkout.

The small Qwen starter is useful for testing integration, but local smoke tests exposed incorrect answers and poor decisions. Its answer-slot probabilities are uncalibrated. Validate model quality before using outputs as creative controls.

## Live API

The Comfy API is loopback-only and same-origin. `GET /genereticore/status` reports capabilities, installed models, busy state and queue depth. Explicit `POST /genereticore/tasks` accepts task/model/inputs/options plus stream ID, input revision and `latest` or `fifo` policy. Poll `GET /genereticore/tasks/{id}?after={cursor}` for events; `POST /genereticore/tasks/{id}/cancel` stops a request. Inputs never go to a hosted inference service.

Async UI completion emits `genereticore:completed` on `window`. The [client module](web/js/client.js) exports the API client and current/next transition primitive. See [API examples](docs/api.md).

## Tests

```sh
python3 -m unittest discover -s tests -v
node tests/test_client.mjs
```

Route tests use aiohttp from the Comfy environment. Bundled samples install on startup without replacing edited copies. Original code is MIT; see [third-party notices](THIRD_PARTY_NOTICES.md) for SDK and model provenance.

## d1 Core ML contributor setup

The optional d1 backend is independent of Core AI: macOS 15+ Apple silicon, Swift 6, `python3 scripts/build_d1_helper.py`. This deployment target is declared by upstream; local tests were on macOS 27. The helper uses pinned MIT FluidUse d1 sources with their license included. Build products and weights stay outside Git. Download `d1-omni-600m` explicitly from Local Decision or the CLI. It supports text decisions only, 2–8 options and at most 256 combined input tokens; long requests fail without silent truncation to a smaller bucket. d1 generates zero output tokens and ignores the Qwen `max_tokens` setting. See [third-party terms](THIRD_PARTY_NOTICES.md) for the weights' LFM Open License.

Example: `python3 -m genereticore.cli decision --model d1-omni-600m --prompt 'A quiet moonlit lake.' --choices '["blue", "orange"]' --repeat 3` after download. Local assets are SHA-256 verified. First compilation/loading is much slower than warm inference. The demo is an integration exercise, not a quality guarantee.

## Realtime SDXS and SD Turbo samples

Samples 09–12 connect Genereti livecode/drawing to Core’s preserved native image IDs and a separate Genereti image preview. They need the updated companion bridge, macOS 14+ Apple silicon, optional image dependencies and the public converted bundles available through ↓. ⓘ links model credits, sources and terms. Students do not convert weights; first-use compilation happens locally. Inference starts explicitly with the generator play glyph; queued mode uses Comfy Run. Do not enable the legacy `genereti_comfy_coreml` pack alongside Core. See [setup and demo controls](docs/realtime-image-demo.md) and [help/UI adoption and validation](docs/help-ui-integration.md). Model workflows have not been run in the cloud.

## Compact image cleanup

The `ꘅ Real-ESRGAN upscale` node provides local AnimeVideo/General cleanup, source-size/2x/4x output and optional same-image refinement on macOS 14+ Apple silicon. Start with **14 - Real-ESRGAN cleanup comparison**. Public verified downloads need no student login. See [setup, measurements and limits](docs/esrgan.md).
