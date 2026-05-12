import asyncio
import os
import subprocess
import webbrowser
from typing import Optional

import uvicorn
from unimcp.web.server import app, mount_static

def main():
    """
    Launches the UniMCP Web Dashboard.
    """
    # Initial setup: Mount static files
    mount_static()

    # Determine port (default to 8000)
    port = 8000

    # Start the FastAPI server using Uvicorn
    # We run this in a separate process or as the main loop
    print(f"Starting UniMCP Dashboard on http://localhost:{port}...")

    # Open the browser automatically
    webbrowser.open(f"http://localhost:{port}")

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
