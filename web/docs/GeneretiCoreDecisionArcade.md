# ꘅ Decision Arcade

Opens Blocks & Beats, a local decision-driven Tetris simulation with an authored soundtrack.

## Inputs, outputs and controls

The ▦ button opens the demo page. Start game and Start audio are separate explicit actions. Comfy Run only returns an opening reminder; there are no inputs or outputs.

## Small example

Open **08 - Blocks and Beats - decision arcade**, read Tutorial 8, and choose the no-AI heuristic player for a model-free baseline. Reset to seed 7 to compare with the local d1 player.

## Requirements and limits

The d1 player requires installed d1 artifacts and its native helper. Errors pause play; there is no automatic fallback. Pause cancels pending decisions and rejects stale results; Reset restores the seeded board. Audio changes at bar boundaries. Opening the page starts no inference, capture or audio.
