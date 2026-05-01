import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test_endpoint(name, url, api_key, model):
    print(f"\n--- Testing Endpoint: {name} ---")
    print(f"Base URL: {url}")
    
    # Initialize the OpenAI client with the given base URL
    client = AsyncOpenAI(api_key=api_key, base_url=url)
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "What is the biggest moon of Jupiter? Answer in one sentence."}],
            max_tokens=500
        )
        print(f"✅ SUCCESS!")
        print(f"Response: {response.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

async def main():
    # Use GEMINI_API_KEY, fallback to OPENAI_API_KEY
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
    model = os.getenv("OPENAI_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
    
    if not api_key:
        print("No API key found. Please ensure OPENAI_API_KEY or GEMINI_API_KEY is in your .env file.")
        return

    print(f"Using Model: {model}")

    # Endpoint 1: Without /openai/ (User's current version)
    url1 = "https://generativelanguage.googleapis.com/v1beta/"
    await test_endpoint("Without /openai/", url1, api_key, model)

    # Endpoint 2: With /openai/ (Standard OpenAI compat path for Gemini)
    url2 = "https://generativelanguage.googleapis.com/v1beta/openai/"
    await test_endpoint("With /openai/", url2, api_key, model)

if __name__ == "__main__":
    asyncio.run(main())
