import asyncio
import os
import subprocess
import sys
from typing import Any, Dict, Optional

import streamlit as st
from unimcp.client import UniClient
from unimcp.exceptions import ConnectionError, NotConnectedError

# --- Async Bridge ---
class AsyncRunner:
    """
    Bridges Streamlit's synchronous execution model with UniClient's async API.
    Manages a persistent event loop and UniClient instance in st.session_state.
    """
    @staticmethod
    def get_loop():
        if "event_loop" not in st.session_state:
            st.session_state.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(st.session_state.event_loop)
        return st.session_state.event_loop

    @staticmethod
    def run_async(coro):
        loop = AsyncRunner.get_loop()
        return loop.run_until_complete(coro)

# --- UI Helpers ---
def generate_dynamic_form(tool_details: Dict[str, Any]):
    """
    Maps JSON Schema properties to Streamlit widgets.
    """
    schema = tool_details.get("inputSchema", {})
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    args = {}
    st.markdown("#### Tool Arguments")

    if not properties:
        st.info("This tool requires no arguments.")
        return args

    for prop_name, prop_details in properties.items():
        prop_type = prop_details.get("type", "string")
        label = f"{prop_name} ({'Required' if prop_name in required else 'Optional'})"

        if "enum" in prop_details:
            args[prop_name] = st.selectbox(label, options=prop_details["enum"])
        elif prop_type == "string":
            args[prop_name] = st.text_input(label, value="")
        elif prop_type == "number" or prop_type == "integer":
            args[prop_name] = st.number_input(label, value=0.0 if prop_type == "number" else 0)
        elif prop_type == "boolean":
            args[prop_name] = st.checkbox(label, value=False)
        else:
            args[prop_name] = st.text_area(f"{label} (JSON/Text)", value="")

    return args

# --- Main App Logic ---
def main_app():
    st.set_page_config(page_title="UniMCP Dashboard", page_icon="🔌", layout="wide")
    st.title("🔌 UniMCP Dashboard")
    st.markdown("Explore and test your MCP servers visually.")

    # --- Sidebar: Connection ---
    with st.sidebar:
        st.header("Connection")
        default_endpoint = os.getenv("MCP_SERVER", "http://localhost:8000/sse")
        endpoint = st.text_input("MCP Server Endpoint", value=default_endpoint)

        if "client" not in st.session_state:
            st.session_state.client = None
            st.session_state.connected = False

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect", disabled=st.session_state.connected):
                try:
                    client = UniClient(endpoint)
                    # Use the async runner to connect
                    AsyncRunner.run_async(client.connect())
                    st.session_state.client = client
                    st.session_state.connected = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Connection failed: {e}")

        with col2:
            if st.button("Disconnect", disabled=not st.session_state.connected):
                if st.session_state.client:
                    AsyncRunner.run_async(st.session_state.client.disconnect())
                st.session_state.client = None
                st.session_state.connected = False
                st.rerun()

        st.divider()
        if st.session_state.connected:
            st.success("Connected to server")
        else:
            st.warning("Not connected")

    # --- Main Content ---
    if not st.session_state.connected:
        st.info("Please connect to an MCP server in the sidebar to start exploring.")
        st.stop()

    client = st.session_state.client

    tab1, tab2 = st.tabs(["🔍 Explorer", "🛠️ Tool Tester"])

    with tab1:
        st.header("Server Exploration")
        try:
            data = AsyncRunner.run_async(client.explore())

            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader("Tools")
                if data["tools"]:
                    for tool in data["tools"]:
                        st.markdown(f"- `{tool}`")
                else:
                    st.write("No tools available.")

            with col2:
                st.subheader("Prompts")
                if data["prompts"]:
                    for prompt in data["prompts"]:
                        st.markdown(f"- `{prompt}`")
                else:
                    st.write("No prompts available.")

            with col3:
                st.subheader("Resources")
                if data["resources"]:
                    for res in data["resources"]:
                        st.markdown(f"- `{res}`")
                else:
                    st.write("No resources available.")
        except Exception as e:
            st.error(f"Error exploring server: {e}")

    with tab2:
        st.header("Test a Tool")
        try:
            # Get list of tools for the dropdown
            data = AsyncRunner.run_async(client.explore())
            tools = data["tools"]

            if not tools:
                st.warning("No tools found on this server.")
            else:
                selected_tool = st.selectbox("Select a tool to test", options=tools)

                if selected_tool:
                    details = AsyncRunner.run_async(client.get_tool_details(selected_tool))
                    st.markdown(f"**Description:** {details['description']}")

                    # Generate inputs
                    args = generate_dynamic_form(details)

                    if st.button("Execute Tool", type="primary"):
                        with st.spinner("Executing..."):
                            # Filter out empty string inputs for optional params
                            cleaned_args = {k: v for k, v in args.items() if v != ""}
                            result = AsyncRunner.run_async(client.call_tool(selected_tool, cleaned_args))
                            st.markdown("#### Result")
                            st.code(result, language="text")
        except Exception as e:
            st.error(f"Error testing tool: {e}")

def main():
    """
    Entry point for the CLI.
    Launches the Streamlit server.
    """
    # We need to get the absolute path to this file to ensure streamlit finds it
    script_path = os.path.abspath(__file__)
    subprocess.run(["streamlit", "run", script_path])

if __name__ == "__main__":
    main_app() # This is called by 'streamlit run'
    # main() # The CLI entry point
