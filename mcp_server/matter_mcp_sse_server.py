"""Matter Control Protocol (MCP) server implementation with SSE transport for WebSocket-based device control."""

import asyncio
import logging
from typing import Any

import anyio
from mcp.server.fastmcp import FastMCP
from WebSocketConnection import WebSocketConnection

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize FastMCP server with CORS configuration
mcp = FastMCP(
    "matter-mcp-server-sse",
)

# Initialize FastMCP server and WebSocket connection
ws_connection = WebSocketConnection()

# Add debug logging to see if the tool is registered
logger.debug("Registered tools: %s", mcp.list_tools())


@mcp.tool()
async def commission_on_network(setup_pin_code: int = 20202021) -> dict[str, Any]:
    """Commission a device that's already on the network.

    Args:
        setup_pin_code: The setup PIN code for commissioning. Default value is 20202021.
    """
    await ws_connection.ready.wait()  # Wait for connection to be ready

    message = {
        "message_id": "1",
        "command": "commission_on_network",
        "args": {"setup_pin_code": setup_pin_code},
    }

    await ws_connection.outgoing_queue.put(message)
    response = await ws_connection.incoming_queue.get()
    ws_connection.incoming_queue.task_done()
    return response


@mcp.tool()
async def get_nodes() -> dict[str, Any]:
    """Get all commissioned nodes, returning only the descriptor and basic information cluster attributes.

    Returns the original response structure but filters the attributes to only include:
    - Descriptor Cluster attributes (0/29/*)
    - Basic Information Cluster attributes (0/40/*)
    """
    await ws_connection.ready.wait()  # Wait for connection to be ready

    message = {"message_id": "get_nodes", "command": "get_nodes"}

    await ws_connection.outgoing_queue.put(message)
    response = await ws_connection.incoming_queue.get()
    ws_connection.incoming_queue.task_done()
    return response


@mcp.tool()
async def get_node(node_id: int) -> dict[str, Any]:
    """Get a specific commissioned node by ID.

    Args:
        node_id: The ID of the node to retrieve

    Returns:
        The node information including descriptor and basic information cluster attributes
    """
    await ws_connection.ready.wait()  # Wait for connection to be ready

    message = {
        "message_id": "get_node",
        "command": "get_node",
        "args": {"node_id": node_id},
    }

    await ws_connection.outgoing_queue.put(message)
    response = await ws_connection.incoming_queue.get()
    ws_connection.incoming_queue.task_done()
    return response


@mcp.tool()
async def read_attribute(node_id: int, attribute_path: str) -> dict[str, Any]:
    """Read an attribute from a node.

    Args:
        node_id: The ID of the node
        attribute_path: The attribute path in format 'endpoint/cluster/attribute'

    Returns:
        The attribute value in the response
    """
    await ws_connection.ready.wait()  # Wait for connection to be ready

    message = {
        "message_id": "read",
        "command": "read_attribute",
        "args": {"node_id": node_id, "attribute_path": attribute_path},
    }

    await ws_connection.outgoing_queue.put(message)
    response = await ws_connection.incoming_queue.get()
    ws_connection.incoming_queue.task_done()
    return response


async def initialize_server():
    """Initialize the WebSocket connection and start message handling."""
    await ws_connection.connect()
    return [
        asyncio.create_task(ws_connection.listen()),
        asyncio.create_task(ws_connection.send_messages()),
    ]


async def start_server():
    """Start the server."""
    tasks = await initialize_server()
    try:
        # Run the MCP server directly without asyncio.run
        await mcp.run_sse_async()
    finally:
        for task in tasks:
            task.cancel()
        await ws_connection.disconnect()


if __name__ == "__main__":
    # Use anyio.run instead of asyncio.run
    anyio.run(start_server)
