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

## 🚀 Interactive CLI

The CLI provides a quick way to chat with your MCP server without writing any code.

### Quick Start
Run the chat command from your terminal:
```bash
unimcp-chat
```

### Configuration
The CLI uses environment variables from your `.env` file by default. To make it work, add these to your `.env`:
- `MCP_SERVER`: The endpoint of your server (e.g., `http://localhost:8000/sse` or `reference/server.py`).
- `LLM_API_KEY`: Your LLM provider API key.
- `LLM_BASE_URL`: The API base URL (e.g., for NVIDIA NIM or Gemini).
- `LLM_MODEL_NAME`: The specific model you wish to use.

### CLI Options
You can override environment variables using flags:
- `--url <url>`: Override the server endpoint.
- `--api-key <key>`: Override the API key.
- `--base-url <url>`: Override the LLM base URL.
- `--model <name>`: Override the model name.
- `--system-prompt "text"`: Set a custom system instruction.

**Example:**
```bash
unimcp-chat --url http://localhost:8000/sse --model meta/llama-3.1-70b --api-key sk-123...
```

---
