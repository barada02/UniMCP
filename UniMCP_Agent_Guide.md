# UniMCP Library Documentation for Agents

## Overview
UniMCP is a Python client library for connecting to Model Context Protocol (MCP) servers and orchestrating tool-use with LLMs.

## Core Components

### 1. `UniClient` (src/unimcp/client.py)
Handles the connection and communication with MCP servers.
- **Constructor**: `UniClient(endpoint: Optional[str] = None, command: Optional[str] = None, args: Optional[List[str]] = None)`
- **Endpoint Resolution**: Priority is `endpoint` argument $\rightarrow$ `MCP_SERVER` env var.
- **Transport Types**: 
    - SSE: If endpoint starts with `http://` or `https://`.
    - Stdio: Otherwise (e.g., `.py` files).
- **Key Methods**:
    - `async connect()`: Establishes connection.
    - `async disconnect()`: Closes connection.
    - `async __aenter__` / `__aexit__`: Supports `async with` context manager.
    - `async get_tools()`: Returns list of available tools.
    - `async call_tool(tool_name, arguments)`: Executes a tool and returns text response.
    - `async load_tools()`: Dynamically generates a toolset object where MCP tools are native Python methods.
    - `async explore()`: Returns dictionary of available tools, prompts, and resources.

### 2. `UniLLM` (src/unimcp/llm.py)
OpenAI-compatible wrapper that manages the tool-execution loop.
- **Constructor**: `UniLLM(mcp_client, api_key=None, base_url=None, model_name=None, provider=None)`
- **Env Var Priority**: Arguments $\rightarrow$ `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME`.
- **Key Methods**:
    - `async chat(user_input, session=None, stream=False)`: Main entry point. Handles the loop: LLM $\rightarrow$ Tool Call $\rightarrow$ UniClient Execution $\rightarrow$ LLM $\rightarrow$ Final Response.
    - `create_session(name=None, system_prompt=None, auto_save=False)`: Returns a new `Session` object.
    - `set_system_prompt(prompt, session=None)`: Updates the system prompt.

### 3. `Session` (src/unimcp/session/session.py)
Manages conversation state and history.
- **Attributes**: `messages` (list of OpenAI-format dicts), `system_prompt`.
- **Key Methods**:
    - `async save(filepath)`: Persists session to JSON.
    - `async load(filepath)`: Static method to load a session.
    - `clear_history()`: Resets messages but keeps system prompt.

### 4. `InteractiveChat` (src/unimcp/interactive.py)
Provides the loop for terminal-based interaction.
- **Method**: `async run()`: Starts the REPL loop.

## Configuration (Environment Variables)
The library relies on the following `.env` variables:
- `MCP_SERVER`: Endpoint for the MCP server (URL or file path).
- `LLM_API_KEY`: API key for the LLM provider.
- `LLM_BASE_URL`: Base URL for the API endpoint.
- `LLM_MODEL_NAME`: Name of the model to use.

## CLI Reference (`unimcp-chat`)
The CLI is a wrapper around the library.
- **Command**: `unimcp-chat`
- **Flags**: `--url`, `--api-key`, `--base-url`, `--model`, `--provider`, `--system-prompt`.
- **Flow**: Resolves endpoint $\rightarrow$ `UniClient` $\rightarrow$ `UniLLM` $\rightarrow$ `InteractiveChat`.

## Project Structure
- `src/unimcp/`: Core library logic.
- `src/unimcp/session/`: Session and storage management.
- `examples/`: End-user implementation examples.
- `reference/`: Test servers and reference implementations.
