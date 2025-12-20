from aiohttp import web
from .routes import setup_routes
from .tools import MCPTools
from .middleware import api_key_middleware
from config.settings import settings

def create_mcp_app(discord_client, sheets_service) -> web.Application:
    app = web.Application(middlewares=[api_key_middleware])
    app["settings"] = settings
    app["mcp_tools"] = MCPTools(settings, discord_client, sheets_service)
    setup_routes(app)
    return app

async def run_mcp_server(discord_client, sheets_service):
    app = create_mcp_app(discord_client, sheets_service)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", settings.MCP_PORT)
    await site.start()
    print(f"MCP Server running on http://localhost:{settings.MCP_PORT}")
