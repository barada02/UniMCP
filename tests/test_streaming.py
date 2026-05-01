"""
Test streaming responses from UniLLM.

Run: python tests/test_streaming.py
"""

import asyncio
from dotenv import load_dotenv
from unimcp import UniClient, UniLLM

load_dotenv()


async def test_streaming():
    """Test streaming with stream=True parameter."""
    print("\n" + "="*60)
    print("TEST: Streaming Responses")
    print("="*60)
    
    try:
        async with UniClient("http://localhost:8000/sse") as client:
            llm = UniLLM(client)
            llm.set_system_prompt("You are a helpful assistant.")
            
            print("\nPrompt: 'Say hello and introduce yourself in 2-3 sentences'")
            print("-" * 60)
            print("Streaming response:\n")
            
            async for chunk in await llm.chat(
                "Say hello and introduce yourself in 2-3 sentences",
                stream=True
            ):
                print(chunk, end="", flush=True)
            
            print("\n" + "-" * 60)
            print("\n✅ Streaming test completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_streaming())
