from aiohttp import web
from aiohttp.web import Request, StreamResponse, middleware
from config.settings import Settings

@middleware
async def api_key_middleware(request: Request, handler) -> StreamResponse:
    if request.path == "/mcp":
        api_key = request.headers.get("Authorization")
        settings: Settings = request.app["settings"]
        if not api_key or api_key != f"Bearer {settings.MCP_API_KEY}":
            raise web.HTTPUnauthorized(text="Unauthorized")
    return await handler(request)
