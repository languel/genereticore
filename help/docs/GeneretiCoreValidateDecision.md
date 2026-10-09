# ꘅ Decision Scores Validator

Checks supplied scores and selected choice. This node does not run AI.

## Inputs, outputs and controls

Inputs: choices_json and decision_json strings. Outputs: choice and normalized decision_json. Labels must match, scores must be finite and nonnegative, and choice must have a highest score. Invalid input explains the issue and blocks downstream outputs.

## Small example

Allowed labels `["blue","orange"]`; decision `{"choice":"blue","scores":{"blue":0.8,"orange":0.2}}`. Run, then change both scores and choice to compare outcomes.

## Requirements and limits

No model or Apple runtime needed. Scores need not sum to one; all-zero distributions are rejected. A previous downstream result is marked not updated when validation fails.
