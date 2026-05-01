class UniMCPError(Exception):
    """Base exception for all UniMCP errors."""
    pass

class ConnectionError(UniMCPError):
    """Raised when the client fails to connect to the MCP server."""
    pass

class NotConnectedError(UniMCPError):
    """Raised when an operation is attempted before connecting."""
    pass

class ToolNotFoundError(UniMCPError):
    """Raised when a requested tool does not exist."""
    pass

class ToolExecutionError(UniMCPError):
    """Raised when a tool execution fails on the server."""
    pass
