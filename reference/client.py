import asyncio
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
# Base URL and API Key are automatically pulled from OPENAI_BASE_URL and OPENAI_API_KEY env variables
openai_client = AsyncOpenAI()
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o")

def convert_mcp_to_openai_tools(mcp_tools) -> list:
    """
    Helper function to convert MCP tool definitions into the format 
    that the OpenAI API expects.
    """
    openai_tools = []
    for tool in mcp_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                # MCP uses JSON Schema for inputs, which matches OpenAI closely
                "parameters": tool.inputSchema
            }
        })
    return openai_tools

async def chat_interaction_loop(session: ClientSession):
    """
    Continuous chat loop that keeps conversation history.
    """
    print("\n[Client] Initializing session history...")
    
    # Ask the MCP server what tools it has available
    tools_response = await session.list_tools()
    available_openai_tools = convert_mcp_to_openai_tools(tools_response.tools)
    print(f"[Client] Server provides {len(available_openai_tools)} tools.")
    print(f"[Client] Tools: {[tool['function']['name'] for tool in available_openai_tools]}")
    #print(f"[Client] tools: {json.dumps(available_openai_tools, indent=2)}")

    # System prompt gives the AI a personality and rules
    system_prompt = (
        "You are a helpful assistant hooked up to an external database. "
        "You MUST use your provided tools to save user preferences, personal details, and contacts. "
        f"You have [{len(available_openai_tools)}] tools available to interact with the file system. "
        "Whenever the user mentions a fact about themselves or a friend, immediately call the appropriate tool."
    )
    
    messages = [
        {
            "role": "system", 
            "content": system_prompt
        }
    ]
    
    print("\n--- Chat Started! Type 'exit' or 'quit' to stop. ---")
    
    while True:
        # Prompt user for input
        user_prompt = input("\nYou: ")
        if user_prompt.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
            
        messages.append({"role": "user", "content": user_prompt})

        # We use a loop here because sometimes the AI calls a tool, gets the result,
        # but decides it needs to call ANOTHER tool before answering the user.
        while True:
            try:
                response = await openai_client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=available_openai_tools,
                    tool_choice="auto" # Wait, some models need this explicitly set
                )
            except Exception as e:
                print(f"\n[Error] The LLM Provider returned an error: {e}")
                print("[Hint] If you hit a rate limit, try waiting a minute, or change the model in your .env file.")
                break
                
            response_message = response.choices[0].message
            # We MUST append the assistant's message to the conversation history
            # either as a text response or a tool call response
            messages.append(response_message)
        
            # If the LLM decides to call a tool (or multiple tools)
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    print(f"\n[Processing] Calling tool '{tool_name}' with args: {tool_args}")
                    
                    # Call the tool on the MCP server
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    
                    # Read the response text from the server
                    tool_result_str = ""
                    for content in result.content:
                        if content.type == "text":
                            tool_result_str += content.text
                            
                    print(f"[Processing] Server replied: {tool_result_str.strip()}")
                    
                    # Feed the result back to the LLM
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_result_str
                    })
                # After feeding all tool results, let the `while True` loop run again
                # so the LLM can generate its final response (or call another tool!)
            else:
                # No more tools requested, the LLM has given us text response
                print(f"AI: {response_message.content}")
                break # Break inner loop, go back to waiting for User input

async def main():
    print("Connecting to remote MCP server via SSE...")
    async with sse_client(url="http://localhost:8000/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected and initialized successfully!")

            # Start interactive chat
            await chat_interaction_loop(session)

if __name__ == "__main__":
    asyncio.run(main())
