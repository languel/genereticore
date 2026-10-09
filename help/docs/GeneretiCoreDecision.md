# ꘅ Local Decision

Ranks your fixed set of allowed labels for a situation and question. It returns controls, not executable code.

## Inputs, outputs and controls

Inputs: model, prompt (state), choices_json (allowed labels), max_tokens and optional question. Outputs: choice, decision_json (scores/probabilities) and metrics. ↓ downloads; ▷ runs the graph; ϟ previews locally; □ cancels a local preview request.

## Small example

State: “A quiet moonlit lake with soft ripples.” Question: “Which palette fits?” Choices: `["blue", "orange"]`. Wire choice to ꘅ Choice to Value.

## Requirements and limits

d1 is text-only, requires macOS 15+ and the d1 helper, accepts 2–8 labels and at most 256 combined input tokens, and ignores max_tokens. Qwen requires macOS 27+ and uses answer-slot scores. Scores are uncalibrated; artistic judgment is not guaranteed.
