"""Comfy entry point. Does not register or replace Genereti's legacy Core ML IDs."""
from .genereticore.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
WEB_DIRECTORY = "./web"

try:
    import folder_paths
    from pathlib import Path
    folder_paths.add_model_folder_path("genereticore", str(Path(folder_paths.models_dir) / "genereticore"))
    from server import PromptServer
    if getattr(PromptServer, "instance", None) is not None:
        from .genereticore.routes import register_routes
        register_routes(PromptServer.instance.routes)
        from .genereticore.examples import install_for_profiles
        install_for_profiles(Path(__file__).resolve().parent)
except ImportError:
    pass

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
