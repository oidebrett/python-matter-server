"""Matter Control Protocol (MCP) server implementation for WebSocket-based device control."""

import asyncio
import json
import time
from typing import Any, Optional

import aiohttp
from aiohttp import WSMsgType
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("matter-mcp-server")


async def send_websocket_command(
    message: dict[str, Any],
    host: str = "ws://127.0.0.1",
    port: int = 5580,
    receive_timeout: float = 2.0,
) -> list[dict[str, Any]]:
    """Send command via WebSocket and receive response using aiohttp.

    Ignores the initial status message and returns only the command response messages.
    """
    url = f"{host}:{port}/ws"
    responses = []

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            # Ignore the initial status message
            await ws.receive()

            # Send the actual command
            await ws.send_json(message)
            end_time = time.time() + receive_timeout

            try:
                while time.time() < end_time:
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                        if msg.type == WSMsgType.TEXT:
                            responses.append(json.loads(msg.data))
                        elif msg.type in (
                            WSMsgType.CLOSED,
                            WSMsgType.CLOSE,
                            WSMsgType.ERROR,
                        ):
                            break
                    except asyncio.TimeoutError:
                        continue

            except aiohttp.ClientError as err:
                print(f"Error in websocket communication: {err}")

    return responses


@mcp.tool()
async def get_nodes() -> list[dict[str, Any]]:
    """Get all commissioned nodes, returning only the descriptor and basic information cluster attributes.

    Returns the original response structure but filters the attributes to only include:
    - Descriptor Cluster attributes (0/29/*)
    - Basic Information Cluster attributes (0/40/*)
    """
    message = {"message_id": "1", "command": "get_nodes"}
    return await send_websocket_command(message)


@mcp.tool()
async def get_node(
    node_id: int, remove_patterns: Optional[list[str]] = None
) -> list[dict[str, Any]]:
    """Get essential information about a specific node.

    Args:
        node_id: The node ID to query
        remove_patterns: Optional list of attribute patterns to remove. Defaults to ["0/62/"].
            Do not include in mcp tool call if you want to use the default.

    Returns:
        Original response structure with specified attribute patterns removed
    """
    message = {"message_id": "2", "command": "get_node", "args": {"node_id": node_id}}
    full_response = await send_websocket_command(message)

    # Use default pattern if none provided
    if remove_patterns is None:
        remove_patterns = ["0/62/"]

    return full_response


@mcp.tool()
async def start_listening() -> list[dict[str, Any]]:
    """Start listening for node events and changes."""
    message = {"message_id": "3", "command": "start_listening"}
    return await send_websocket_command(message)


@mcp.tool()
async def set_wifi_credentials(ssid: str, credentials: str) -> list[dict[str, Any]]:
    """Set WiFi credentials for device commissioning."""
    message = {
        "message_id": "1",
        "command": "set_wifi_credentials",
        "args": {"ssid": ssid, "credentials": credentials},
    }
    return await send_websocket_command(message)


@mcp.tool()
async def set_thread_dataset(dataset: str) -> list[dict[str, Any]]:
    """Set Thread credentials for device commissioning."""
    message = {
        "message_id": "1",
        "command": "set_thread_dataset",
        "args": {"dataset": dataset},
    }
    return await send_websocket_command(message)


@mcp.tool()
async def commission_with_code(
    code: str, network_only: Optional[bool] = False
) -> list[dict[str, Any]]:
    """Commission a new device using QR code or manual pairing code."""
    message = {
        "message_id": "1",
        "command": "commission_with_code",
        "args": {"code": code},
    }
    if network_only:
        message["args"]["network_only"] = True
    return await send_websocket_command(message)


@mcp.tool()
async def read_attribute(node_id: int, attribute_path: str) -> list[dict[str, Any]]:
    """Read an attribute from a node."""
    message = {
        "message_id": "read",
        "command": "read_attribute",
        "args": {"node_id": node_id, "attribute_path": attribute_path},
    }
    return await send_websocket_command(message)


@mcp.tool()
async def write_attribute(
    node_id: int, attribute_path: str, value: Any
) -> list[dict[str, Any]]:
    """Write an attribute value to a node."""
    # If the value is already a string, don't wrap it in extra quotes
    actual_value = value.strip('"') if isinstance(value, str) else value

    message = {
        "message_id": "write",
        "command": "write_attribute",
        "args": {
            "node_id": node_id,
            "attribute_path": attribute_path,
            "value": actual_value,
        },
    }
    return await send_websocket_command(message)


@mcp.tool()
async def device_command(
    endpoint_id: int,
    node_id: int,
    cluster_id: int,
    command_name: str,
    payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Send a command to a device.

    Args:
        endpoint_id: The endpoint ID of the device.
        node_id: The node ID of the device.
        cluster_id: The cluster ID of the command.
        command_name: The name of the command.
        payload: The payload of the command.
    """
    if payload is None:
        payload = {}

    message = {
        "message_id": "device_command",
        "command": "device_command",
        "args": {
            "endpoint_id": endpoint_id,
            "node_id": node_id,
            "payload": payload,
            "cluster_id": cluster_id,
            "command_name": command_name,
            "timed_request_timeout_ms": 100,
            "interaction_timeout_ms": 100,
        },
    }
    return await send_websocket_command(message)


if __name__ == "__main__":
    # asyncio.run(test_light_on(1, 13))
    #
    # Initialize and run the server
    mcp.run(transport="stdio")
