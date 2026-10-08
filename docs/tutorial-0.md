# Tutorial 0 · From a situation to a creative decision

You do not need to know machine learning or JSON to start. This tutorial introduces the idea behind our workflows, explains the nodes you will meet, and gives each experiment a purpose. Read it before opening the practical examples. The first exercise does not run a model.

## What are we making?

We are making a small artwork whose color can respond to a description of a scene. Imagine two descriptions: “a quiet moonlit lake” and “a lively sunrise festival.” Our artwork has two authored palettes: blue and orange. We ask a local model which palette fits the description, then turn that answer into the hue of a moving circle.

The model does not draw the circle, write the sketch, or invent new controls. You authored the artwork and the possible palettes. The model makes one bounded choice inside that design. This is a useful pattern for interactive art: a changing situation becomes a small, inspectable control.

## What is a decision model?

A decision model reads a **state** (a description of the current situation), a **question**, and a set of **allowed options**. It returns a distribution over those options and a selected answer.

For our palette demo:

- State: “A quiet moonlit lake with soft ripples.”
- Question: “Which palette best fits this scene?”
- Allowed options: `blue`, `orange`.
- Possible result: blue has a larger score than orange, so blue is selected.

The words blue and orange are labels you define. They are not automatically colors in Comfy. A later mapping node assigns each label a number that the artwork understands.

A chat model generates a sequence of words. A specialist decision model such as d1 instead evaluates the allowed answers in a single forward pass, without generating a written reply. Our Qwen example uses a different method: it scores answer slots with a small language model. Both can feed the same creative graph, but their scores have different meanings and their quality must be evaluated separately.

## Why choose the options ourselves?

Allowed options define the boundaries of your artwork. If you offer only blue and orange, the decision cannot introduce a third palette or execute a command. You might instead offer `slow` and `fast`, `sparse` and `dense`, or three named scenes. Choose options that correspond to controls you actually designed.

Changing an option changes the question the model is answering. It is not a way to train the model. For your first experiment, keep the two palette labels unchanged and edit only the scene description. This lets you compare answers while the artwork's meaning stays stable.

Later, adding a label such as violet also requires adding a numeric mapping. A label alone does not tell p5 what to render. The label, the mapping, and the creative control form a contract between your graph's parts.

## Scores, probabilities, and uncertainty

A score indicates how much the model favors an option for this particular input. A distribution assigns a value to each allowed option. In a normalized distribution, the values add up to one. For example, blue 0.8 and orange 0.2 selects blue.

This does **not** mean that 80 percent of people would prefer blue, or that blue is objectively correct. Creative choices are contextual and subjective. A model can be confidently unhelpful. Two almost equal scores tell you the decision is close; you may decide to keep the previous palette instead of switching on every small change.

Our d1 adapter applies the upstream model's published calibration temperatures before converting logits to probabilities. The result labels its method `d1_temperature_scaled`. Calibration from the model's training/evaluation setting does not certify reliability for your creative task. Qwen's result is labeled `answer_slot_softmax_uncalibrated`; the supplied-score exercise is `normalized_uncalibrated_scores`. Read the method alongside the numbers rather than treating all distributions as equally reliable.

## What is JSON?

JSON is a plain-text format for named data. Curly braces group an object, a name followed by a colon introduces a field, and square brackets hold a list. Quotation marks identify text. You will see a result shaped like this:

```json
{"choice":"blue","scores":{"blue":0.8,"orange":0.2}}
```

`choice` is the selected label. `scores` contains a value for every allowed label. Our validator adds a normalized `probabilities` object and a `probability_kind` field explaining the method.

The Text / JSON Viewer offers **Tree**, **Pretty**, and **Minified**. Tree lets you expand or collapse an object such as scores. Pretty shows indented text. Minified shows compact JSON for copying. These are three views of the same data; switching views never changes the decision. Plain text is displayed as plain text. The viewer does not run AI.

## Exercise 1 · Read a decision, without AI

Open **01 - Read a decision - no model**. This is a demonstration of the result contract, not a decision-model inference demo. The **ꘅ Decision Scores Validator** receives a small, already-written result and checks it. The connected **Text / JSON Viewers** display the selected label and distribution.

Press top Run, then expand scores in the tree. The numbers are supplied by us; nothing was inferred. We use this exercise so you can learn what an answer looks like before waiting for downloads or interpreting a model.

An optional second experiment changes the supplied scores. Change blue from `0.8` to `0.1`, leave orange at `0.2`, and also change `choice` from `blue` to `orange`:

```json
{"choice":"orange","scores":{"blue":0.1,"orange":0.2}}
```

Press Run. Orange now has the larger score, so the selected label is orange. The normalized probabilities are about `0.333` for blue and `0.667` for orange. The supplied scores do not need to sum to one.

