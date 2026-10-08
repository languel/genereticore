import json
from pathlib import Path

CATALOG = json.loads(Path(__file__).with_name("catalog.json").read_text())
MODELS = {m["id"]: m for m in CATALOG["models"]}

def model_entry(model, task=None):
    if model not in MODELS:
        raise ValueError(f"Unknown model: {model}")
    entry = MODELS[model]
    if task and task != "model.download" and task not in entry["tasks"]:
        raise ValueError(f"{model} does not support {task}")
    return entry
