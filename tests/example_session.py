"""
Example: Using Sessions with UniMCP

This example demonstrates:
1. Ephemeral in-memory sessions (default)
2. Persistent sessions (saved to disk)
3. Session management (clear, export, load)

Setup:
1. Create a .env file in the project root with your API credentials
2. Start the MCP server in reference/:
   python reference/server.py
3. Run this script:
   python tests/example_session.py
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from unimcp import UniClient, UniLLM, Session

# Load environment variables from .env file
load_dotenv()


async def example_1_ephemeral_session():
    """
    Example 1: Ephemeral in-memory session (default behavior)
    Session is auto-garbage collected when done.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Ephemeral In-Memory Session (Default)")
    print("=" * 70)
    
    mcp_endpoint = "http://localhost:8000/sse"
    
    async with UniClient(mcp_endpoint) as client:
        llm = UniLLM(client)
        
        print("\n✓ LLM initialized (default ephemeral session)")
        
        # These chats use an implicit temporary session
        print("\n👤 User: Save a contact for me: John with phone 555-1234")
        response1 = await llm.chat("Save a contact for me: Dinesh with phone 555-1234")
        print(f"🤖 AI: {response1[:100]}...")
        
        print("\n👤 User: What contacts did I save?")
        response2 = await llm.chat("What contacts did I save?")
        print(f"🤖 AI: {response2[:100]}...")
        
        print("\n✓ Session will be auto-garbage collected")


async def example_2_persistent_session():
    """
    Example 2: Persistent session (saved to disk)
    Can be loaded and continued later.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Persistent Session (Saved to Disk)")
    print("=" * 70)
    
    mcp_endpoint = "http://localhost:8000/sse"
    save_path = "sessions/example_conversation.json"
    
    async with UniClient(mcp_endpoint) as client:
        llm = UniLLM(client)
        
        # Create an explicit persistent session
        session = llm.create_session(
            name="support_conversation_001",
            system_prompt="You are a helpful support assistant."
        )
        
        print(f"\n✓ Created persistent session: {session.name}")
        
        # Chat 1
        print("\n👤 User: Get my system status")
        response1 = await llm.chat("Get my system status", session=session)
        print(f"🤖 AI: {response1[:100]}...")
        
        # Chat 2
        print("\n👤 User: Save my email as alex@example.com")
        response2 = await llm.chat("Save my email as Chandan@example.com", session=session)
        print(f"🤖 AI: {response2[:100]}...")
        
        # Chat 3
        print("\n👤 User: Show me all saved data")
        response3 = await llm.chat("Show me all saved data", session=session)
        print(f"🤖 AI: {response3[:100]}...")
        
        # Save the session
        await session.save(save_path)
        print(f"\n✓ Session saved to: {save_path}")
        print(f"  - Messages: {session.get_message_count()}")
        print(f"  - Conversation turns: {session.get_conversation_turns()}")


async def example_3_load_and_continue():
    """
    Example 3: Load a saved session and continue the conversation
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Load and Continue Previous Session")
    print("=" * 70)
    
    mcp_endpoint = "http://localhost:8000/sse"
    save_path = "sessions/example_conversation.json"
    
    # Check if session file exists from Example 2
    if not os.path.exists(save_path):
        print(f"\n⚠ Session file not found: {save_path}")
        print("  Please run Example 2 first to create a session.")
        return
    
    async with UniClient(mcp_endpoint) as client:
        llm = UniLLM(client)
        
        # Load the saved session
        session = await UniLLM.load_session(save_path)
        print(f"\n✓ Loaded session: {session.name}")
        print(f"  - Previous messages: {session.get_message_count()}")
        print(f"  - Previous turns: {session.get_conversation_turns()}")
        
        # Continue conversation
        print("\n👤 User: What data do you have about me?")
        response = await llm.chat("What data do you have about me?", session=session)
        print(f"🤖 AI: {response[:100]}...")
        
        # Save the updated session
        await session.save(save_path)
        print(f"\n✓ Session updated and saved")
        print(f"  - Total messages: {session.get_message_count()}")


async def example_4_session_management():
    """
    Example 4: Session management features
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Session Management Features")
    print("=" * 70)
    
    mcp_endpoint = "http://localhost:8000/sse"
    
    async with UniClient(mcp_endpoint) as client:
        llm = UniLLM(client)
        
        # Create session
        session = llm.create_session(
            name="demo_session",
            system_prompt="You are helpful."
        )
        
        print(f"\n✓ Created session: {session}")
        
        # Have a conversation
        await llm.chat("Save contact: Alice, phone 555-9999", session=session)
        await llm.chat("What's my system status?", session=session)
        
        print(f"\n📊 Session Stats:")
        print(f"  - Name: {session.name}")
        print(f"  - Total messages: {session.get_message_count()}")
        print(f"  - Conversation turns: {session.get_conversation_turns()}")
        print(f"  - Created at: {session.created_at}")
        print(f"  - Updated at: {session.updated_at}")
        
        # Export transcript
        print(f"\n📝 Conversation Transcript:")
        print("-" * 70)
        transcript = session.export_transcript()
        print(transcript)
        
        # Clear history (keep system prompt)
        print(f"\n🧹 Clearing conversation history...")
        session.clear_history()
        print(f"  - Messages after clear: {session.get_message_count()}")
        
        # Continue with fresh history
        await llm.chat("New conversation: What's the system status?", session=session)
        print(f"  - Messages after new chat: {session.get_message_count()}")


async def main():
    """Run all examples"""
    try:
        # Example 1: Ephemeral session
        await example_1_ephemeral_session()
        
        # Example 2: Persistent session
        await example_2_persistent_session()
        
        # Example 3: Load and continue
        await example_3_load_and_continue()
        
        # Example 4: Session management
        await example_4_session_management()
        
        print("\n" + "=" * 70)
        print("✓ All examples completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
