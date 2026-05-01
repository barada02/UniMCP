"""
Command-line interface for UniMCP interactive chat.

Usage:
    unimcp-chat                    # Start interactive session with default settings
    unimcp-chat --model gpt-4o     # Use specific model
    unimcp-chat --help             # Show help
"""

import asyncio
import argparse
import os
from typing import Optional
from .client import UniClient
from .llm import UniLLM
from .interactive import InteractiveChat


def main():
    """CLI entry point for interactive chat."""
    parser = argparse.ArgumentParser(
        description="UniMCP Interactive Chat - Chat with your MCP tools via LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  unimcp-chat
      Start interactive session using env vars (OPENAI_API_KEY, OPENAI_MODEL)
  
  unimcp-chat --model gpt-4-turbo
      Override model from environment
  
  unimcp-chat --url http://localhost:8000/sse
      Connect to specific MCP server
  
  unimcp-chat --system-prompt "You are a code expert"
      Set custom system prompt
        """
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:8000/sse",
        help="MCP server URL (default: http://localhost:8000/sse)"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="LLM model name (overrides OPENAI_MODEL env var)"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (overrides OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="API base URL (overrides OPENAI_BASE_URL env var)"
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="Provider name (groq, together, etc.) - auto-selects base_url"
    )
    parser.add_argument(
        "--system-prompt",
        default=None,
        help="System prompt for the chat"
    )
    
    args = parser.parse_args()
    
    # Run async main
    asyncio.run(_async_main(args))


async def _async_main(args):
    """Async implementation of CLI."""
    try:
        # Connect to MCP server
        print(f"Connecting to MCP server at {args.url}...")
        async with UniClient(args.url) as client:
            # Create LLM with provided args
            llm_kwargs = {"mcp_client": client}
            
            if args.api_key:
                llm_kwargs["api_key"] = args.api_key
            if args.model:
                llm_kwargs["model_name"] = args.model
            if args.base_url:
                llm_kwargs["base_url"] = args.base_url
            if args.provider:
                llm_kwargs["provider"] = args.provider
            
            llm = UniLLM(**llm_kwargs)
            
            # Start interactive chat
            system_prompt = args.system_prompt or "You are a helpful assistant with access to tools."
            await InteractiveChat(llm, system_prompt=system_prompt).run()
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
