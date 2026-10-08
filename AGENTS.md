# GeneretiCore agent instructions

- Read docs/handoff.md and docs/plan.md before implementing.
- This repository is currently a planning scaffold. Do not claim installability or working inference until tested.
- Preserve /Users/liuboto/dev/genereti (private dev branch) and /Users/liuboto/dev/genereti-public (public main). Do not push private Genereti dev or copy its embedded Strudel into this repository.
- Existing Genereti is a working system: do not remove its backend until replacement and migration are verified.
- Core ML generator requires macOS 14+ Apple silicon; Core AI experimental runtime currently requires macOS 27+. Check real availability, never silently fall back to cloud.
- Keep model weights, converted/compiled packages, caches, captures, credentials and private data out of Git.
- Do not inspect or print token values. Use credentials through SDKs; never persist them in workflows or source.
- Local inference is the default. Hosted calls and user-media uploads require explicit user authorization.
- Use upstream SDKs and standard model formats where practical, pin versions and record licenses and provenance.
- Preserve existing native Core ML node IDs when migrating. Avoid registering duplicates beside the existing pack.
- Bind any native helper to loopback; camera/screen/audio capture remains explicitly user-started.
- Keep heavy model work off browser rendering/audio threads. Bound work queues and make stale-result behavior explicit.
- Benchmark actual warm and cold paths alongside creative rendering; distinguish model-card reports from local measurements.
- Use Genereti docs/node-ui-design.md for custom controls: glyphs, hover tips, accessible state, borderless toolbar controls.
