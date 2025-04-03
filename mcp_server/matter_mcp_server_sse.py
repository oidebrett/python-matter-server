"""Matter Control Protocol (MCP) server implementation with SSE transport for WebSocket-based device control."""

import asyncio
from collections.abc import AsyncGenerator
import json
from typing import Any, Optional

import aiohttp
from aiohttp import WSMsgType
from mcp.server.fastmcp import FastMCP


class WebSocketConnection:
    """WebSocket connection handler for Matter Control Protocol.

    Manages WebSocket connection to the Matter server, including connection establishment,
    message sending/receiving, and reconnection logic.
    """

    def __init__(self, host: str = "ws://127.0.0.1", port: int = 5580):
        """Initialize the WebSocket connection.

        Args:
            host: WebSocket host address. Defaults to "ws://127.0.0.1".
            port: WebSocket port number. Defaults to 5580.
        """
        self.url = f"{host}:{port}/ws"
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.ready = asyncio.Event()
        self.outgoing_queue: asyncio.Queue = asyncio.Queue()
        self.incoming_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self):
        """Establish WebSocket connection."""
        try:
            self.session = aiohttp.ClientSession()
            self.ws = await self.session.ws_connect(self.url)
            # Ignore initial status message
            await self.ws.receive()
            self.ready.set()
        except (aiohttp.ClientError, aiohttp.WebSocketError, ConnectionError) as err:
            print(f"Connection error: {err}")
            if self.session:
                await self.session.close()
            raise

    async def disconnect(self):
        """Close WebSocket connection."""
        self.ready.clear()
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()

    async def listen(self):
        """Listen for messages from WebSocket and put them in incoming queue."""
        while True:
            try:
                if not self.ws:
                    await asyncio.sleep(1)
                    continue

                msg = await self.ws.receive()
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.incoming_queue.put(data)
                elif msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSE, WSMsgType.ERROR):
                    self.ready.clear()
                    await self.connect()
            except (
                aiohttp.ClientError,
                aiohttp.WebSocketError,
                ConnectionError,
                json.JSONDecodeError,
            ) as err:
                print(f"WebSocket error: {err}")
                await asyncio.sleep(1)

    async def maintain_connection(self):
        """Maintain the WebSocket connection."""
        while True:
            try:
                if not self.ws or self.ws.closed:
                    self.ready.clear()
                    await self.connect()
            except (
                aiohttp.ClientError,
                aiohttp.WebSocketError,
                ConnectionError,
            ) as err:
                print(f"WebSocket error: {err}")
                await asyncio.sleep(1)

    async def send_messages(self):
        """Send messages from the outgoing queue."""
        while True:
            try:
                message = await self.outgoing_queue.get()
                if not self.ws:
                    continue
                await self.ws.send_json(message)
                self.outgoing_queue.task_done()
            except (
                aiohttp.ClientError,
                aiohttp.WebSocketError,
                ConnectionError,
            ) as err:
                print(f"Error sending message: {err}")
                await asyncio.sleep(1)


# Initialize FastMCP server and WebSocket connection
mcp = FastMCP("matter-mcp-server-sse")
ws_connection = WebSocketConnection()


@mcp.tool()
async def start_listening() -> AsyncGenerator[dict[str, Any], None]:
    """Start listening for Matter events."""
    await ws_connection.ready.wait()  # Wait for connection to be ready
    while True:
        event = await ws_connection.incoming_queue.get()
        yield event
        ws_connection.incoming_queue.task_done()


@mcp.tool()
async def commission_on_network(setup_pin_code: int = 20202021) -> dict[str, Any]:
    """Commission a device that's already on the network."""
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
        attribute_path: The attribute path in format "endpoint/cluster/attribute"

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
        await mcp.run(transport="sse")  # Changed from run_async to run
    finally:
        for task in tasks:
            task.cancel()
        await ws_connection.disconnect()


if __name__ == "__main__":
    asyncio.run(start_server())
