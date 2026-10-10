# Third-party provenance

Original GeneretiCore source is MIT. Model assets are not MIT and are not included in this repository.

- CoreAIKit 0.7.3 (`f32626037741222c17042cd1bc0301185c077e8e`): https://github.com/john-rocky/coreai-kit/tree/0.7.3 — BSD-3-Clause. Used through Swift Package Manager, not copied into this source tree. Redistribution of a helper binary must include its LICENSE and NOTICE.txt and notices/licenses for the transitive packages in Package.resolved.
- Native SDK dependencies include john-rocky/coreai-models, Hugging Face swift-transformers, swift-huggingface and swift-jinja, Apple swift-collections, swift-crypto and swift-asn1, EventSource, yyjson and XGrammar. Their exact revisions are in native/Package.resolved; contributor builds fetch their original license files. A redistributable native binary release requires a complete bundled notice inventory.
- Qwen3 0.6B: https://huggingface.co/Qwen/Qwen3-0.6B — Apache-2.0 upstream weights. Core AI conversion from mlboydaisuke/qwen3-0.6b-CoreAI-official, pinned in the catalog.
- Qwen3-VL 2B Instruct: https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct — Apache-2.0 upstream weights. Core AI conversion from mlboydaisuke/Qwen3-VL-2B-CoreAI, pinned in the catalog.

Pinned manifests describe downloaded upstream artifacts; they do not grant redistribution rights. Weights download directly from upstream for the user's local experiments. Public audited SDXS, SD Turbo and compact Real-ESRGAN converted bundles are now published separately from source, with pinned downloads, model-specific terms and full credits. See docs/image-license-review.md and docs/esrgan.md.

- FluidUse d1 runtime: `e55561ab32a43d9a70e6531bedc3a05a5e502201` from https://github.com/FluidInference/FluidUse/pull/27, MIT. Two unmodified upstream source files (`D1OmniManager.swift`, `D1OmniTokenizer.swift`) are vendored under `native/d1/Sources/GeneretiD1Helper/Upstream` with the full MIT LICENSE. This isolates the decision runtime from the SDK's unrelated capture/accessibility/audio modules and dependencies. The surrounding helper and Python downloader are original code. Revisit the pin when the PR lands.
- Liquid d1-omni weights: LFM Open License v1.0, not MIT. Text-only Core ML conversion from FluidInference/d1-omni-600m-coreml, pinned to `8ae382b1f2e5b9b7e33008515a40df4ecdfcebdb` with per-file sizes/SHA-256 in the catalog. The manifest downloads the upstream LICENSE alongside assets. Commercial use has a revenue restriction; redistribution requires license/attribution preservation. Weights and compiled packages stay outside Git.

Legacy SDXS/control/anime/Turbo assets have separate model-specific terms and remain outside this runtime.

## Migrated Genereti image runtime

`genereticore/image/{engine,guides,model_resolution,postprocess,nodes,live}.py`
are adapted from the MIT-licensed public `languel/genereti` archive
(`integrations/legacy-generator`, source commit recorded in
`docs/help-ui-integration.md`). This migration includes source only. It conveys
no model weights or new model redistribution rights. The optional runtime pins
match the archive for Core ML, Transformers, Hugging Face Hub, NumPy, Pillow and
OpenCV; Torch is supplied by Comfy. SDXS/DreamShaper, SD Turbo and optional guide
models retain their upstream licenses and require an individual bundle audit
before distribution; the public bundle reviews are recorded in docs/image-license-review.md. No conversion-only Diffusers/PEFT dependency is added.

## Compact Real-ESRGAN

The contributor SRVGG conversion follows the BSD-3-Clause Real-ESRGAN architecture by Xintao Wang and contributors. Full notice: licensing/Real-ESRGAN-LICENSE.txt. Official weights and independently converted packages remain outside Git; public model provenance and terms are in docs/esrgan.md and the HF bundle.
