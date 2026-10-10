from concurrent.futures import TimeoutError
import base64
import io
import json
import time
from .contracts import Request, validate_decision
from .service import get_runtime
from .catalog import model_entry


def wait_for(job, runtime):
    try:
        while True:
            try:
                return job.future.result(timeout=0.1)
            except TimeoutError:
                import comfy.model_management
                comfy.model_management.throw_exception_if_processing_interrupted()
    except BaseException:
        runtime.cancel(job.request.request_id)
        raise


def execute(task, model, inputs, max_tokens=256, temperature=0.0):
    runtime = get_runtime()
    request = Request(task, model, inputs, {"max_tokens": max_tokens, "temperature": temperature})
    result = wait_for(runtime.submit(request), runtime)
    return result["content"], json.dumps({"request_id": request.request_id,
        "backend": model_entry(model)["backend"], "model": model, "timestamp": time.time(), **result.get("timings", {})})

class GeneretiCoreText:
    CATEGORY = "Genereti / Inference"
    FUNCTION = "generate"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "metrics")
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model": (["qwen3-0.6b"],),
            "prompt": ("STRING", {"multiline": True, "default": "Describe a playful generative art scene in one sentence. /no_think"}),
            "max_tokens": ("INT", {"default": 128, "min": 1, "max": 2048}),
            "temperature": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 2.0})}}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def generate(self, model, prompt, max_tokens=128, temperature=0.0):
        content, metrics = execute("text.generate", model, {"prompt": prompt}, max_tokens, temperature)
        return {"ui": {"text": [content["text"]]}, "result": (content["text"], metrics)}

class GeneretiCoreVision:
    CATEGORY = "Genereti / Inference"
    FUNCTION = "analyze"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "metrics")
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model": (["qwen3-vl-2b"],), "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True, "default": "Describe the image briefly."}),
            "max_tokens": ("INT", {"default": 128, "min": 1, "max": 2048})}}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def analyze(self, model, image, prompt, max_tokens=128):
        if image.shape[0] != 1:
            raise ValueError("Vision accepts one observation, not a batch")
        import numpy as np
        from PIL import Image
        picture = Image.fromarray((image[0].detach().cpu().numpy().clip(0, 1) * 255).astype(np.uint8))
        picture.thumbnail((1024, 1024))
        buffer = io.BytesIO()
        picture.save(buffer, format="PNG")
        content, metrics = execute("vision.analyze", model, {"prompt": prompt,
            "image_base64": base64.b64encode(buffer.getvalue()).decode()}, max_tokens)
        return {"ui": {"text": [content["text"]]}, "result": (content["text"], metrics)}

class GeneretiCoreDecision:
    DESCRIPTION = "A decision model reads a situation and ranks a fixed set of allowed answers. It returns the selected label, a JSON distribution, and local timing metrics. d1 runs one Core ML pass; Qwen uses answer-slot scores. Neither runs generated code."
    CATEGORY = "Genereti / Inference"
    FUNCTION = "evaluate"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("choice", "decision_json", "metrics")
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model": (["qwen3-0.6b", "d1-omni-600m"], {"tooltip": "Local decision backend. d1 is a text-only specialist; Qwen uses language-model answer slots."}),
            "prompt": ("STRING", {"multiline": True, "default": "A quiet moonlit lake with soft ripples.", "tooltip": "State: the situation the model should judge. Change this to compare decisions."}),
            "choices_json": ("STRING", {"default": '["blue", "orange"]', "multiline": True, "tooltip": "Allowed answer labels, authored by you. Keep these unchanged for the first comparison."}),
            "max_tokens": ("INT", {"default": 256, "min": 1, "max": 2048, "tooltip": "Qwen generation budget. Ignored by d1, which produces zero generated tokens."})},
            "optional": {"question": ("STRING", {"default": "Which option best fits the situation?", "multiline": True, "tooltip": "The question to answer about the state. Define what each option means if needed."})}}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def evaluate(self, model, prompt, choices_json, max_tokens=256, question="Which option best fits the situation?"):
        content, metrics = execute("decision.evaluate", model,
            {"prompt": (prompt if model == "d1-omni-600m" else prompt + "\n" + question), "question": question, "choices": json.loads(choices_json)}, max_tokens)
        serialized = json.dumps(content)
        return {"ui": {"text": [serialized]}, "result": (content["choice"], serialized, metrics)}

