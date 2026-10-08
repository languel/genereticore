# GeneretiCore

Experimental local-first inference for creative coding and ComfyUI.

GeneretiCore is the planned optional inference companion to [Genereti](https://github.com/languel/genereti): image generation/editing, visual analysis, language generation, and structured decisions. Genereti handles live rendering, shaders, audio, transport and transitions; GeneretiCore will supply asynchronous model results.

**Status: architecture checkpoint, not an installable Comfy extension yet.** No models or inference runtime are bundled. Nothing needs to be installed to read this plan.

## Start here

- [Implementation plan](docs/plan.md)
- [Architecture](docs/architecture.md)
- [New-session handoff](docs/handoff.md)

The first demonstration will generate images asynchronously while a Genereti shader transitions between the previous and next result. Analysis and decision nodes will emit structured values and completion events for creative controls.

## Backends and platforms

- Core ML: preserve the existing working Genereti SDXS path, macOS 14+ on Apple silicon.
- Core AI: experimental native backend, currently macOS 27+; development requires Xcode 27. Local machine preflight on October 7, 2026: macOS 27.0.1, Xcode 27.0 (27A266a). Runtime compatibility and performance have not yet been tested.
- Portable local runtimes: evaluate small Liquid models without requiring Apple-specific conversion.
- Hosted providers: optional explicit opt-in; Liquid hosted D1 is a candidate; downloadable d1-3B/d1-omni are separate local candidates. No weights are bundled.

## Distribution

Keep code on GitHub, publish the eventual Comfy extension through Comfy Registry, and host redistributable model bundles on Hugging Face. Students should install the extension through Manager and download missing model components from its UI. Conversion tools are for contributors, not a prerequisite for students.

## License

Our original code and documentation are MIT licensed. Reused code retains its original notices. Model weights, tokenizers, and other assets have their own upstream terms; conversion does not change their licenses. No blanket MIT claim applies to models.
