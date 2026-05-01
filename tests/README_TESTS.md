"""
Comprehensive test suite for UniMCP v0.3.0 - Streaming & Interactive Chat

Available tests:
1. test_streaming.py            - Test streaming responses
2. test_non_streaming.py        - Test original non-streaming behavior
3. test_interactive_pythonic.py - Test interactive chat (Pythonic API)
4. test_interactive_class.py    - Test InteractiveChat class directly

Run tests:
    python tests/test_streaming.py
    python tests/test_non_streaming.py
    python tests/test_interactive_pythonic.py
    python tests/test_interactive_class.py

Or run CLI:
    unimcp-chat
    unimcp-chat --model gpt-4o
    unimcp-chat --system-prompt "You are a code expert"

Requirements:
- MCP server running at http://localhost:8000/sse
- OPENAI_API_KEY environment variable set
- Optional: OPENAI_MODEL, OPENAI_BASE_URL
"""

print(__doc__)
