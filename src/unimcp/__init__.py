"""
UniMCP package - Connect to MCP servers and use them pythonically or with LLMs.
"""

from .client import UniClient
from .llm import UniLLM

__version__ = "0.1.0"
__all__ = ["UniClient", "UniLLM"]
