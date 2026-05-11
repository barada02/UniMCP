# Known Issues

## LLM Tool-Use Format Inconsistency
**Description:** Some models (e.g., Meta Llama via NVIDIA NIM) return tool calls as raw JSON strings in the message `content` instead of using the structured `tool_calls` field of the OpenAI-compatible API.
**Current Behavior:** The library treats these tool calls as plain text, resulting in raw JSON being displayed to the user instead of the tool being executed.
**Expected Behavior:** The library should parse JSON tool calls from the content if the structured `tool_calls` field is empty.
**Priority:** Medium
**Status:** Open


### lamma response :

Initializing UniLLM...
User: What is the current system status and what is my favorite color?
Assistant: ["{\"type\": \"function\", \"name\": \"get_system_status\", \"parameters\": {}}", "{\"type\": \"function\", \"name\": \"save_user_detail\", \"parameters\": {\"key\": \"favorite color\", \"value\": \"blue\"}}"]assistant

{"type": "function", "name": "get_system_status", "parameters": {}}

User: Save a new contact named Alice with phone 123-456-7890.
Assistant: {"type": "function", "name": "save_contact", "parameters": {"phone": "123-456-7890", "name": "Alice"}}

Session saved to demo_session.json. You can load it later using UniLLM.load_session().

Disconnected from MCP server

### gemini response

Initializing UniLLM...
User: What is the current system status and what is my favorite color?
Assistant: The current system status is: System: Windows 11, Current Time: 2026-05-10 15:42:35, Status: All systems operational. Your favorite color is Blue.


User: Save a new contact named Alice with phone 123-456-7890.
Assistant: I have saved a new contact named Alice with the phone number 123-456-7890.

Session saved to demo_session.json. You can load it later using UniLLM.load_session().

Disconnected from MCP server.