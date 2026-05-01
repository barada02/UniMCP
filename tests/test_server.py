from mcp.server.fastmcp import FastMCP
mcp = FastMCP("test-server")

@mcp.tool()
def get_system_status() -> str:
    """Returns the current system status."""
    return "All good!"

@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for a specific city."""
    return f"The weather in {city} is sunny and 72°F."

@mcp.tool()
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")
