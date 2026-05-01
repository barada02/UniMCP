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

UniLLM connects your MCP server to any OpenAI-compatible LLM API. The LLM will autonomously call MCP tools as needed to answer user queries.

#### Configuration Priority: **Parameters > Environment Variables > Defaults**

You can configure UniLLM in three ways:

**Option A: Pass all parameters explicitly**
```python
import asyncio
from unimcp import UniClient, UniLLM

async def main():
    async with UniClient("http://localhost:8000/sse") as client:
        # Explicit configuration (parameters override env vars)
        llm = UniLLM(
            client,
            api_key="sk-...",                          # Your OpenAI API key
            model_name="gpt-4o",                       # Model to use
            base_url="https://api.openai.com/v1"      # Optional: OpenAI is default
        )
        
        llm.set_system_prompt("You are a helpful assistant with access to MCP tools.")
        response = await llm.chat("Can you perform an action using your tools?")
        print("AI:", response)

if __name__ == "__main__":
    asyncio.run(main())
```

**Option B: Use environment variables only**
```python
# Set these environment variables first:
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o
# OPENAI_BASE_URL=https://api.openai.com/v1  (optional, defaults to OpenAI)

import asyncio
from unimcp import UniClient, UniLLM

async def main():
    async with UniClient("http://localhost:8000/sse") as client:
        # AutomaticallyLoads from environment variables
        llm = UniLLM(client)
        
        llm.set_system_prompt("You are a helpful assistant with access to MCP tools.")
        response = await llm.chat("Can you perform an action using your tools?")
        print("AI:", response)

if __name__ == "__main__":
    asyncio.run(main())
```

**Option C: Mix both (parameters override env vars)**
```python
# Set in .env or environment:
# OPENAI_API_KEY=sk-...
# OPENAI_BASE_URL=https://api.openai.com/v1

import asyncio
from unimcp import UniClient, UniLLM

async def main():
    async with UniClient("http://localhost:8000/sse") as client:
        # api_key from env, but override model
        llm = UniLLM(
            client,
            model_name="gpt-4-turbo"  # Override default from env
        )
        
        llm.set_system_prompt("You are a helpful assistant with access to MCP tools.")
        response = await llm.chat("Can you perform an action using your tools?")
        print("AI:", response)

if __name__ == "__main__":
    asyncio.run(main())
```

**Option D: Use with provider name (for non-OpenAI APIs)**
```python
import asyncio
from unimcp import UniClient, UniLLM

async def main():
    async with UniClient("http://localhost:8000/sse") as client:
        # Use provider name to auto-select base_url
        llm = UniLLM(
            client,
            api_key="your-groq-api-key",
            model_name="mixtral-8x7b-32768",
            provider="groq"  # Auto-selects https://api.groq.com/openai/v1
        )
        
        response = await llm.chat("What can you do?")
        print("AI:", response)

if __name__ == "__main__":
    asyncio.run(main())
```

## UniLLM Configuration Reference

### Parameters

| Parameter | Type | Required? | Priority | Description |
|-----------|------|-----------|----------|-------------|
| `mcp_client` | UniClient | ✅ Yes | - | Connected MCP client |
| `api_key` | str | ❌ No | Param > Env | LLM API key. Uses `OPENAI_API_KEY` env var if not provided |
| `model_name` | str | ❌ No | Param > Env | Model to use. Default: `gpt-4o`. Uses `OPENAI_MODEL` env var if not provided |
| `base_url` | str | ❌ No | Param > Env | API endpoint URL. Uses `OPENAI_BASE_URL` env var if not provided. Defaults to OpenAI |
| `provider` | str | ❌ No | Param | Provider name (`openai`, `groq`, `together`, `openrouter`, `deepseek`, `ollama`, `vllm`, `lmstudio`, `xai`, `gemini`). Only used if `base_url` not explicitly provided |

### Environment Variables

Set these in your `.env` file or system environment:

```bash
# Required (or pass as parameter)
OPENAI_API_KEY=sk-...

# Optional
OPENAI_MODEL=gpt-4o              # Default: gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1  # Default: OpenAI
```

### Supported Providers (Auto base_url)

If you provide `provider` parameter (and no explicit `base_url`), these are auto-selected:

```python
{
    "openai": "https://api.openai.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "together": "https://api.together.xyz/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "ollama": "http://localhost:11434/v1",
    "vllm": "http://localhost:8000/v1",
    "lmstudio": "http://localhost:1234/v1",
    "xai": "https://api.x.ai/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/"
}
