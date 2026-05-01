import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.unimcp.client import UniClient
from src.unimcp.llm import UniLLM

# Load environment variables from .env file
load_dotenv()

async def run_tests():
    # Read variables from environment
    # Feel free to adjust these key names if they differ in your .env
    env_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY") or "dummy_key"
    env_base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or "https://api.openai.com/v1"
    env_model = os.getenv("OPENAI_MODEL") or os.getenv("MODEL") or "gpt-4o"
    gemini_api_key = os.getenv("GEMINI_API_KEY") or env_api_key

    print("=== Loaded Environment Settings ===")
    print(f"API Key Found: {bool(env_api_key and env_api_key != 'dummy_key')}")
    print(f"Base URL: {env_base_url}")
    print(f"Model: {env_model}")
    print("===================================\n")

    # Connect to a local test server so UniLLM has a valid client
    mcp_client = UniClient(endpoint="tests/test_server.py")
    await mcp_client.connect()

    try:
        # Test 1: Normal initialization explicitly providing all three parameters
        print("--- Test 1: Normal Initialization (Explicit Parameters) ---")
        llm1 = UniLLM(
            mcp_client=mcp_client,
            api_key=env_api_key,
            base_url=env_base_url,
            model_name=env_model
        )
        print(f"-> Resulting Base URL: {llm1.client.base_url}")
        print(f"-> Resulting Model: {llm1.model_name}")
        
        # Test 2: Using the provider parameter with Gemini
        print("\n--- Test 2: Initialization with provider='gemini' ---")
        llm2 = UniLLM(
            mcp_client=mcp_client,
            api_key=gemini_api_key,
            model_name="gemini-2.5-flash",
            provider="gemini"
        )
        print(f"-> Resulting Base URL: {llm2.client.base_url}")
        print(f"-> Resulting Model: {llm2.model_name}")
        
        # Test 3: Environment variable fallback (No arguments)
        print("\n--- Test 3: Relying on Environment Variables ---")
        # Ensure env vars are set for this test
        os.environ["OPENAI_API_KEY"] = env_api_key
        os.environ["OPENAI_BASE_URL"] = env_base_url
        os.environ["OPENAI_MODEL"] = env_model
        
        llm3 = UniLLM(mcp_client=mcp_client)
        print(f"-> Resulting Base URL: {llm3.client.base_url}")
        print(f"-> Resulting Model: {llm3.model_name}")

        print("\n--- Note on Gemini OpenAI Compatibility ---")
        print("To make an actual API call to Gemini using the OpenAI Python SDK, the base URL usually must end in '/openai/'.")
        print("The SDK automatically appends 'chat/completions' making the final endpoint: '.../v1beta/openai/chat/completions'.")
        print("If you get 404 errors during a real `.chat()` call, you might need to revert 'gemini' in constants.py back to ending with '/openai/'.")

    finally:
        await mcp_client.disconnect()

if __name__ == "__main__":
    asyncio.run(run_tests())
