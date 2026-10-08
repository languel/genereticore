# New-session handoff

Repository: /Users/liuboto/dev/genereticore

## User objective

Build an optional Comfy inference extension supporting Core ML and Core AI, eventually portable small local models (including Liquid) and explicitly enabled hosted providers. Keep Genereti lightweight. AI generates/analyses asynchronously while shaders, particles, audio and generative code continue at their own frame rate. Students should install through Comfy Manager and download missing models with UI progress.

## Current state

Only repository scaffolding, architecture and milestone documents exist. No extension, model downloads, inference implementation or performance tests have been done here. Do not describe this as runnable.

Main dev laptop preflight: macOS 27.0.1, Xcode 27.0 build 27A266a, October 7, 2026. Suitable for trying Core AI, not proof that any candidate model runs.

Existing project:
- /Users/liuboto/dev/genereti: private local dev branch, full development features. NEVER PUSH this branch.
- /Users/liuboto/dev/genereti-public: public main, GitHub languel/genereti. Separate clean distribution checkout.
- Native backend: integrations/genereti_comfy_coreml; root engine.py/model_resolution.py and supporting imports. This optional pack is absent from the lightweight Registry package.
- Older integrations/comfyui_genereti bridge uses a separate local server; distinguish it from native Core ML nodes.
- Core ML generator supports macOS 14+ Apple silicon. Current setup uses conversion scripts; aim to replace student conversion with prepared bundles.
- Canonical demos remain integrations/comfyui_genereti/workflows. Public package mirrors them into example_workflows and installs preserving user copies.

## Suggested next action

Read AGENTS.md, architecture.md and plan.md. Inspect existing engine dependencies and upstream CoreAIKit's current release/license/capability matrix. Run the smallest official example before building adapters. Then implement one runnable task path and its Comfy interface. Preserve the current working Genereti installation.

No secrets have been copied. User believes a Hugging Face token is available in the environment. Verify authentication without printing the token when publishing is needed. Model files remain outside Git. No models have been published to Hugging Face from this repo.

Liquid D1 is currently an API model per the linked release, not a confirmed local downloadable checkpoint. User may have seen a newer weights announcement on X: recheck official channels. APIs are not a current priority; keep hosted providers out of initial implementation. Ask before any later user-media transmission or provider costs.
