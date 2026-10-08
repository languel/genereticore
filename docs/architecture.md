# Architecture proposal

One task interface, multiple capability-aware backends. This is a proposal, not an implemented API.

## Components

1. A Comfy extension registers task nodes, settings, model catalog/download UI, standard queued execution, and an optional realtime connection to Genereti.
2. A backend layer implements Core ML, Core AI and subsequently portable local runtimes. A native helper process is a candidate for isolating Swift SDKs and model work from Comfy's Python environment; decide after a working upstream smoke test.
3. Hugging Face stores versioned model bundles. A catalog pins repository revision, artifact checksums, byte sizes, license/provenance, input/output contract and minimum platform/runtime. Download into Comfy's configured model paths, validate safely, and atomically install. Cache compiled artifacts separately.
4. Genereti consumes results through live streams without waiting for the Comfy execution queue. Ordinary Comfy IMAGE/text outputs remain available when explicitly queued.

## Proposed task contract

Tasks: image.generate, image.edit, vision.analyze, text.generate, decision.evaluate.

Requests carry task/request IDs, backend/model selection, input revision, inputs and task options. Events include download/load progress, started, partial text, completed, canceled and failed. Results carry typed content, timestamps and timings. Backend capabilities declare supported tasks, streaming, cancellation and structured-output support. Do not imply identical controls or model portability across backends.

Keep model sessions warm. Permit one active request plus a bounded pending policy: latest-wins for live observations, explicit bounded FIFO for composition jobs. Never silently queue every video frame. Ignore obsolete responses by request/input revision; distinguish result suppression from actual backend cancellation.

## Creative bridge

Use an explicit user-started live mode. Hold the last completed image while generating another. A current/next pair feeds a transition controlled by continuous phase or a musical trigger. Retain next results until the selected beat/bar boundary. Analysis returns timestamped text/JSON/values; decision outputs are constrained labels, probabilities or scores, validated before driving controls. A decision result does not execute arbitrary code.

Comfy's queued execution, Genereti's animation time and musical time remain separate. GPU inference can contend with shaders: expose latency, result age, busy state and queue depth, then benchmark shared workloads.

## Reuse

- Apple model formats: .mlpackage for Core ML, .aimodel for Core AI. These standardize graphs and weights, not application preprocessing or a complete diffusion pipeline.
- CoreAIKit: evaluate download/cache/chat/vision/speech support through pinned public APIs; inspect its capability matrix before assuming guided decisions or tool calls.
- Diffusion: evaluate Apple's Core AI diffusion pipeline and the zoo's editing extensions separately from CoreAIKit.
- Keep copied upstream code and notices identifiable. Prefer dependencies over wholesale forks when packaging permits.

No automatic cloud fallback. Hosted adapters are separately enabled, show where inputs go, and read credentials from protected local settings/environment.
