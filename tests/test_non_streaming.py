"""
Test non-streaming (original) chat behavior.

Run: python tests/test_non_streaming.py
"""

import asyncio
from dotenv import load_dotenv
from unimcp import UniClient, UniLLM

load_dotenv()


async def test_non_streaming():
    """Test that original non-streaming behavior still works (stream=False by default)."""
    print("\n" + "="*60)
    print("TEST: Non-Streaming Chat (Original Behavior)")
    print("="*60)
    
    try:
        async with UniClient("http://localhost:8000/sse") as client:
            llm = UniLLM(client)
            llm.set_system_prompt("You are a helpful assistant.")
            
            print("\nPrompt 1: 'What is 2+2?'")
            print("-" * 60)
            response1 = await llm.chat("What is 2+2?")  # stream=False by default
            print(f"Response: {response1}")
            
            print("\n" + "-" * 60)
            print("\nPrompt 2: 'Tell me about Python'")
            print("-" * 60)
            response2 = await llm.chat("Tell me about Python")
            print(f"Response: {response2}")
            
            print("\n" + "-" * 60)
            print("\n✅ Non-streaming test completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_non_streaming())
