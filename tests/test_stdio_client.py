import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.unimcp.client import UniClient

async def main():
    # Provide the path to the local server script
    client = UniClient(endpoint="tests/test_server.py")
    
    print("Connecting to local stdio server...")
    await client.connect()
    print("Connected successfully!")
    
    print("\nAvailable tools:")
    tools = await client.get_tools()
    for tool in tools:
        print(f" - {tool.name}: {tool.description}")
        
    print("\nCalling 'get_system_status'...")
    try:
        result = await client.call_tool("get_system_status", {})
        print("Result:", result)
    except Exception as e:
        print("Error calling tool:", e)
        
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
