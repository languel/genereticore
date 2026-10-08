# Start here

Read [Tutorial 0: decision models and creative controls](tutorial-0.md) first, or open **00 - Tutorial 0 - decision models** and click its book button. It defines the demos and explains every node type. The model-free example reads a supplied result; it does not ask you to train a model by editing scores.

Open **Workflows → GeneretiCore → 01 - Read a decision - no model**. Press the blue **Run** button at the top of Comfy. The result nodes on the right show a choice and its scores. Nothing downloads and no AI runs in this first sample.

These examples are installed into your Comfy profile on startup. Refresh the Workflows panel if it was already open. Edited copies are preserved when samples update. Replaced or retired unchanged samples are backed up in the profile’s `.genereticore-workflow-backups` folder. You can also drag any JSON from `example_workflows/` onto Comfy, or use Comfy's Open command.

## Which Run button?

| Action | What happens |
| --- | --- |
| Top **Run**, or inference node **▷** | Runs the workflow; connected result/image nodes update. Use this for the examples. |
| Inference node **ϟ** | A quick local preview appears inside that node. Connected nodes do not update. |
| Inference node **↓** | Downloads the selected pinned model if missing; wait for `installed`. It does not run the workflow. |
| Inference node **□** | Cancels its local preview/download. Use Comfy's top cancel button for workflow execution. |
| Inference node **?** | Opens this getting-started guide. |
| Genereti editor **Run** | Applies creative code edits; the saved sketch starts on open. It does not queue AI. |
| Genereti walkthrough **Run** | Starts the step-by-step guide. It does not queue AI. |

Your earlier screenshot showed `ready` after an independent async submission, while the connected Preview as Text stayed empty. That action did not run the connected graph. The controls now distinguish **workflow complete** from **preview**, and show the actual answer inside the inference node. Use top Run for connected outputs.

## Eight sample workflows

| Open this workflow | What to do | What you should see |
| --- | --- | --- |
| **00 - Tutorial 0 - decision models** | Open the book button. | The theory-first lesson; no model needed. |
| **01 - Read a decision - no model** | Press Run. Edit the example scores, set choice to the largest score, Run again. | Selected label and normalized score JSON. No model required. |
| **02 - Local text** | Download Qwen 0.6B with ↓ if missing. Run. Change the artwork-title prompt and Run again. | Generated title plus model/timing details. |
| **03 - Local decisions** | Use the same downloaded model. Run, then change the scene prompt. | One listed palette label and finite scores for both choices. |
| **04 - Local vision** | Download Qwen3-VL 2B with ↓ if missing (about 3.3 GB). Run. | A description of the solid blue fixture and an image preview. |
| **05 - Genereti - sketch to vision walkthrough** | Requires Genereti public. Observe the moving sketch, download vision if needed, then top Run. | An orange circle keeps moving while a sampled frame is analyzed locally. |
| **06 - Genereti - AI palette walkthrough** | Requires Genereti public. Observe the sketch, download Qwen if needed, then top Run. | Choice → numeric hue → moving artwork; scores remain visible. |

| **07 - d1 - scene to artwork palette** | Download d1 if missing, top Run, then change only the state. | A specialist decision distribution drives the authored circle through a hue map. |

Workflows 05, 06 and 07 include a **walkthrough** node below the graph. Press **Run on that lesson node** for narration and node highlights. Previous/Next advances the guide; you perform model download and top Run yourself. Opening the workflow or guide does not start inference, camera, microphone or audio.

## The d1 artwork demo

Open **07 - d1 - scene to artwork palette**. Local Decision reads a text situation and question, ranks the allowed blue/orange labels, and supplies a distribution. Choice to Value maps the selected label to a numeric hue for the authored p5 circle. Keep the options unchanged initially; change only the situation and compare answers. The same viewer offers Tree, Pretty and Minified without changing data. d1 requires macOS 15+ Apple silicon and `python3 scripts/build_d1_helper.py` for this contributor build. Its conversion is text-only, limited to eight options and a 256-token combined prompt. Too-long inputs fail explicitly. `max_tokens` belongs to Qwen generation; d1 ignores it and generates zero tokens.

## Use your own image

In workflow 04, add Comfy's **Load Image** node and choose a local picture. Connect its **IMAGE** output to **local vision → image**, replacing the Empty Image wire. Press top Run. The image is analyzed locally; this pack does not upload it to hosted inference. One image is analyzed per run; batches are rejected.

In workflow 05, change the p5 circle's color or motion, apply the editor, then top Run to inspect another frame. Animation continues independently; repeated top Runs are explicit observations, not automatic analysis of every video frame.

## Change the palette mapping

In workflow 06, the model chooses `blue` or `orange`. **choice to value** maps those labels to hues 210 and 30. The numeric connection drives the p5 `paletteHue` parameter. Edit `values_json` to change those hues. If you add a choice, add its numeric mapping too. Only listed choices and finite numbers pass through this graph; generated code is never executed.

## If something is missing

- **No workflows:** restart Comfy to install them, then refresh Workflows. Or drag a sample JSON onto Comfy. To install into another writable profile, run `python3 scripts/install_examples.py /path/to/Comfy/user/default/workflows` from this checkout.
- **Red/missing Genereti nodes in 05/06/07:** install the separate public Genereti pack in the same Comfy instance, then restart and refresh. Samples 00–04 only need GeneretiCore and standard Comfy nodes. In the local port-8003 test, Genereti public is already linked.
- **Model missing:** click ↓ on the corresponding inference node. Text/decision share Qwen 0.6B; vision requires the separate Qwen3-VL download. Nothing silently downloads on Run.
- **Native helper missing:** this contributor build requires macOS 27+ Apple silicon, Xcode 27, and `python3 scripts/build_helper.py`. A student-ready prebuilt release is not available yet.
- **Blank connected result:** use top Run or node ▷. ϟ only updates the local preview. Also check Comfy's execution error and the model's installed status.
- **Wrong model answer:** the small Qwen starter gave incorrect answers and poor choices in tests. These examples teach wiring and delivery; they do not certify reasoning quality. Scores are uncalibrated.

See [API examples](api.md) for explicit live clients, and [validation](validation.md) for measured platform and performance limits.
