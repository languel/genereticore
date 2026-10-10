# Blocks & Beats in a Comfy webview

Open **Workflows → GeneretiCore → 13 - Blocks and Beats - embedded webview**.
This example needs both Genereti's `ꘇ webview` (`GeneretiDocument`) and
GeneretiCore's existing arcade page/local decision API.

The webview uses URL mode with
`/extensions/genereti-core/blocks-beats.html?embed=1`. The relative URL follows
the running Comfy host and port. The query selects a compact layout; the standalone
page keeps its original layout. The example saves a 700px webview surface through
the optional `generetiWebviewHeight` workflow property (ordinary webviews default
to 320px; supported property range 160–1600px).

Loading the graph starts neither inference nor sound. Choose d1 or the explicit
authored heuristic, then Start game. Start audio is a separate gesture. The
browser's Web Audio scheduler plays authored oscillator patterns; d1 selects
pattern labels. No audio files, camera, microphone or cloud calls are used.
Download d1 explicitly if missing. Comfy's Run delivers the URL as STRING; it
does not start the game and is not a stream of game telemetry.

Raw shows the URL; Rendered returns to the existing page if its source is
unchanged. Reload deliberately restarts it. Pause cancels pending decisions;
Stop audio is separate. Reset returns to seed 7. Closing/removing the iframe
releases its runtime. Output windows create separate page instances, not mirrors
of a running game, so avoid starting several during comparison.

## Local verification — October 9, 2026

Comfy Desktop localhost:8188, Codex in-app browser, macOS Apple silicon:
the saved workflow loaded with no missing nodes and an idle embedded page.
Actual d1 decisions returned normalized scores and advanced pieces; a warm
sample reported 23.2ms prediction / 24.2ms end-to-end while the canvas ran.
Start audio activated the scheduler and its 16-step bar clock; Stop audio
restored audio-off state. This verifies browser scheduling and controls, not
an acoustic recording or a statistical latency/quality benchmark.

The compact layout was checked in the real node. Raw editing the URL and
returning to Rendered loaded the requested page. 26 Python tests and existing
JavaScript client/layout checks passed. No errors were captured by the final
browser's error log; existing Comfy setting-deprecation warnings were present.
The compact embedded d1 run completed 20 placements with music choices staged
for upcoming bars. Raw/Rendered preserved the paused board. Reset returned zero
pieces; saving/reloading restored the URL and 700px surface with game/audio idle.
Comfy Run completed successfully and returned the relative URL in its UI payload.
Other browsers and older macOS versions remain untested.
