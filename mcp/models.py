from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class MCPRequest(BaseModel):
    tool: str = Field(..., description="The name of the tool to be executed.")
    args: Optional[Dict[str, Any]] = Field(None, description="The arguments for the tool.")

class MCPResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
