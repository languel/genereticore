"""Comfy entry point. Preserves migrated native Core ML IDs; rejects duplicate legacy installs."""
from .genereticore.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
WEB_DIRECTORY = "./web"

try:
    import folder_paths
    from pathlib import Path
    folder_paths.add_model_folder_path("genereticore", str(Path(folder_paths.models_dir) / "genereticore"))
    # Fail before registering routes if the optional legacy pack is also active.
    from comfy.cli_args import args
    for base in folder_paths.get_folder_paths('custom_nodes'):
        if (Path(base) / 'genereti_comfy_coreml').is_dir() and (not args.disable_all_custom_nodes or 'genereti_comfy_coreml' in args.whitelist_custom_nodes):
            raise RuntimeError('Duplicate native generator IDs: move genereti_comfy_coreml outside custom_nodes before enabling GeneretiCore. Keep workflows and models.')
    from .genereticore.image.nodes import NODE_CLASS_MAPPINGS as IMAGE_NODES, NODE_DISPLAY_NAME_MAPPINGS as IMAGE_LABELS
    from .genereticore.upscale.nodes import GeneretiCoreUpscale
    from .genereticore.browser.nodes import GeneretiCoreBrowserUpscale
    IMAGE_NODES = {**IMAGE_NODES, "GeneretiCoreUpscale": GeneretiCoreUpscale, "GeneretiCoreBrowserUpscale": GeneretiCoreBrowserUpscale}
    IMAGE_LABELS = {**IMAGE_LABELS, "GeneretiCoreUpscale": "ꘅ Real-ESRGAN upscale"}
    NODE_CLASS_MAPPINGS = {**NODE_CLASS_MAPPINGS, **IMAGE_NODES}
    NODE_DISPLAY_NAME_MAPPINGS = {**NODE_DISPLAY_NAME_MAPPINGS, **IMAGE_LABELS}
    from server import PromptServer
    if getattr(PromptServer, "instance", None) is not None:
        from .genereticore.routes import register_routes
        register_routes(PromptServer.instance.routes)
        from .genereticore.image.live import register_routes as register_image_routes
        register_image_routes(PromptServer.instance.routes)
        from .genereticore.upscale.live import register_routes as register_upscale_routes
        register_upscale_routes(PromptServer.instance.routes)
        from .genereticore.browser.assets import register_routes as register_browser_routes
        register_browser_routes(PromptServer.instance.routes)
        from .genereticore.examples import install_for_profiles
        install_for_profiles(Path(__file__).resolve().parent)
except ImportError:
    pass

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
