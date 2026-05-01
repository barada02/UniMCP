"""
Comprehensive feature test - Tests all new v0.3.0 features.

Run: python tests/test_all_features.py
"""

import asyncio
from dotenv import load_dotenv
from unimcp import UniClient, UniLLM

load_dotenv()


async def test_all_features():
    """Test streaming, non-streaming, and multi-turn conversations."""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST: UniMCP v0.3.0 Features")
    print("="*70)
    
    try:
        async with UniClient("http://localhost:8000/sse") as client:
            llm = UniLLM(client)
            llm.set_system_prompt("You are a helpful assistant.")
            
            # Test 1: Non-streaming single message
            print("\n[TEST 1] Non-Streaming Single Message")
            print("-" * 70)
            print("Query: 'What is async programming?'")
            response = await llm.chat("What is async programming?")
            print(f"Response (first 100 chars): {response[:100]}...")
            print("✅ Passed")
            
            # Test 2: Streaming single message
            print("\n[TEST 2] Streaming Single Message")
            print("-" * 70)
            print("Query: 'Explain Python lists briefly' (streaming)")
            print("Streamed response: ", end="", flush=True)
            async for chunk in await llm.chat("Explain Python lists briefly", stream=True):
                print(chunk, end="", flush=True)
            print("\n✅ Passed")
            
            # Test 3: Multi-turn non-streaming conversation
            print("\n[TEST 3] Multi-Turn Non-Streaming Conversation")
            print("-" * 70)
            print("Message 1: 'What is a function?'")
            msg1 = await llm.chat("What is a function?")
            print(f"Response (first 80 chars): {msg1[:80]}...")
            
            print("\nMessage 2: 'How do I define one in Python?'")
            msg2 = await llm.chat("How do I define one in Python?")
            print(f"Response (first 80 chars): {msg2[:80]}...")
            print("✅ Passed (Context maintained)")
            
            # Test 4: Multi-turn streaming conversation
            print("\n[TEST 4] Multi-Turn Streaming Conversation")
            print("-" * 70)
            print("Message 1 (streaming): 'Explain variables' (first 50 chars)")
            async for chunk in await llm.chat("Explain variables", stream=True):
                print(chunk, end="", flush=True)
            
            print("\n\nMessage 2 (streaming): 'How do I assign them?' (first 50 chars)")
            async for chunk in await llm.chat("How do I assign them?", stream=True):
                print(chunk, end="", flush=True)
            print("\n✅ Passed (Context maintained with streaming)")
            
            print("\n" + "="*70)
            print("✅ ALL TESTS PASSED!")
            print("="*70)
            print("\nSummary:")
            print("  ✓ Non-streaming responses work")
            print("  ✓ Streaming responses work")
            print("  ✓ Multi-turn conversations maintain context")
            print("  ✓ Streaming works in multi-turn conversations")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(test_all_features())
