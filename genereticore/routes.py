"""Local same-origin API for explicit live submissions; no capture APIs."""
from dataclasses import asdict
import ipaddress
from urllib.parse import urlsplit
from .catalog import model_entry
from .contracts import Request
from .service import get_runtime


def require_local(request):
    from aiohttp import web
    try:
        if not ipaddress.ip_address(request.remote).is_loopback:
            raise ValueError()
    except (ValueError, TypeError):
        raise web.HTTPForbidden(text="GeneretiCore inference API is loopback-only")
    origin = request.headers.get("Origin")
    if origin and urlsplit(origin).netloc != request.host:
        raise web.HTTPForbidden(text="Same-origin requests required")
    if request.headers.get("Sec-Fetch-Site") == "cross-site":
        raise web.HTTPForbidden(text="Same-origin requests required")


def register_routes(routes):
    from aiohttp import web

    @routes.get('/genereticore/status')
    async def status(request):
        require_local(request)
        runtime = get_runtime()
        return web.json_response({"capability": asdict(runtime.backend.capability()),
            "models": runtime.backend.catalog(), **runtime.status()})

    @routes.post('/genereticore/tasks')
    async def submit(request):
        require_local(request)
        if request.content_length and request.content_length > 8_000_000:
            raise web.HTTPRequestEntityTooLarge(max_size=8_000_000, actual_size=request.content_length)
        try:
            data = await request.json()
            # Ignore caller-supplied paths/backends/IDs: this API only exposes the allowlisted local catalog.
            task = data["task"]
            model_entry(data["model"], task)
            item = Request(task, data["model"], data.get("inputs", {}), data.get("options", {}),
                data.get("input_revision", 0), data.get("stream_id", "live"))
            runtime = get_runtime()
            cap = runtime.backend.capability()
            if not cap.available:
                raise web.HTTPServiceUnavailable(text=cap.reason)
            if task != "model.download" and not runtime.backend.installed(model_entry(item.model)):
                raise web.HTTPConflict(text="Model missing; download it explicitly first")
            job = runtime.submit(item, policy=data.get("policy", "latest"))
            return web.json_response({"request_id": job.request.request_id}, status=202)
        except (ValueError, TypeError, KeyError) as exc:
            raise web.HTTPBadRequest(text=str(exc)) from exc
        except RuntimeError as exc:
            raise web.HTTPTooManyRequests(text=str(exc)) from exc

    @routes.get('/genereticore/tasks/{id}')
    async def events(request):
        require_local(request)
        try:
            after = int(request.query.get("after", "0"))
            return web.json_response(get_runtime().snapshot(request.match_info["id"], after))
        except KeyError as exc:
            raise web.HTTPNotFound(text="Unknown or expired request") from exc
        except ValueError as exc:
            raise web.HTTPBadRequest(text="Invalid event cursor") from exc

    @routes.post('/genereticore/tasks/{id}/cancel')
    async def cancel(request):
        require_local(request)
        try:
            return web.json_response({"canceled": get_runtime().cancel(request.match_info["id"])})
        except KeyError as exc:
            raise web.HTTPNotFound(text="Unknown or expired request") from exc
