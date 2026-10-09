# ꘅ Text / JSON Viewer

Displays connected text or JSON after Run.

## Inputs, outputs and controls

Input: text (STRING). No outputs. Tree expands nested JSON; Pretty uses indentation; Minified removes whitespace. The selected view is saved with the workflow. Preview minimize and freeze affect local display only; downstream work continues.

## Small example

Wire decision_json from ꘅ Local Decision into text, press Run, and expand probabilities in Tree.

## Requirements and limits

Read-only: it neither infers nor edits data. Tree limits rendering to 5000 entries; Pretty or Minified exposes full text. A blank viewer needs a connected upstream Run. Alt-O uses the shared visual view when Genereti is installed.
