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
    
    print("\nExploring server capabilities...")
    exploration = await client.explore()
    
    print("\n--- Exploration Results ---")
    print("Tools:", exploration.get("tools", []))
    print("Prompts:", exploration.get("prompts", []))
    print("Resources:", exploration.get("resources", []))
    print("---------------------------\n")
        
    print("Calling 'get_system_status'...")
    try:
        # Show tool details
        print("\n--- Tool Details: get_weather ---")
        details = await client.get_tool_details("get_weather")
        import json
        print(json.dumps(details, indent=2))
        
        # Test Dynamic load_tools functionality
        print("\n--- Testing dynamic load_tools() ---")
        tools = await client.load_tools()
        
        # Use native Python function call syntax!
        print("Calling tools.get_system_status():")
        result1 = await tools.get_system_status()
        print("Result:", result1)
        
        print("\nCalling tools.get_weather(city='Seattle'):")
        result2 = await tools.get_weather(city="Seattle")
        print("Result:", result2)
        
        print("\nCalling tools.calculate_sum(a=10, b=25):")
        result3 = await tools.calculate_sum(a=10, b=25)
        print("Result:", result3)
        
    except Exception as e:
        print("Error calling tool:", e)
        
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
