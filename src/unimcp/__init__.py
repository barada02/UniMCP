"""
UniMCP package - Connect to MCP servers and use them pythonically or with LLMs.
"""

from dotenv import load_dotenv

# Load environment variables from .env file automatically
load_dotenv()

from .client import UniClient
from .llm import UniLLM
from .session import Session
from .interactive import InteractiveChat, start_interactive_chat

__version__ = "0.3.0"
__all__ = ["UniClient", "UniLLM", "Session", "InteractiveChat", "start_interactive_chat"]
