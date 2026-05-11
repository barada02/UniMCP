from mcp.server.fastmcp import FastMCP
import platform
import datetime
import json
import os

# Create server with a specific name
mcp = FastMCP("remote-system-notes")

DB_FILE = "user_data.json"

def _load_data() -> dict:
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def _save_data(data: dict):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@mcp.tool()
def get_system_status() -> str:
    """
    Get the current system status, including OS details and current time.
    """
    os_info = platform.system() + " " + platform.release()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"System: {os_info}\nCurrent Time: {current_time}\nStatus: All systems operational."

@mcp.tool()
def get_all_data() -> str:
    """Read and retrieve all saved user data and contacts from the database."""
    data = _load_data()
    if not data:
        return "The database is currently empty."
    return json.dumps(data, indent=2)

@mcp.tool()
def save_user_detail(key: str, value: str) -> str:
    """
    Save or update a piece of personal information about the user (e.g., 'name', 'age', 'email').
    """
    data = _load_data()
    if "user" not in data:
        data["user"] = {}
    data["user"][key] = value
    _save_data(data)
    return f"Successfully saved user detail: {key} = {value}"

@mcp.tool()
def save_contact(name: str, phone: str = "", email: str = "") -> str:
    """
    Save or update a contact/friend's details.
    Must provide the name, and optionally a phone number or email string.
    """
    data = _load_data()
    if "contacts" not in data:
        data["contacts"] = {}
    data["contacts"][name] = {"phone": phone, "email": email}
    _save_data(data)
    return f"Contact '{name}' saved successfully."

if __name__ == "__main__":
    # FastMCP supports 'sse' (Server-Sent Events) for acting as a remote HTTP server
    # Note: running this requires 'uvicorn' and 'starlette' (pip install uvicorn starlette)
    import sys
    print("Starting Remote MCP Server on http://localhost:8000/sse")
    print("Press CTRL+C to close.")
    
    try:
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\nServer stopped unexpectedly: {e}")
        sys.exit(1)
