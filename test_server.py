from mcp.server.fastmcp import FastMCP
mcp = FastMCP("test-server")

@mcp.tool()
def get_system_status() -> str:
    return "All good!"

if __name__ == "__main__":
    mcp.run(transport="stdio")
