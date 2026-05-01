"""
Test interactive chat using start_interactive_chat helper.

Run: python tests/test_interactive_chat.py
"""

import asyncio
from dotenv import load_dotenv
from unimcp import UniClient, UniLLM, start_interactive_chat

load_dotenv()


async def test_interactive():
    """
    Test interactive chat with streaming support.
    
    Commands to try:
    - Type your queries and see streaming responses
    - Type 'exit', 'quit', 'bye', or 'q' to exit
    """
    print("\n" + "="*60)
    print("TEST: Interactive Chat (Pythonic API)")
    print("="*60)
    
    try:
        async with UniClient("http://localhost:8000/sse") as client:
            llm = UniLLM(client)
            
            print("\nStarting interactive chat session...")
            print("(Streaming enabled - responses appear in real-time)\n")
            
            await start_interactive_chat(
                llm,
                system_prompt="You are a helpful assistant with access to tools."
            )
            
            print("\n✅ Interactive chat test completed!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_interactive())
