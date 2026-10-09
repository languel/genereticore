# ꘅ Choice to Value

Maps a selected label to an authored finite number for a creative control.

## Inputs, outputs and controls

Inputs: choice (STRING socket) and values_json. Output: value (FLOAT). Every selected label needs an entry; booleans and nonfinite numbers are rejected.

## Small example

Use `{"blue":210,"orange":30}`. Connect value to a livecode paletteHue socket using HSB degrees (0–360).

## Requirements and limits

No model runs here. Units come from the destination control. A model decision updates this mapping only after connected workflow Run.
