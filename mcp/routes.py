from aiohttp import web
from .models import MCPRequest, MCPResponse
from .tools import MCPTools

async def mcp_handler(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        mcp_request = MCPRequest(**data)
        
        mcp_tools: MCPTools = request.app["mcp_tools"]
        
        result = await mcp_tools.execute_tool(mcp_request.tool, mcp_request.args)
        
        response = MCPResponse(success=True, result=result)
        return web.json_response(response.dict())
    
    except Exception as e:
        response = MCPResponse(success=False, error=str(e))
        return web.json_response(response.dict(), status=500)

def setup_routes(app: web.Application):
    app.router.add_post("/mcp", mcp_handler)
