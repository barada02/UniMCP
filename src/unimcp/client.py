import asyncio
from typing import Optional, List, Dict, Any
from mcp import ClientSession
from contextlib import AsyncExitStack

class UniClient:
    """
    A unified MCP Client that connects to an MCP server (SSE or Stdio)
    and allows execution of tools.
    """
    def __init__(self, endpoint: str, command: Optional[str] = None, args: Optional[List[str]] = None):
        """
        :param endpoint: A URL (http://...) for remote SSE, or a file path (e.g., 'server.py') for local Stdio.
        :param command: Explicit command to run for Stdio (e.g., 'python'). If None, inferred from endpoint.
        :param args: Additional arguments for the Stdio command.
        """
        self.endpoint = endpoint
        self.command = command
        self.args = args or []
        self.session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None

    async def connect(self):
        """Connects to the MCP server."""
        self._exit_stack = AsyncExitStack()
        
        if self.endpoint.startswith("http://") or self.endpoint.startswith("https://"):
            from mcp.client.sse import sse_client
            read_stream, write_stream = await self._exit_stack.enter_async_context(sse_client(url=self.endpoint))
        else:
            from mcp.client.stdio import stdio_client, StdioServerParameters
            
            cmd = self.command
            arguments = self.args
            
            # Infer command if not explicitly provided
            if not cmd:
                if self.endpoint.endswith(".py"):
                    cmd = "python"
                    arguments = [self.endpoint] + self.args
                elif self.endpoint.endswith(".js"):
                    cmd = "node"
                    arguments = [self.endpoint] + self.args
                else:
                    # Treat endpoint as the command executable itself
                    cmd = self.endpoint
                    
            server_params = StdioServerParameters(
                command=cmd,
                args=arguments
            )
            read_stream, write_stream = await self._exit_stack.enter_async_context(stdio_client(server_params))

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

    async def explore(self) -> Dict[str, List[str]]:
        """
        Explores the connected MCP server and returns the names of available tools, 
        prompts, and resources.
        """
        if not self.session:
            raise RuntimeError("Client not connected. Call connect() first.")
            
        exploration_data = {
            "tools": [],
            "prompts": [],
            "resources": []
        }
        
        # Get Tools
        try:
            tools_response = await self.session.list_tools()
            if tools_response and hasattr(tools_response, 'tools'):
                exploration_data["tools"] = [tool.name for tool in tools_response.tools]
        except Exception as e:
            print(f"Notice: Failed to fetch tools: {e}")
            
        # Get Prompts
        try:
            prompts_response = await self.session.list_prompts()
            if prompts_response and hasattr(prompts_response, 'prompts'):
                exploration_data["prompts"] = [prompt.name for prompt in prompts_response.prompts]
        except Exception as e:
            pass # Server might not support prompts
            
        # Get Resources
        try:
            resources_response = await self.session.list_resources()
            if resources_response and hasattr(resources_response, 'resources'):
                exploration_data["resources"] = [resource.name for resource in resources_response.resources]
        except Exception as e:
            pass # Server might not support resources
            
        return exploration_data
