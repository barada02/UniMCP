import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.unimcp.client import UniClient
from src.unimcp.exceptions import (
    ConnectionError,
    NotConnectedError,
    ToolNotFoundError,
    ToolExecutionError
)

async def test_not_connected_error():
    print("\n--- Testing NotConnectedError ---")
    client = UniClient(endpoint="tests/test_server.py")
    try:
        await client.get_tools()
        print("FAIL: Should have raised NotConnectedError")
    except NotConnectedError as e:
        print(f"PASS: Caught NotConnectedError -> {e}")

async def test_connection_error():
    print("\n--- Testing ConnectionError ---")
    client = UniClient(endpoint="tests/this_file_does_not_exist.py")
    try:
        await client.connect()
        print("FAIL: Should have raised ConnectionError")
    except ConnectionError as e:
        print(f"PASS: Caught ConnectionError -> {e}")

async def test_tool_not_found_error():
    print("\n--- Testing ToolNotFoundError ---")
    client = UniClient(endpoint="tests/test_server.py")
    await client.connect()
    try:
        await client.get_tool_details("fake_tool_name")
        print("FAIL: Should have raised ToolNotFoundError")
    except ToolNotFoundError as e:
        print(f"PASS: Caught ToolNotFoundError -> {e}")
    finally:
        await client.disconnect()

async def test_tool_execution_error():
    print("\n--- Testing ToolExecutionError ---")
    client = UniClient(endpoint="tests/test_server.py")
    await client.connect()
    try:
        tools = await client.load_tools()
        # calculate_sum expects 'a' and 'b', but we only provide 'a'
        await tools.calculate_sum(a=10)
        print("FAIL: Should have raised ToolExecutionError")
    except ToolExecutionError as e:
        print(f"PASS: Caught ToolExecutionError -> {e}")
    finally:
        await client.disconnect()

async def main():
    await test_not_connected_error()
    await test_connection_error()
    await test_tool_not_found_error()
    await test_tool_execution_error()

if __name__ == "__main__":
    asyncio.run(main())
