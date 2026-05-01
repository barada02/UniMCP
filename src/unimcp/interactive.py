"""
Interactive chat interface for UniLLM.

Provides a Pythonic API for interactive, multi-turn conversations with streaming support.
Users can also invoke this via the CLI command 'unimcp-chat'.
"""

import asyncio
from typing import Optional
from .llm import UniLLM


class InteractiveChat:
    """
    Interactive chat interface with streaming support.
    
    Usage:
        chat = InteractiveChat(llm, system_prompt="You are helpful.")
        await chat.run()  # Starts interactive loop
    """
    
    def __init__(
        self,
        llm: UniLLM,
        system_prompt: Optional[str] = None,
        exit_commands: Optional[list] = None
    ):
        """
        Initialize interactive chat.
        
        Args:
            llm: UniLLM instance to use
            system_prompt: Optional system prompt for the chat
            exit_commands: List of commands to exit (default: ["exit", "quit", "bye", "q"])
        """
        self.llm = llm
        self.system_prompt = system_prompt or "You are a helpful assistant with access to tools."
        self.exit_commands = exit_commands or ["exit", "quit", "bye", "q"]
        
        # Set the system prompt
        self.llm.set_system_prompt(self.system_prompt)
    
    async def run(self) -> None:
        """
        Run the interactive chat loop. Streams responses in real-time.
        
        User can type queries and see streamed AI responses.
        Type one of the exit commands to exit.
        """
        print("\n" + "="*60)
        print("Interactive Chat (Streaming Enabled)")
        print("="*60)
        print(f"System: {self.system_prompt}")
        print(f"Type one of {self.exit_commands} to exit.\n")
        
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit command
            if user_input.lower() in self.exit_commands:
                print("\nGoodbye!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Stream the response
            print("AI: ", end="", flush=True)
            try:
                async for chunk in await self.llm.chat(user_input, stream=True):
                    print(chunk, end="", flush=True)
                print()  # Newline after response
            except Exception as e:
                print(f"\nError: {e}")
            
            print()  # Blank line between turns


async def start_interactive_chat(
    llm: UniLLM,
    system_prompt: Optional[str] = None
) -> None:
    """
    Convenience function to start an interactive chat session.
    
    Args:
        llm: UniLLM instance to use
        system_prompt: Optional system prompt
    
    Example:
        from unimcp import UniClient, UniLLM
        from unimcp.interactive import start_interactive_chat
        
        async def main():
            async with UniClient("http://localhost:8000/sse") as client:
                llm = UniLLM(client)
                await start_interactive_chat(llm)
        
        asyncio.run(main())
    """
    chat = InteractiveChat(llm, system_prompt=system_prompt)
    await chat.run()
