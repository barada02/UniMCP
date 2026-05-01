import asyncio
from unimcp import UniClient, UniLLM
import os
import dotenv
dotenv.load_dotenv()

url=os.getenv("OPENAI_BASE_URL")
token=os.getenv("OPENAI_API_KEY")
model_name=os.getenv("OPENAI_MODEL")

async def main():
    async with UniClient("http://localhost:8000/sse") as client:
        # Pass in base_url, api_key, model_name OR let it read from .env!
        llm = UniLLM(client, model_name=model_name,api_key=token,base_url=url)
        
        response = await llm.chat("hi can you save my friends name dinesh and his phone number is 9009876543 and his email id is dinesh@gmail.com ")
        print("AI:", response)

asyncio.run(main())
