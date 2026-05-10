<div align="center">

```text
 _   _       _ __  __  ____ ____ 
| | | | ___ (_)  \/  |/ ___|  _ \
| | | |/ _ \| | |\/| | |   | |_) |
| |_| | | | | | |  | | |___|  __/ 
 \___/|_| |_|_|_|  |_|\____|_|    
  Universal MCP Client
```

</div>

# UniMCP

A simple, Python-native client library to connect to any Model Context Protocol (MCP) server. UniMCP allows you to interact with tools seamlessly via native Python code, an interactive CLI, or an autonomous LLM agent.

## Features

- **Multiple Transports**: Connect to remote servers via **SSE** (`http://...`) or local executables via **Stdio** (`server.py`, `npx ...`).
- **Dynamic Tool Generation**: Automatically converts MCP tools into native Python `async` functions with IDE support.
- **Interactive CLI Playground**: Test and chat with your tools straight from the terminal.
- **LLM Integration**: Built-in, provider-agnostic LLM wrapper (OpenAI, Groq, Ollama, etc.) to hook your MCP server tools directly into an autonomous agent.
- **Session Management**: Automatically persist and resume multi-turn conversations with context awareness.

## Installation

```bash
pip install unimcp
```

*(Note: While in development, you can install it locally using `pip install -e .`)*

---

## ⚡ Quick Start: Interactive CLI Playground

The easiest way to test an MCP server is using the built-in interactive CLI. 

Once installed, you can use the `unimcp-chat` command:

```bash
# Connect to a remote SSE server
unimcp-chat --url http://localhost:8000/sse

# Connect to a local python server (Stdio)
unimcp-chat --url my_local_server.py
```

**CLI Options:**
```bash
unimcp-chat --url http://localhost:8000/sse \
            --model gpt-4o \
            --api-key sk-... \
            --provider openai \
            --system-prompt "You are a helpful assistant."
```
*(If you have `OPENAI_API_KEY` set in your environment, you don't need to pass the `--api-key` flag!)*

---

## 🐍 Python API Usage

### 1. Dynamic Tool Execution (The Pythonic Way)

Forget manually formatting JSON payloads. UniMCP dynamically generates native Python functions for your tools.

```python
import asyncio
from unimcp import UniClient

async def main():
    # Connect to a local server script (Stdio transport)
    async with UniClient("server.py") as client:
        
        # Explore available capabilities
        exploration = await client.explore()
        print("Available tools:", exploration["tools"])
        
        # Load tools as native Python functions!
        tools = await client.load_tools()
        
        # Call them directly like normal functions
        weather = await tools.get_weather(city="Seattle")
        print("Weather:", weather)
        
        status = await tools.get_system_status()
        print("Status:", status)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Connecting to Servers (Stdio vs SSE)

UniMCP handles both local and remote MCP servers effortlessly:

```python
# 1. Local Python script (Stdio)
client = UniClient("my_server.py")

# 2. Local Node/npx server (Stdio)
client = UniClient("npx", args=["-y", "@modelcontextprotocol/server-postgres", "postgres://..."])

# 3. Remote Server (SSE)
client = UniClient("http://localhost:8000/sse")
```

### 3. Using the LLM Client

UniLLM connects your MCP server to any OpenAI-compatible LLM API. The LLM will autonomously call MCP tools as needed to answer user queries.

```python
import asyncio
from unimcp import UniClient, UniLLM

async def main():
    async with UniClient("http://localhost:8000/sse") as client:
        
        # UniLLM automatically loads OPENAI_API_KEY from environment variables
        llm = UniLLM(client)
        
        llm.set_system_prompt("You are a helpful assistant with access to MCP tools.")
        
        # The LLM will decide which tools to call, execute them, and return a final answer
        response = await llm.chat("What's the weather in Seattle and should I bring an umbrella?")
        print("AI:", response)

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Session Management & Persistent Conversations

For multi-turn conversations or saving chat history to disk, you can use explicit Sessions.

```python
import asyncio
from unimcp import UniClient, UniLLM

async def main():
    async with UniClient("http://localhost:8000/sse") as client:
        llm = UniLLM(client)
        
        # 1. Create a persistent session
        session = llm.create_session(
            name="support_ticket",
            system_prompt="You are a helpful assistant."
        )
        
        # 2. Chat with context
        await llm.chat("Save contact: Alice, phone 555-1234", session=session)
        await llm.chat("Who are my saved contacts?", session=session)
        
        # 3. Save the conversation to disk
        await session.save("ticket.json")
        
        # 4. Later, load it back and continue
        loaded_session = await UniLLM.load_session("ticket.json")
        await llm.chat("Add Bob too", session=loaded_session)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ⚙️ UniLLM Configuration Reference

UniLLM supports a variety of providers out-of-the-box.

### Parameters

| Parameter | Type | Required? | Priority | Description |
|-----------|------|-----------|----------|-------------|
| `mcp_client` | UniClient | ✅ Yes | - | Connected MCP client |
| `api_key` | str | ❌ No | Param > Env | LLM API key. Uses `OPENAI_API_KEY` env var if not provided |
| `model_name` | str | ❌ No | Param > Env | Model to use. Default: `gpt-4o`. Uses `OPENAI_MODEL` env var if not provided |
| `base_url` | str | ❌ No | Param > Env | API endpoint URL. Uses `OPENAI_BASE_URL` env var if not provided. |
| `provider` | str | ❌ No | Param | Auto-selects base URL (`openai`, `groq`, `ollama`, `vllm`, `gemini`, etc.) |

### Example: Using Groq

```python
llm = UniLLM(
    client,
    api_key="your-groq-api-key",
    model_name="mixtral-8x7b-32768",
    provider="groq"  # Automatically uses https://api.groq.com/openai/v1
)
```

### Supported Auto-Providers (`provider` param)
`openai`, `groq`, `openrouter`, `together`, `deepseek`, `ollama`, `vllm`, `lmstudio`, `xai`, `gemini`.
