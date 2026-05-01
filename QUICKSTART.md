"""
Quick Start Guide: Testing UniMCP with Example Chat

This guide shows how to test the UniMCP library locally.
"""

# ============================================================================
# STEP 1: Install the library in development mode
# ============================================================================

# From the project root directory:
# pip install -e .


# ============================================================================
# STEP 2: Install dependencies for the reference MCP server
# ============================================================================

# The reference server uses FastMCP with SSE transport, which requires:
# pip install uvicorn starlette


# ============================================================================
# STEP 3: Set your OpenAI API key
# ============================================================================

# Option A (Linux/Mac):
# export OPENAI_API_KEY=sk-your-key-here

# Option B (Windows PowerShell):
# $env:OPENAI_API_KEY = "sk-your-key-here"

# Option C (Windows Command Prompt):
# set OPENAI_API_KEY=sk-your-key-here


# ============================================================================
# STEP 4: Start the MCP server (in a separate terminal)
# ============================================================================

# From the project root:
# python reference/server.py

# You should see:
# Starting Remote MCP Server on http://localhost:8000/sse


# ============================================================================
# STEP 5: Run the example chat script (in another terminal)
# ============================================================================

# From the project root:
# python example_chat.py

# You should see the example conversations with the LLM executing tools


# ============================================================================
# FULL SETUP EXAMPLE (Windows PowerShell)
# ============================================================================

"""
# Terminal 1: Install and start server
pip install -e .
pip install uvicorn starlette
$env:OPENAI_API_KEY = "sk-your-key-here"
python reference/server.py

# Terminal 2: Run example
python example_chat.py
"""

# ============================================================================
# FULL SETUP EXAMPLE (Linux/Mac)
# ============================================================================

"""
# Terminal 1: Install and start server
pip install -e .
pip install uvicorn starlette
export OPENAI_API_KEY=sk-your-key-here
python reference/server.py

# Terminal 2: Run example
python example_chat.py
"""
