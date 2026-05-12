import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

async def main():
    # We use the OpenAI client but point it to the NVIDIA base URL.
    # This demonstrates that the NVIDIA API is OpenAI-compatible.
    api_key = os.getenv("GEMINI_API_KEY")  # Ensure
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    model_name = "gemini-2.5-flash"

    if not api_key:
        print("Error: GEMINI_API key not found in .env file.")
        return

    print(f"Initializing OpenAI client with NVIDIA endpoint...")
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )

    try:
        print(f"Sending chat request to model: {model_name}...\n")

        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Can you explain what an MCP server is in one sentence?"}
            ]
        )

        # Print the response content
        print(f"Assistant: {response.choices[0].message.content}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
