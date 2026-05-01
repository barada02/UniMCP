from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
import json
import os

class UniLLM:
    """
    A unified LLM wrapper that connects to OpenAI (or any OpenAI-compatible API)
    and automatically executes tools provided by a UniClient.
    """
    def __init__(
        self,
        mcp_client,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        self.mcp_client = mcp_client
        self.messages: List[Dict[str, Any]] = []
        
        kwargs = {}
        # Priority: arguments > environment variables
        final_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if final_api_key:
            kwargs["api_key"] = final_api_key
            
        final_base_url = base_url or os.getenv("OPENAI_BASE_URL")
        if final_base_url:
            kwargs["base_url"] = final_base_url
            
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.client = AsyncOpenAI(**kwargs)

    def _convert_mcp_to_openai_tools(self, mcp_tools) -> list:
        openai_tools = []
        for tool in mcp_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        return openai_tools

    def set_system_prompt(self, prompt: str):
        """Sets the system prompt for the LLM."""
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = prompt
        else:
            self.messages.insert(0, {"role": "system", "content": prompt})

    async def chat(self, user_input: str) -> str:
        """
        Sends a user message to the LLM and processes any required tool calls 
        from the MCP server before returning the final text response.
        """
        self.messages.append({"role": "user", "content": user_input})
        
        mcp_tools = await self.mcp_client.get_tools()
        available_openai_tools = self._convert_mcp_to_openai_tools(mcp_tools)
        
        while True:
            chat_kwargs = {
                "model": self.model_name,
                "messages": self.messages,
            }
            if available_openai_tools:
                chat_kwargs["tools"] = available_openai_tools
                chat_kwargs["tool_choice"] = "auto"
                
            response = await self.client.chat.completions.create(**chat_kwargs)
            response_message = response.choices[0].message
            
            # Append the assistant's message to the history
            self.messages.append(response_message)
            
            # If the LLM decides to call a tool (or multiple tools)
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Execute tool via MCP client
                    tool_result_str = await self.mcp_client.call_tool(tool_name, tool_args)
                    
                    # Feed the result back to the LLM
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_result_str
                    })
                # After resolving tools, loop to let the LLM generate a final text response
            else:
                return response_message.content
