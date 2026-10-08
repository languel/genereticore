"""Lazy shared service: no helper, model loading or download at import time."""
import atexit
import threading
import os
from .coreml import LocalBackend
from .runtime import TaskRuntime

_runtime = None
_lock = threading.Lock()

def get_runtime():
    global _runtime
    with _lock:
        if _runtime is None:
            try:
                import folder_paths
                from pathlib import Path
                paths = folder_paths.get_folder_paths("genereticore")
                model_dir = paths[0] if paths else str(Path(folder_paths.models_dir) / "genereticore")
            except (ImportError, KeyError):
                model_dir = None
            _runtime = TaskRuntime(LocalBackend(model_dir=os.environ.get("GENERETICORE_MODEL_DIR", model_dir)))
        return _runtime


def close_runtime():
    global _runtime
    with _lock:
        if _runtime:
            _runtime.close()
            _runtime = None

atexit.register(close_runtime)
