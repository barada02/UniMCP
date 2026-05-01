from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
import json
import os
from .session import Session

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
        model_name: Optional[str] = None,
        provider: Optional[str] = None
    ):
        from .constants import PROVIDER_BASE_URLS
        
        self.mcp_client = mcp_client
        self.messages: List[Dict[str, Any]] = []
        
        kwargs = {}
        # Priority: arguments > environment variables
        final_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if final_api_key:
            kwargs["api_key"] = final_api_key
            
        final_base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        # If no explicit base_url, but a provider is given, look it up in constants
        if not final_base_url and provider:
            provider_key = provider.lower()
            if provider_key in PROVIDER_BASE_URLS:
                final_base_url = PROVIDER_BASE_URLS[provider_key]
                
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

    def set_system_prompt(self, prompt: str, session: Optional[Session] = None):
        """
        Sets the system prompt for the LLM.
        
        Args:
            prompt: System prompt text
            session: Optional session to set prompt on. If None, sets on default ephemeral session.
        """
        target_messages = session.messages if session else self.messages
        
        if target_messages and target_messages[0]["role"] == "system":
            target_messages[0]["content"] = prompt
        else:
            target_messages.insert(0, {"role": "system", "content": prompt})
        
        if session:
            session.system_prompt = prompt

    async def chat(self, user_input: str, session: Optional[Session] = None) -> str:
        """
        Sends a user message to the LLM and processes any required tool calls 
        from the MCP server before returning the final text response.
        
        Args:
            user_input: User's message
            session: Optional explicit session. If None, uses ephemeral in-memory session.
        
        Returns:
            LLM's final text response
        """
        # Use provided session or ephemeral in-memory session
        if session is None:
            session = Session()  # Temporary session, will be GC'd
        
        target_messages = session.messages
        target_messages.append({"role": "user", "content": user_input})
        
        mcp_tools = await self.mcp_client.get_tools()
        available_openai_tools = self._convert_mcp_to_openai_tools(mcp_tools)
        
        while True:
            chat_kwargs = {
                "model": self.model_name,
                "messages": target_messages,
            }
            if available_openai_tools:
                chat_kwargs["tools"] = available_openai_tools
                chat_kwargs["tool_choice"] = "auto"
                
            response = await self.client.chat.completions.create(**chat_kwargs)
            response_message = response.choices[0].message
            
            # Convert OpenAI message object to JSON-serializable dict
            message_dict = {
                "role": response_message.role,
                "content": response_message.content
            }
            
            # Add tool_calls if present
            if response_message.tool_calls:
                message_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response_message.tool_calls
                ]
            
            # Append the assistant's message to the history
            target_messages.append(message_dict)
            
            # If the LLM decides to call a tool (or multiple tools)
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Execute tool via MCP client
                    tool_result_str = await self.mcp_client.call_tool(tool_name, tool_args)
                    
                    # Feed the result back to the LLM
                    target_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_result_str
                    })
                # After resolving tools, loop to let the LLM generate a final text response
            else:
                return response_message.content
    
    def create_session(
        self,
        name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        auto_save: bool = False
    ) -> Session:
        """
        Create a new persistent or auto-save session.
        
        Args:
            name: Optional name for the session
            system_prompt: Optional system prompt for this session
            auto_save: If True, saves state to memory (not disk) after each chat
        
        Returns:
            Session object
        
        Example:
            session = llm.create_session(name="support_ticket_123")
            response = await llm.chat("How can I help?", session=session)
            await session.save("conversations/123.json")
        """
        session = Session(
            name=name,
            system_prompt=system_prompt,
            auto_save=auto_save
        )
        return session
    
    @staticmethod
    async def load_session(filepath: str) -> Session:
        """
        Load a previously saved session.
        
        Args:
            filepath: Path to the saved session file
        
        Returns:
            Loaded Session object
        
        Example:
            session = await UniLLM.load_session("conversations/123.json")
            response = await llm.chat("Continue...", session=session)
        """
        return await Session.load(filepath)