class GeneretiCoreValidateDecision:
    DESCRIPTION = "Validates supplied example scores; this node does not run AI. Checks allowed labels, finite scores and that the selected label has the largest score, then normalizes the distribution. Invalid input shows an inline explanation and skips connected outputs; edit and Run again."
    """Accept scores from specialist/portable providers through the same validated contract."""
    CATEGORY = "Genereti / Inference"
    FUNCTION = "validate"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("choice", "decision_json")
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"choices_json": ("STRING", {"default": '["blue", "orange"]', "tooltip": "Allowed labels. These are answer names, not scores."}),
            "decision_json": ("STRING", {"multiline": True, "default": '{"choice":"blue","scores":{"blue":0.8,"orange":0.2}}', "tooltip": 'The choice must name a highest-scoring label. If blue becomes 0.1 and orange stays 0.2, set choice to orange too. Scores need not sum to 1; the viewer shows normalized probabilities.'})}}
    def validate(self, choices_json, decision_json):
        try:
            result = validate_decision(decision_json, json.loads(choices_json))
        except (ValueError, TypeError) as error:
            from comfy_execution.graph_utils import ExecutionBlocker
            message = "Needs correction: " + str(error)
            return {"ui": {"text": [message + "\n\nConnected outputs were not updated. Edit the JSON and Run again."],
                           "validation": [{"valid": False, "message": message}]},
                    "result": (ExecutionBlocker(None), ExecutionBlocker(None))}
        return {"ui": {"text": [json.dumps(result)], "validation": [{"valid": True}]},
                "result": (result["choice"], json.dumps(result))}

class GeneretiCoreResult:
    DESCRIPTION = "Displays connected text or JSON after workflow Run. Choose Tree, Pretty or Minified in the viewer toolbar. It does not run a model."
    """A dependency-free text/JSON sink for queued workflow outputs."""
    CATEGORY = "Genereti / Inference"
    FUNCTION = "show"
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"text": ("STRING", {"forceInput": True})}}
    def show(self, text):
        return {"ui": {"text": [str(text)]}, "result": ()}

class GeneretiCoreChoiceValue:
    DESCRIPTION = "Maps a selected label to a number using values_json. This authored rule translates a decision into a creative control; it does not run AI."
    CATEGORY = "Genereti / Inference"
    FUNCTION = "map_choice"
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"choice": ("STRING", {"forceInput": True}),
            "values_json": ("STRING", {"default": '{"blue":210,"orange":30}', "multiline": True})}}
    def map_choice(self, choice, values_json):
        import math
        values = json.loads(values_json)
        if not isinstance(values, dict) or choice not in values:
            raise ValueError("Add the selected choice to values_json")
        value = values[choice]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("Choice values must be finite numbers")
        return (float(value),)

class GeneretiCoreTutorial:
    DESCRIPTION = "Tutorial 0 introduces states, questions, allowed options, distributions and creative controls. Open the local reading page from this node; no model or inference is needed."
    CATEGORY = "Genereti / Inference"
    FUNCTION = "read"
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    @classmethod
    def INPUT_TYPES(cls): return {"required": {}}
    def read(self): return {"ui": {"text": ["Open Tutorial 0 from the book button on this node."]}, "result": ()}

class GeneretiCoreDecisionArcade:
    DESCRIPTION = "Opens Blocks & Beats: a local decision-driven Tetris simulation and authored music sequencer. Start game explicitly in the demo page; audio has a separate Start audio control. Comfy Run does not start either."
    CATEGORY = "Genereti / Inference"
    FUNCTION = "open_demo"
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    @classmethod
    def INPUT_TYPES(cls): return {"required": {}}
    def open_demo(self): return {"ui": {"text": ["Open Blocks & Beats with the arcade button. Start game and audio separately."]}, "result": ()}

NODE_CLASS_MAPPINGS = {c.__name__: c for c in (GeneretiCoreText, GeneretiCoreVision, GeneretiCoreDecision, GeneretiCoreValidateDecision, GeneretiCoreResult, GeneretiCoreChoiceValue, GeneretiCoreTutorial, GeneretiCoreDecisionArcade)}
NODE_DISPLAY_NAME_MAPPINGS = {"GeneretiCoreDecisionArcade": "ꘅ Decision Arcade", "GeneretiCoreTutorial": "ꘅ Tutorial", "GeneretiCoreText": "ꘅ Local Text", "GeneretiCoreVision": "ꘅ Local Vision",
    "GeneretiCoreDecision": "ꘅ Local Decision", "GeneretiCoreValidateDecision": "ꘅ Decision Scores Validator", "GeneretiCoreResult": "ꘅ Text / JSON Viewer", "GeneretiCoreChoiceValue": "ꘅ Choice to Value"}

# Comfy uses DESCRIPTION for the native title-dot hover and Info panel.
for node_name, node_class in NODE_CLASS_MAPPINGS.items():
    description = getattr(node_class, "DESCRIPTION", "Local inference node.")
    node_class.DESCRIPTION = node_name + "\n\n" + description
