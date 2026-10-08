from __future__ import annotations
from dataclasses import asdict
import json
import os
from pathlib import Path
import platform
import subprocess
import threading
import time
from typing import Callable, Protocol

from .artifacts import ArtifactVerifier
from .catalog import MODELS, model_entry
from .contracts import Capability, Request, validate_decision

class Backend(Protocol):
    def capability(self) -> Capability: ...
    def execute(self, request: Request, emit: Callable, canceled: Callable) -> dict: ...
    def cancel(self) -> bool: ...
    def close(self) -> None: ...

class CoreAIBackend:
    """One warm, isolated helper. Cancellation terminates it and releases its models."""
    def __init__(self, model_dir=None, helper=None):
        self.model_dir = Path(model_dir or os.environ.get("GENERETICORE_MODEL_DIR", Path.home() / "Library/Application Support/GeneretiCore/models"))
        self.helper = Path(helper or os.environ.get("GENERETICORE_HELPER", Path(__file__).resolve().parents[1] / "native/bin/genereticore-helper"))
        self._process = None
        self._verifier = ArtifactVerifier()
        self._process_lock = threading.Lock()

    def capability(self):
        reason = ""
        if platform.system() != "Darwin" or platform.machine() != "arm64":
            reason = "Core AI requires macOS 27+ on Apple silicon"
        elif int(platform.mac_ver()[0].split(".")[0] or 0) < 27:
            reason = "Core AI requires macOS 27+"
        elif not self.helper.is_file() or not os.access(self.helper, os.X_OK):
            reason = "Native helper missing. Contributor setup: python scripts/build_helper.py"
        return Capability("coreai", ("text.generate", "vision.analyze", "decision.evaluate", "model.download"),
                          True, "terminate_helper", True, not reason, reason)

    def installed(self, entry):
        root = self.model_dir / entry["repo"] / entry["revision"]
        return bool(entry.get("files")) and all((root / f["path"]).is_file() and (root / f["path"]).stat().st_size == f["bytes"] for f in entry["files"])

    def catalog(self):
        return [{**m, "installed": self.installed(m)} for m in MODELS.values()]

    def _start(self, canceled):
        with self._process_lock:
            if canceled():
                raise RuntimeError("Request canceled before helper start")
            if self._process is None or self._process.poll() is not None:
                if self._process is not None:
                    self._process.wait(timeout=10)
                    self._process.stdin.close()
                    self._process.stdout.close()
                # Upstream diagnostics can contain prompts. Discard stderr; structured errors use stdout.
                self._process = subprocess.Popen([str(self.helper), str(self.model_dir)],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                    text=True, encoding="utf-8", bufsize=1)
            return self._process

    def execute(self, request, emit, canceled=lambda: False):
        start = time.perf_counter()
        entry = model_entry(request.model, request.task)
        cap = self.capability()
        if not cap.available:
            raise RuntimeError(cap.reason)
        if request.task != "model.download" and not self.installed(entry):
            raise RuntimeError("Model missing. Download it explicitly from the node toolbar first.")
        if request.task != "model.download":
            self._verifier.verify(self.model_dir, entry, emit, canceled)
        wire = request.wire()
        process = self._start(canceled)
        process.stdin.write(json.dumps(wire, allow_nan=False) + "\n")
        process.stdin.flush()
        for line in process.stdout:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue  # Ignore non-protocol runtime diagnostics.
            if not isinstance(event, dict) or event.get("id") != request.request_id:
                continue
            kind, payload = event.get("type"), event.get("payload", {})
            if kind == "failed":
                raise RuntimeError(payload.get("message", "Native helper failed"))
            if kind == "completed":
                if request.task == "model.download":
                    self._verifier.verify(self.model_dir, entry, emit, canceled)
                if request.task == "decision.evaluate":
                    payload["content"] = validate_decision(payload["content"], request.inputs["choices"])
                    payload["content"]["probability_kind"] = payload.get("probability_kind", "answer_slot_softmax_uncalibrated")
                payload.setdefault("timings", {})["end_to_end_ms"] = (time.perf_counter() - start) * 1000
                return payload
            emit(kind, payload)
        raise RuntimeError(f"Native helper stopped before completing the request (exit {process.poll()}); run the contributor build again if macOS rejected an updated helper")

    def cancel(self):
        with self._process_lock:
            if self._process and self._process.poll() is None:
                self._process.kill()
                self._process.wait(timeout=10)
                return True
        return False

    def close(self):
        self.cancel()
        with self._process_lock:
            if self._process:
                self._process.wait(timeout=10)
                self._process.stdin.close()
                self._process.stdout.close()
                self._process = None
