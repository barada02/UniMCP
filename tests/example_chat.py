"""
Example: Chat with LLM that can execute MCP tools

This example connects to a local MCP server and uses an LLM to chat
with autonomous tool execution.

Setup:
1. Create a .env file in the project root with your OpenAI API key:
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o
   OPENAI_BASE_URL=https://api.openai.com/v1

2. Start the MCP server in reference/:
   python reference/server.py

3. Run this script:
   python tests/example_chat.py
"""

import asyncio
import os
from dotenv import load_dotenv
from unimcp import UniClient, UniLLM

# Load environment variables from .env file
load_dotenv()


async def main():
    # MCP Server endpoint (local SSE server)
    mcp_endpoint = "http://localhost:8000/sse"
    
    print("=" * 60)
    print("UniMCP Chat Example - With Tool Execution")
    print("=" * 60)
    print(f"\nConnecting to MCP server: {mcp_endpoint}")
    
    try:
        # Step 1: Connect to MCP server
        async with UniClient(mcp_endpoint) as client:
            print("✓ Connected to MCP server")
            
            # Step 2: Explore available tools
            exploration = await client.explore()
            print(f"\n📋 Available tools: {', '.join(exploration['tools'])}")
            
            # Step 3: Initialize LLM
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("\n❌ Error: OPENAI_API_KEY environment variable not set")
                print("Please set it in .env file or environment variable")
                return
            
            # Use model and base_url from .env, don't hardcode them
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
            base_url = os.getenv("OPENAI_BASE_URL")
            
            print(f"\n🔧 Configuration:")
            print(f"   - Model: {model_name}")
            if base_url:
                print(f"   - Base URL: {base_url}")
            
            llm = UniLLM(
                client
            )
            print("✓ LLM initialized")
            
            # Step 4: Set system prompt
            llm.set_system_prompt(
                "You are a helpful assistant with access to tools for managing user data and contacts. "
                "You can save contacts, retrieve data, and check system status. "
                "Be friendly and informative."
            )
            print("✓ System prompt set\n")
            
            # Step 5: Chat examples
            print("-" * 60)
            print("Starting conversation...")
            print("-" * 60)
            
            # First query: Get system status
            query1 = "What's the current system status?"
            print(f"\n👤 User: {query1}")
            try:
                response1 = await llm.chat(query1)
                print(f"🤖 AI: {response1}")
            except Exception as e:
                print(f"❌ Chat error: {type(e).__name__}")
                print(f"   Message: {str(e)}")
                return
            
            # Second query: Save a contact
            query2 = "Please save a contact for John Doe with phone 123-456-7890"
            print(f"\n👤 User: {query2}")
            try:
                response2 = await llm.chat(query2)
                print(f"🤖 AI: {response2}")
            except Exception as e:
                print(f"❌ Chat error: {type(e).__name__}")
                print(f"   Message: {str(e)}")
                return
            
            # Third query: Get all data
            query3 = "Show me all the data you have saved"
            print(f"\n👤 User: {query3}")
            try:
                response3 = await llm.chat(query3)
                print(f"🤖 AI: {response3}")
            except Exception as e:
                print(f"❌ Chat error: {type(e).__name__}")
                print(f"   Message: {str(e)}")
                return
            
            # Fourth query: Multi-step task
            query4 = "Save my details: my name is Alex and my email is alex@example.com, then show me all data"
            print(f"\n👤 User: {query4}")
            try:
                response4 = await llm.chat(query4)
                print(f"🤖 AI: {response4}")
            except Exception as e:
                print(f"❌ Chat error: {type(e).__name__}")
                print(f"   Message: {str(e)}")
                return
            
            print("\n" + "-" * 60)
            print("✓ Conversation completed successfully!")
            print("-" * 60)
            
    except Exception as e:
        print(f"\n❌ Connection Error: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