If you change only blue's score, the JSON still says `"choice":"blue"`. Editing a number does not update another JSON field automatically. With blue at `0.1` and orange at `0.2`, that answer contradicts itself. The validator shows “Needs correction” inside the node when the selected choice contradicts the scores. Connected outputs are skipped and our JSON viewers are marked “Not updated”; no Comfy execution error dialog is needed. Correct the JSON and press Run again. This shows the safety contract: downstream controls should receive a complete, consistent answer. Editing these example scores does not teach or fine-tune a model. In the real demos, the model supplies the scores for you.

## Meet the nodes

`ꘅ` substitutes for GeneretiCore in visible node labels; `ꘇ` substitutes for Genereti. Class names, workflow node types and model catalog identifiers retain their Latinized names.

The node title contains its actual display type followed by its job in this graph. Hover the main node dot to see its saved Comfy class and description. Select a node and open Node Info for its description. Custom titles are descriptions; they do not change the underlying class.

- **ꘅ Tutorial** (`GeneretiCoreTutorial`): opens this lesson. No inference.
- **ꘅ Decision Scores Validator** (`GeneretiCoreValidateDecision`): validates supplied decisions. No inference.
- **ꘅ Local Decision** (`GeneretiCoreDecision`): sends a state, question and allowed options to the selected local model.
- **ꘅ Choice to Value** (`GeneretiCoreChoiceValue`): looks up a selected label in an authored dictionary and outputs a number. No inference.
- **ꘅ Text / JSON Viewer** (`GeneretiCoreResult`): displays connected results. No inference.
- **ꘅ Local Text** (`GeneretiCoreText`): generates words with Qwen; it is not the same task as selecting a fixed option.
- **ꘅ Local Vision** (`GeneretiCoreVision`): describes one connected image with Qwen3-VL. The current d1 Core ML conversion does not accept images or audio.
- **ꘇ livecode**: runs your p5 artwork in the browser. It renders independently of model inference.

## Exercise 2 · A real local d1 decision

Open **07 - d1 - scene to artwork palette**. This demo connects a real decision model to a moving artwork. It requires Genereti public as well as GeneretiCore.

Read the state, question and allowed labels on Local Decision. If d1 is missing, use its download arrow. Downloads are explicit and cached locally. The contributor build requires the d1 helper; model assets and compiled caches are kept outside the source repository.

Press the top Comfy Run. Follow the graph: Local Decision selects a label; Choice to Value maps blue to 210 or orange to 30; the numeric wire sets p5's `paletteHue` control. The viewer displays the distribution, and the timing viewer reports loading and prediction time. No model-written code is evaluated.

Try the quiet moonlit lake, then change only the state to “The scene is entirely orange: orange lights, orange walls and an orange sunset.” Run again and compare the selected palette and distribution. These clear fixtures exercise the complete wiring. Then try an energetic sunrise festival: in one local test the model still chose blue for that warm scene. This is a useful disagreement to inspect, not something the demo should hide. Ask whether each choice serves your artwork. Record disagreements rather than assuming the model must be right. You may change the mapping values to explore different colors while keeping the same decision labels.

## Which Run does what?

Top Run, or the inference node's triangle, queues the connected graph and updates downstream results. The lightning glyph submits a local preview inside the inference node only. Use top Run for these exercises.

The p5 editor's Run applies your creative code. Its saved artwork starts rendering when you open the workflow. The walkthrough node's Run opens narrated steps and node highlights. Neither of these buttons queues model inference.

The download arrow prepares the selected model; it does not run inference. Opening a workflow never starts inference, camera, microphone, or audio. Our models run locally, with no automatic hosted fallback.

## Timing and two clocks

The artwork keeps animating while a model works. Browser rendering and native model inference have separate clocks. Inference runs in an isolated native helper through a bounded queue, away from rendering and audio threads.

The first run can compile and load the model and is much slower than a warm prediction. `prediction_ms` measures the model call; `end_to_end_ms` also includes the surrounding request work. `generated_tokens: 0` is expected for d1. It is choosing an answer, not writing a sentence. Compare cold and warm results instead of promising live responsiveness from a single model-card number.

The image walkthrough takes one queued frame from the moving sketch. It does not analyze every animation frame. For future continuously changing inputs, stale results must be handled explicitly: the latest-state policy suppresses obsolete answers, and a previous visual result can remain displayed while the next request works.

## A useful next experiment

Design one control with a small set of meaningful states. Write the state and question plainly. Define the options, map each option to a control, and inspect both the answer and its distribution. Change one part at a time. Keep a manual override and a visible result so that the artist can understand what the system did.

These examples demonstrate wiring, local inference and creative control—not a benchmark or a guarantee of good judgment. Your evaluation is part of the artwork's design.
