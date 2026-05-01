import asyncio
from typing import Optional, List, Dict, Any
from mcp import ClientSession
from mcp.client.sse import sse_client
from contextlib import AsyncExitStack

class UniClient:
    """
    A unified MCP Client that connects to an MCP server (SSE by default)
    and allows execution of tools.
    """
    def __init__(self, url: str):
        self.url = url
        self.session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None

    async def connect(self):
        """Connects to the MCP server."""
        self._exit_stack = AsyncExitStack()
        read_stream, write_stream = await self._exit_stack.enter_async_context(sse_client(url=self.url))
        self.session = await self._exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await self.session.initialize()

    async def disconnect(self):
        """Disconnects from the MCP server."""
        if self._exit_stack:
            await self._exit_stack.aclose()
            self._exit_stack = None
            self.session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def get_tools(self) -> List[Any]:
        """Lists available tools from the MCP server."""
        if not self.session:
            raise RuntimeError("Client not connected. Call connect() first.")
        response = await self.session.list_tools()
        return response.tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Executes a tool on the MCP server and returns the text result."""
        if not self.session:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        result = await self.session.call_tool(tool_name, arguments=arguments)
        
        # Read the response text from the server
        tool_result_str = ""
        for content in result.content:
            if content.type == "text":
                tool_result_str += content.text
        return tool_result_str
