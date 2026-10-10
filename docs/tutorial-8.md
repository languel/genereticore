# Tutorial 8 · ꘅ Blocks & Beats

This demo is a simplified self-playing Tetris simulation whose board state also conducts music. Open **08 - Blocks and Beats - decision arcade** in Comfy. The **ꘅ Decision Arcade · open Blocks & Beats** node opens the local demo with its ▦ button. **ꘇ lesson · walkthrough · press its Run** narrates the exercise. In the demo page, **ꘅ Local Decision · choose a legal placement** and **ꘅ Local Decision · choose the next music pattern** expose the two decision loops. These panel labels describe tasks; they are not additional registered Comfy classes.

Nothing starts merely by opening the workflow or page. Click **Start game** to start simulation/inference. **Start audio** is separate. Comfy's top Run does not start the game or sound.

## What does a decision model do here?

The authored game rules enumerate legal hard drops for the current piece. They measure the board after each drop: rows cleared, holes under occupied cells, total column height and unevenness. A fixed heuristic shortlists four good placements. d1 receives that compact situation, a question about the best drop, and labels A–D. It selects a label; the game looks up the already-validated placement. It never executes model-written game code.

This is already a helpful limitation: d1 cannot choose an illegal move. It can still choose a strategically poor move. The shortlist itself contains human assumptions. Ask whether minimizing holes and height is enough to play well, and whether the numeric summary loses useful spatial information. The demo does not use vision; only text features reach the current Core ML model.

Follow **ꘅ Local Decision · choose a legal placement**. The highlighted candidate is the selected answer. The JSON viewer contains scores and timings; Tree, Pretty and Minified change presentation, not data. Scores describe model preferences, not the objective value of a move.

## Three clocks

Rendering runs on the browser animation clock. One asynchronous move decision finishes before the next piece is committed; only one request is outstanding. A legal ghost drop animates while the native helper remains separate from the renderer.

Audio uses its own Web Audio scheduling clock. Every four pieces, and after a cleared row, the music decision reads stack height, holes and recently cleared rows. It chooses one of four authored patterns: calm, drive, tense or celebrate. The first piece also requests a music decision.

Follow **ꘅ Local Decision · choose the next music pattern**. While audio plays, a completed choice is staged as next. It becomes current at the next bar boundary. The previous pattern continues during inference. The ResultPair helper also rejects older revisions. With audio off there is no sounding bar, so the visual pattern preview can update immediately. These patterns are local synthesized notes and percussion; no Strudel source, samples or hosted music model are required.

Pause stops the game and invalidates pending inference, but audio continues until **Stop audio**. Reset cancels outstanding decisions and restores the same seed; it does not secretly switch the player. Errors pause with an inline status and no automatic cloud or heuristic fallback.

## Compare an authored player with d1

Choose **Authored heuristic · no AI**, then Start game. This chooses the highest heuristic utility directly, without model download or inference. Reset to seed 7, choose d1 and repeat. Use the same pace and number of committed pieces. Compare rows cleared, stack height and holes rather than just asking which animation looks smarter. Pausing retains the uncommitted piece.

The game uses all seven tetrominoes in a seeded seven-bag sequence. This teaching simulation omits manual controls, hold, wall kicks and competitive scoring. It is a demonstration of decision-to-control architecture, not a competitive Tetris agent.

## Model setup and boundaries

The d1 mode uses the existing locally tested Core ML backend on Apple silicon. Download the pinned model explicitly if missing; first compilation/loading can take much longer than a warm decision. The no-model player runs without a native helper. The browser calls the same loopback-only, same-origin API as other ꘅ nodes. Stop/Reset rejects late results, including those already submitted when the board changes. No camera, microphone or screen capture is involved.

The current catalog does not load ONNX models. The ONNX community d1 export is a promising separate backend, with custom token/marker handling and text, image and audio graphs. Supporting it requires pinned assets/runtime, license provenance, cancellation and parity checks against the existing decision contract. Published ONNX timings are not local measurements. See the [ONNX model card](https://huggingface.co/onnx-community/d1-omni-600M-ONNX).

## Experiments

- Watch the candidate features before revealing the model's answer. Which drop would you choose, and why?
- Compare a calm low stack with a high stack: does the music choice reflect the stated mapping?
- Start audio, then watch next wait until a bar. Pause the game and notice that music has a separate clock.
- Reset and compare d1 against the authored heuristic. A fast local model is not automatically a strong game player.
