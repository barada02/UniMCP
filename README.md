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

---
