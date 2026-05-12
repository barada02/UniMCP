import asyncio
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import importlib.resources

from unimcp.client import UniClient
from unimcp.exceptions import ConnectionError, NotConnectedError

app = FastAPI(title="UniMCP Dashboard API")

# --- State Management ---
# We use a simple global state for the client.
# In a production app, we'd use a session manager, but for a local dev tool, a singleton is fine.
class ClientState:
    def __init__(self):
        self.client: Optional[UniClient] = None
        self.loop = asyncio.get_event_loop()

state = ClientState()

# --- Models ---
class ConnectRequest(BaseModel):
    endpoint: str
    command: Optional[str] = None
    args: Optional[List[str]] = None

class ExecuteRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

# --- API Endpoints ---
@app.get("/")
async def read_index():
    # Use importlib.resources to find the static folder relative to this package
    # This ensures PyPI compatibility
    with importlib.resources.files("unimcp.web.static").joinpath("index.html") as f:
        return FileResponse(f, media_type="text/html")

# Mount static files for JS/CSS
# Note: We'll mount this in the main entry point if needed,
# but for now we'll define the route.
def mount_static():
    static_path = importlib.resources.files("unimcp.web.static")
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.post("/api/connect")
async def connect(req: ConnectRequest):
    try:
        # If already connected, disconnect first
        if state.client:
            await state.client.disconnect()

        state.client = UniClient(endpoint=req.endpoint, command=req.command, args=req.args)
        await state.client.connect()
        return {"status": "connected", "endpoint": req.endpoint}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/disconnect")
async def disconnect():
    if not state.client:
        return {"status": "already disconnected"}

    try:
        await state.client.disconnect()
        state.client = None
        return {"status": "disconnected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/explore")
async def explore():
    if not state.client:
        raise HTTPException(status_code=400, detail="Client not connected")

    try:
        return await state.client.explore()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tool/{name}")
async def get_tool(name: str):
    if not state.client:
        raise HTTPException(status_code=400, detail="Client not connected")

    try:
        return await state.client.get_tool_details(name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute")
async def execute(req: ExecuteRequest):
    if not state.client:
        raise HTTPException(status_code=400, detail="Client not connected")

    try:
        result = await state.client.call_tool(req.tool, req.arguments)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
