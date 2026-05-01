# UniMCP

A simple client library to connect to any MCP server and interact with tools seamlessly via code or through an LLM.

## Installation

```bash
pip install unimcp
```

*(Note: While in development, you can install it locally using `pip install -e .`)*

## Features
- **Simple MCP Client**: Connect to any MCP server, list available tools, and call them directly with just a few lines of Python.
- **LLM Integration**: Built-in wrapper to hook your MCP server tools directly into OpenAI (or any OpenAI-compatible API), enabling an LLM agent out-of-the-box.

## Usage

### 1. Using only the MCP Client (No LLM)

```python
import asyncio
from unimcp import UniClient

async def main():
    # Connect to your MCP server
    async with UniClient("http://localhost:8000/sse") as client:
        # 1. Get available tools
        tools = await client.get_tools()
        print("Available tools:", [t.name for t in tools])

        # 2. Call a specific tool manually
        result = await client.call_tool("my_tool_name", {"arg1": "value"})
        print("Tool Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Using the LLM Client

This utilizes OpenAI's python library under the hood. You can configure it using environment variables (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`) or pass them directly.

```python
import asyncio
from unimcp import UniClient, UniLLM

async def main():
    async with UniClient("http://localhost:8000/sse") as client:
        
        # Initialize the LLM with the MCP client
        # It automatically detects OPENAI_API_KEY from environment variables
        llm = UniLLM(client, model_name="gpt-4o")
        
        # Optionally set a system prompt
        llm.set_system_prompt("You are a helpful assistant with access to MCP tools.")

        # Chat with the LLM (it will automatically use the tools if needed)
        response = await llm.chat("Can you perform an action using your tools?")
        print("AI:", response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Variables
The `UniLLM` automatically respects the following standard environment variables:
- `OPENAI_API_KEY`: Your API key.
- `OPENAI_BASE_URL`: For connecting to local LLMs (like LMStudio, Ollama) or other providers.
- `OPENAI_MODEL`: Default model to use (fallback is `gpt-4o`).
