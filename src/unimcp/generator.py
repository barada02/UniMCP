from typing import Any, List

class DynamicToolset:
    """A collection of dynamically generated native Python tool methods."""
    pass

class ToolFunctionGenerator:
    """
    Responsible for dynamically generating native Python methods 
    from available MCP tools.
    """
    def __init__(self, client):
        # We store a reference to the client to make the actual execution calls
        self.client = client

    async def generate(self, tools_list: List[Any]) -> Any:
        toolset = DynamicToolset()
        
        for tool in tools_list:
            func = self._create_function(tool.name, tool.description)
            setattr(toolset, tool.name, func)
            
        return toolset

    def _create_function(self, tool_name: str, tool_description: str):
        # We define the inner async function that acts as the callable
        async def native_tool_call(**kwargs):
            return await self.client.call_tool(tool_name, kwargs)
        
        native_tool_call.__name__ = tool_name
        native_tool_call.__doc__ = tool_description
        return native_tool_call
