# Matter Control Protocol (MCP) Server for python-matter-server

This project provides server implementations for the [Model Context Protocol (MCP)](https://mcp.aiprompt.dev/), enabling Large Language Models (LLMs) and other applications to interact with Matter devices. It acts as a bridge, wrapping the WebSocket API of the [python-matter-server](https://github.com/home-assistant-libs/python-matter-server) and exposing Matter device interactions as MCP tools.

This allows MCP clients (like Claude Desktop, Cursor, or custom applications) to discover and control Matter devices connected through a running `python-matter-server` instance.

**Key Features:**

*   Provides multiple MCP transport options (Stdio, SSE).
*   Offers a dedicated SSE stream for real-time Matter events.
*   Uses a persistent WebSocket connection to the `python-matter-server` for efficiency.

## Prerequisites

*   **Python:** Version 3.11 or higher recommended.
*   **uv:** A fast Python package installer and resolver. ([Installation Instructions](https://astral.sh/uv#installation)).
*   **Running `python-matter-server`:** A separate instance of the `python-matter-server` must be running and accessible (defaults to `ws://127.0.0.1:5580`). This server manages the actual communication with your Matter devices.
*   **Matter Device(s):** Commissioned Matter devices accessible by your `python-matter-server` instance. Using a [Matter Virtual Device (MVD)](https://developers.home.google.com/matter/tools/virtual-device) is recommended for testing.
*   **MCP Client Application:** An application capable of interacting with MCP servers (e.g., [Claude Desktop](https://www.anthropic.com/claude-in-your-pocket), [Cursor](https://cursor.sh/), custom scripts).
*   **(Optional) `mcp-proxy`:** Needed if you want to connect a `stdio`-only MCP client (like Claude Desktop) to the SSE-based MCP server provided here. ([mcp-proxy on GitHub](https://github.com/sparfenyuk/mcp-proxy)).

## Installation

1.  **Install uv:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Source the environment profile if needed (e.g., source ~/.profile)
    ```

2.  **Clone this repository (if you haven't already):**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

3.  **Set up a virtual environment (Recommended):**
    ```bash
    # Activate your preferred virtual environment tool
    # Example using Python's built-in venv:
    python -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    ```

4.  **Install required packages using uv:**
    ```bash
    uv pip install "mcp[cli]" aiohttp fastapi uvicorn anyio
    ```

## Server Types Provided

This repository includes three distinct server implementations catering to different needs:

1.  **`matter_mcp_stdio_server.py` (Stdio MCP Server)**
    *   **Purpose:** Provides MCP tool access via standard input/output (stdio). Ideal for direct integration with clients like Claude Desktop that primarily use command-line tools.
    *   **Transport:** Stdio
    *   **How to Run:**
        ```bash
        uv run python matter_mcp_stdio_server.py
        ```

2.  **`matter_mcp_sse_server.py` (SSE MCP Server)**
    *   **Purpose:** Provides MCP tool access via Server-Sent Events (SSE) over HTTP. Suitable for programmatic clients or web interfaces that prefer HTTP-based communication. Requires a proxy like `mcp-proxy` if used with stdio-only clients.
    *   **Transport:** SSE (HTTP)
    *   **How to Run:**
        ```bash
        uv run python matter_mcp_sse_server.py
        ```
    *   **Note:** Runs an HTTP server, typically on `http://localhost:8000` (configurable via MCP/FastAPI mechanisms if needed, though not explicitly set in the code).

3.  **`matter_event_sse_streamer.py` (SSE Event Streamer)**
    *   **Purpose:** Provides a continuous stream of *all* events (device updates, connection status, etc.) received from the backend `python-matter-server` WebSocket. This server *does not* accept MCP commands via its endpoint; it's purely for monitoring.
    *   **Transport:** SSE (HTTP)
    *   **Endpoint:** `/updates`
    *   **How to Run:**
        ```bash
        uv run python matter_event_sse_streamer.py
        ```
    *   **How to Use (Example):**
        ```bash
        # Connect and view the real-time event stream
        curl -N -H "Accept: text/event-stream" http://localhost:8001/updates
        ```
    *   **Note:** Runs an HTTP server on port `8001` by default.

## Architecture Overview

These servers act as intermediaries:

*   **MCP Client** <-> **MCP Server (this project)** <-> **`python-matter-server`** <-> **Matter Device**

They establish a persistent WebSocket connection to the `python-matter-server` using `aiohttp`. Incoming MCP requests (via Stdio or SSE) are translated into WebSocket commands, sent to `python-matter-server`, and the responses are relayed back to the MCP client. The Event Streamer pushes *all* messages received over the WebSocket to connected SSE clients.

*(Note: Currently, there is no authentication layer between the MCP Client and these MCP servers. Access control relies on network accessibility and the security of the underlying `python-matter-server`.)*

## Client Configuration Examples

### Example: Claude for Desktop

Claude Desktop primarily uses `stdio` transport for MCP servers.

**Option 1: Connecting Directly to the Stdio Server (Recommended for Claude)**

1.  Open the Claude Desktop configuration file (`claude_desktop_config.json`).
    *   Find it via Settings > Developer > Edit Config.
    *   Location varies by OS (e.g., `~/.config/Claude` on Linux, `~/Library/Application Support/Claude` on macOS, `%APPDATA%\Claude` on Windows).
2.  Add the following entry to the `mcpServers` section, replacing `[REPLACE_WITH_FULL_PATH_TO_YOUR_REPO]` with the absolute path to the directory containing these server files:

    ```json
    {
      "mcpServers": {
        "matter-mcp-server-stdio": {
          "command": "uv",
          "args": [
            "run",
            "--directory",
            "[REPLACE_WITH_FULL_PATH_TO_YOUR_REPO]",
            "matter_mcp_stdio_server.py"
          ]
        }
      }
    }
    ```

3.  Restart Claude Desktop. The "matter-mcp-server-stdio" should appear as a connectable MCP server.

**Option 2: Connecting to the SSE Server via `mcp-proxy`**

This is necessary *only* if you specifically need to use the SSE server with Claude (or another stdio-only client).

1.  Install `mcp-proxy`:
    ```bash
    uv pip install git+https://github.com/sparfenyuk/mcp-proxy
    ```
2.  Ensure `matter_mcp_sse_server.py` is running.
3.  Add the following to `claude_desktop_config.json` (adjust the `SSE_URL` if your SSE server runs on a different host/port):

    ```json
    {
      "mcpServers": {
        "matter-mcp-server-sse-proxied": {
          "command": "mcp-proxy",
          "env": {
            "SSE_URL": "http://127.0.0.1:8000/sse" // Default SSE endpoint for FastMCP
            // No API_ACCESS_TOKEN needed for this server currently
          }
        }
      }
    }
    ```
4.  Restart Claude Desktop.

## Testing

This project includes `pytest` tests.

1.  **Prerequisites for Testing:**
    *   A running `python-matter-server` instance.
    *   A commissioned Matter device (MVD recommended) accessible by `python-matter-server`. Note the `node_id` and a relevant `endpoint_id` (e.g., for an OnOff cluster).
    *   The specific MCP server being tested must be running in a separate terminal.

2.  **Running Tests:**
    *   Identify the Node ID and Endpoint ID of your test device.
    *   Run pytest, providing the IDs as arguments:

    ```bash
    # Example: Test against node 1, endpoint 1
    # Ensure the relevant MCP server (e.g., matter_mcp_stdio_server.py for test_onoff_cluster) is running!
    python -m pytest --node-id=1 --endpoint-id=1

    # To run only SSE tests (ensure matter_mcp_sse_server.py is running)
    python -m pytest test_commission_sse.py
    ```

## Supported MCP Functionality

*   **Tools:** ✅ Exposes `python-matter-server` commands as MCP tools, including:
    *   `get_nodes`
    *   `get_node`
    *   `commission_on_network`
    *   `commission_with_code` (Stdio only currently)
    *   `set_wifi_credentials` (Stdio only currently)
    *   `set_thread_dataset` (Stdio only currently)
    *   `start_listening` (Used internally by Event Streamer)
    *   `read_attribute`
    *   `write_attribute`
    *   `device_command`
*   **Prompts:** ✅ Basic tool descriptions are provided to the MCP client.
*   **Resources:** ❌ Not Implemented
*   **Sampling:** ❌ Not Implemented
*   **Notifications:** ❌ Not Implemented (Though the Event Streamer provides raw event data)

## Known Limitations

*   **No Authentication:** Communication between MCP clients and these servers is currently unauthenticated. Security relies on network isolation.
*   **Dependency:** Requires a separate, running `python-matter-server` instance.
*   **Limited MCP Features:** Only implements MCP Tools and basic Prompts.

## Troubleshooting

*   **Connection Errors (Logs):** If servers fail to start or tools fail, check the server logs. Errors often indicate the backend `python-matter-server` is not running or accessible at `ws://127.0.0.1:5580`. Verify its status and network accessibility.
*   **Claude: "Failed to start MCP server":** Usually means the `command` or `args` (especially the `--directory` path) in `claude_desktop_config.json` are incorrect, or `uv` is not in the system's PATH for Claude. Try running the `uv run ...` command manually in a terminal first.
*   **Claude: "MCP server ... disconnected":** If using `mcp-proxy`, this means the proxy started but couldn't connect to the target SSE server (`matter_mcp_sse_server.py` or `matter_event_sse_streamer.py`). Check if the target server is running and the `SSE_URL` in the proxy config is correct. Check for firewall issues.
*   **Tool Errors:** Ensure `node_id`, `endpoint_id`, `attribute_path`, `cluster_id`, `command_name`, etc., are correct for your specific Matter device according to `python-matter-server`.

## Related Projects

*   **[python-matter-server](https://github.com/home-assistant-libs/python-matter-server):** The core backend server that manages Matter communication.
*   **[Home Assistant Matter Integration](https://www.home-assistant.io/integrations/matter/):** An example of integrating Matter control into a larger system.
*   **[Model Context Protocol (MCP)](https://mcp.aiprompt.dev/):** The specification defining the interaction protocol.
*   **[mcp-proxy](https://github.com/sparfenyuk/mcp-proxy):** Useful for bridging stdio clients to SSE servers.
