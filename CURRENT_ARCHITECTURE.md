# UniMCP Architecture

## Overview
UniMCP is a Python-native, framework-agnostic client for interacting with Model Context Protocol (MCP) servers. The current implementation provides a unified interface to connect to MCP servers, explore their capabilities, dynamically convert MCP tools into callable Python functions, and interact with an LLM to autonomously trigger these tools.

## Core Architecture

The system is organized into a modular set of components that separate the client connectivity, dynamic generation of tools, and LLM orchestration.

```mermaid
classDiagram
    class UniClient {
        +endpoint: str
        +command: Optional[str]
        +args: List[str]
        +session: Optional[ClientSession]
        +connect()
        +disconnect()
        +get_tools() List
        +call_tool(tool_name, arguments) str
        +explore() Dict
        +get_tool_details(tool_name) Dict
        +load_tools() Any
    }

    class ToolFunctionGenerator {
        +client: UniClient
        +generate(tools_list) DynamicToolset
        -_create_function(tool_name, tool_description)
    }

    class UniLLM {
        +mcp_client: UniClient
        +messages: List[Dict]
        +client: AsyncOpenAI
        +set_system_prompt(prompt)
        +chat(user_input) str
        -_convert_mcp_to_openai_tools(mcp_tools) list
    }

    class DynamicToolset {
        <<dynamic>>
        +native_tool_call(**kwargs)
    }

    UniClient --> ToolFunctionGenerator : load_tools()
    ToolFunctionGenerator --> DynamicToolset : generates
    UniLLM --> UniClient : gets tools & executes
```

## System Workflow Diagram

The sequence of connecting to a server, exploring tools, and utilizing them natively in Python or via an LLM.

```mermaid
sequenceDiagram
    participant User
    participant UniClient
    participant ToolFunctionGenerator
    participant UniLLM
    participant MCPServer
    participant OpenAI

    User->>UniClient: connect(endpoint)
    UniClient->>MCPServer: Initialize Session (Stdio or SSE)
    MCPServer-->>UniClient: Session Ready
    
    rect rgb(240, 240, 240)
        Note right of User: Mode 1: Direct Execution
        User->>UniClient: explore()
        UniClient->>MCPServer: list_tools, list_prompts, list_resources
        MCPServer-->>UniClient: Tool data
        
        User->>UniClient: load_tools()
        UniClient->>ToolFunctionGenerator: generate(tools_list)
        ToolFunctionGenerator-->>User: DynamicToolset (callable Python functions)
        User->>DynamicToolset: call tool (e.g. `get_weather(city="London")`)
        DynamicToolset->>UniClient: call_tool()
        UniClient->>MCPServer: execute tool
        MCPServer-->>DynamicToolset: execution result
        DynamicToolset-->>User: text result
    end

    rect rgb(230, 240, 255)
        Note right of User: Mode 2: LLM Execution
        User->>UniLLM: chat("What's the weather?")
        UniLLM->>UniClient: get_tools()
        UniClient->>MCPServer: list_tools()
        MCPServer-->>UniLLM: Tools payload
        UniLLM->>OpenAI: Send messages + Tools
        OpenAI-->>UniLLM: Tool Call Request
        UniLLM->>UniClient: call_tool()
        UniClient->>MCPServer: execute tool
        MCPServer-->>UniLLM: tool execution result
        UniLLM->>OpenAI: Send result back
        OpenAI-->>UniLLM: Final Answer
        UniLLM-->>User: Final Answer
    end
```

## Current Component Details

### `unimcp.client.UniClient`
The primary connection interface to an MCP server.
- Supports both **Stdio Transport** (for local scripts/executables) and **SSE Transport** (for remote HTTP/HTTPS connections).
- Seamless connection and disconnection management via `AsyncExitStack`.
- Implements comprehensive tool exploration via `.explore()`, `.get_tool_details()`, and `.get_tools()`.
- Catches errors during connection and execution, mapping them to standard UniMCP exceptions.

### `unimcp.generator.ToolFunctionGenerator`
Dynamically transforms MCP protocol definitions into native Python methods.
- Accepts raw MCP tool responses and iterates over them.
- Creates asynchronous inner functions attached to a `DynamicToolset` object.
- Automatically handles argument passing from the native python function `kwargs` into the `call_tool` MCP payload.

### `unimcp.llm.UniLLM`
A bridging component connecting OpenAI-compatible APIs directly with the `UniClient`.
- Maps MCP tool schemas into OpenAI-compatible tool schemas on-the-fly.
- Handles the automated cycle of prompting the LLM, triggering required tool functions via the `UniClient`, and passing the context back to the LLM.
- Retains ongoing conversation history within the `messages` list.

### `unimcp.exceptions`
Contains dedicated custom exception classes to facilitate clean error handling:
- `ConnectionError`: Emitted when connection/initialization to an MCP server fails.
- `NotConnectedError`: Emitted when operations are performed before establishing a connection.
- `ToolNotFoundError`: Emitted when asking for details of an unknown tool.
- `ToolExecutionError`: Emitted when a tool executes and returns an internal server-side error, or crashes during execution.
