"""
Test InteractiveChat class directly.

Run: python tests/test_interactive_class.py
"""

import asyncio
from dotenv import load_dotenv
from unimcp import UniClient, UniLLM, InteractiveChat

load_dotenv()


async def test_interactive_class():
    """
    Test InteractiveChat class with custom exit commands and system prompt.
    
    Commands to try:
    - Type your queries and see streaming responses
    - Type 'exit' or 'done' to exit (custom commands for this test)
    """
    print("\n" + "="*60)
    print("TEST: InteractiveChat Class")
    print("="*60)
    
    try:
        async with UniClient("http://localhost:8000/sse") as client:
            llm = UniLLM(client)
            
            # Create an interactive chat with custom system prompt and exit commands
            chat = InteractiveChat(
                llm,
                system_prompt="You are a Python programming expert. Help users with code.",
                exit_commands=["exit", "done", "quit"]
            )
            
            print("\nStarting interactive chat session...")
            print("(Try asking Python-related questions)\n")
            
            await chat.run()
            
            print("\n✅ InteractiveChat class test completed!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_interactive_class())
