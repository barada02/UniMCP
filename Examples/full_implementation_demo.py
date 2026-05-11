

import asyncio
import os
from unimcp import UniClient, UniLLM, Session
import dotenv

dotenv.load_dotenv()

async def main():
    # --- STEP 1: Initialize the MCP Client ---
    # We point to the server.py file in the reference directory.
    # UniClient will automatically infer the 'python' command to run it.
    server_path = "../reference/server.py"
    client = UniClient()

    try:
        print(f"Connecting to MCP server at {server_path}...")
        await client.connect()
        print("Connected successfully!\n")

        # --- STEP 2: Explore the Server ---
        # Let's see what tools, prompts, and resources the server provides.
        exploration = await client.explore()
        print(f"Available Tools: {exploration['tools']}")
        print(f"Available Prompts: {exploration['prompts']}")
        print(f"Available Resources: {exploration['resources']}")
        print("-" * 40)

        # --- STEP 3: Native Tool Execution (No LLM) ---
        # You can call tools directly using a dictionary for arguments.
        print("\nCalling 'get_system_status' directly...")
        status = await client.call_tool("get_system_status", {})
        print(f"Server Response: {status}")

        print("\nSaving a user detail directly...")
        save_res = await client.call_tool("save_user_detail", {"key": "favorite_color", "value": "Blue"})
        print(f"Server Response: {save_res}")
        print("-" * 40)

        # --- STEP 4: Dynamic Tool Loading ---
        # This is a powerful feature that turns MCP tools into native Python methods.
        print("\nLoading tools dynamically...")
        tools = await client.load_tools()

        # Now we can call 'get_all_data()' as if it were a local function
        # Note: The dynamic proxy handles the async call to the server.
        all_data = await tools.get_all_data()
        print(f"All Data (via dynamic tool): {all_data}")
        print("-" * 40)

        # --- STEP 5: Using the LLM for Intelligent Tool Orchestration ---
        # Now we integrate an LLM to let the AI decide which tools to use.
        # Ensure OPENAI_API_KEY is set in your .env or environment.
        print("\nInitializing UniLLM...")
        llm = UniLLM(mcp_client=client)
       

        # We create a Session to maintain conversation history
        session = llm.create_session(
            name="DemoSession",
            system_prompt="You are a helpful personal assistant with access to system notes."
        )

        # Example 1: A query that requires a tool call
        user_query = "What is the current system status and what is my favorite color?"
        print(f"User: {user_query}")

        # The chat method automatically handles:
        # 1. LLM Tool Call -> 2. UniClient Execution -> 3. Result back to LLM -> 4. Final Answer
        response = await llm.chat(user_query, session=session)
        print(f"Assistant: {response}\n")

        # Example 2: A request to save information
        user_query_2 = "Save a new contact named Alice with phone 123-456-7890."
        print(f"User: {user_query_2}")
        response_2 = await llm.chat(user_query_2, session=session)
        print(f"Assistant: {response_2}\n")

        # --- STEP 6: Session Persistence ---
        # Save the session to disk to resume later.
        session_file = "demo_session.json"
        await session.save(session_file)
        print(f"Session saved to {session_file}. You can load it later using UniLLM.load_session().")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Always disconnect from the server to clean up processes
        await client.disconnect()
        print("\nDisconnected from MCP server.")

if __name__ == "__main__":
    asyncio.run(main())
