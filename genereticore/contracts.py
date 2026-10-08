from __future__ import annotations
from dataclasses import dataclass, field
import json
import math
from typing import Any
from uuid import uuid4

TASKS = {"text.generate", "vision.analyze", "decision.evaluate", "model.download"}

@dataclass(frozen=True)
class Capability:
    backend: str
    tasks: tuple[str, ...]
    streaming: bool
    cancellation: str
    structured_output: bool
    available: bool
    reason: str = ""

@dataclass(frozen=True)
class Request:
    task: str
    model: str = "qwen3-0.6b"
    inputs: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
    input_revision: int = 0
    stream_id: str = "queue"
    request_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self):
        if not isinstance(self.inputs, dict) or not isinstance(self.options, dict):
            raise ValueError("inputs and options must be objects")
        if not isinstance(self.stream_id, str) or not isinstance(self.request_id, str):
            raise ValueError("Request and stream IDs must be strings")
        if self.task not in TASKS:
            raise ValueError(f"Unsupported task: {self.task}")
        if not isinstance(self.input_revision, int) or self.input_revision < 0:
            raise ValueError("input_revision must be a nonnegative integer")
        if not self.stream_id or len(self.stream_id) > 128:
            raise ValueError("stream_id must be 1–128 characters")
        if not self.request_id or len(self.request_id) > 128:
            raise ValueError("request_id must be 1–128 characters")
        if len(json.dumps(self.inputs)) > 8_000_000:
            raise ValueError("Input exceeds 8 MB")
        tokens = self.options.get("max_tokens", 256)
        if not isinstance(tokens, int) or not 1 <= tokens <= 2048:
            raise ValueError("max_tokens must be 1–2048")
        temperature = self.options.get("temperature", 0.0)
        if not isinstance(temperature, (int, float)) or not math.isfinite(temperature) or not 0 <= temperature <= 2:
            raise ValueError("temperature must be finite and between 0 and 2")
        if self.task != "model.download":
            if not isinstance(self.inputs.get("prompt"), str) or not 1 <= len(self.inputs["prompt"]) <= 32768:
                raise ValueError("prompt must be 1–32768 characters")
        if self.task == "decision.evaluate":
            validate_choices(self.inputs.get("choices"))
            if self.model == "d1-omni-600m" and len(self.inputs["choices"]) > 8:
                raise ValueError("d1 Core ML supports at most 8 choices")
            if "question" in self.inputs and (not isinstance(self.inputs["question"], str) or not 1 <= len(self.inputs["question"]) <= 2048):
                raise ValueError("question must be 1–2048 characters")
            if self.model == "qwen3-0.6b" and len(self.inputs["choices"]) > 26:
                raise ValueError("Qwen supports at most 26 choices")

    def wire(self):
        return {"id": self.request_id, "task": self.task, "model": self.model,
                "inputs": self.inputs, "options": self.options}


def validate_choices(choices):
    if not isinstance(choices, list) or not 2 <= len(choices) <= 32:
        raise ValueError("Provide 2–32 choices")
    if any(not isinstance(c, str) or not c.strip() or len(c) > 128 for c in choices):
        raise ValueError("Choices must be nonempty strings of at most 128 characters")
    if len(set(choices)) != len(choices):
        raise ValueError("Choices must be unique")
    return choices


def decision_schema(choices):
    validate_choices(choices)
    return json.dumps({"type": "object", "properties": {
        "choice": {"type": "string", "enum": choices},
        "scores": {"type": "object", "properties": {c: {"type": "number", "minimum": 0, "maximum": 1} for c in choices},
                   "required": choices, "additionalProperties": False}},
        "required": ["choice", "scores"], "additionalProperties": False})


def validate_decision(value, choices):
    """Validate model/specialist scores; never execute model output as code."""
    validate_choices(choices)
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict) or set(value) != {"choice", "scores"}:
        raise ValueError("Decision must contain only choice and scores")
    if value["choice"] not in choices or not isinstance(value["scores"], dict) or set(value["scores"]) != set(choices):
        raise ValueError("Decision contains missing or unknown choices")
    scores = value["scores"]
    if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) or not 0 <= v <= 1 for v in scores.values()):
        raise ValueError("Scores must be finite numbers between 0 and 1")
    total = sum(scores.values())
    if total <= 0:
        raise ValueError("Decision scores have zero mass")
    if scores[value["choice"]] != max(scores.values()):
        winner = max(choices, key=scores.get)
        selected = value["choice"]
        raise ValueError(
            f"Decision mismatch: choice is {json.dumps(selected)} (score {scores[selected]:g}), "
            f"but {json.dumps(winner)} has the highest score ({scores[winner]:g}). "
            f"Set choice to {json.dumps(winner)}, or change the scores so {json.dumps(selected)} "
            "has the highest score. Editing scores does not automatically change choice."
        )
    # These are normalized model-reported scores, NOT calibrated probabilities.
    return {"choice": value["choice"], "scores": scores,
            "probabilities": {c: scores[c] / total for c in choices},
            "probability_kind": "normalized_uncalibrated_scores"}
