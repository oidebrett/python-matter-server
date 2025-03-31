"""Matter Control Protocol (MCP) server implementation.

This module provides a server that wraps the Matter Server WebSocket API,
supporting both STDIO and SSE transport modes for Matter device control.
"""

import argparse
import asyncio
from collections.abc import Sequence
import os
from typing import Any, Optional

import aiohttp

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as err:
    raise ImportError(
        "MCP package not found. Please install it with: pip install mcp[cli]"
    ) from err

from matter_server.client.client import MatterClient
from matter_server.client.models.node import MatterFabricData
from matter_server.common.models import (
    CommissionableNodeData,
    CommissioningParameters,
    MatterNodeData,
    MatterSoftwareVersion,
    NodePingResult,
)


class ClientManager:
    """Manages the Matter client instance."""

    def __init__(self) -> None:
        """Initialize the client manager."""
        self._client: Optional[MatterClient] = None

    async def get_client(self) -> MatterClient:
        """Get or create a Matter client instance.

        Returns:
            MatterClient: Connected Matter client instance.
        """
        if not self._client:
            session = aiohttp.ClientSession()
            matter_server_url = os.environ.get(
                "MATTER_SERVER_URL", "ws://localhost:5580/ws"
            )
            client = MatterClient(matter_server_url, session)
            await client.connect()
            self._client = client
        return self._client


# Initialize FastMCP server and client manager
mcp = FastMCP("Matter MCP Server")
client_manager = ClientManager()


@mcp.tool()
async def commission_with_code(code: str, network_only: bool) -> dict[str, Any]:
    """Commission a device using a QR Code or Manual Pairing Code."""
    client = await client_manager.get_client()
    return await client.commission_with_code(code, network_only)


@mcp.tool()
async def set_wifi_credentials(ssid: str, credentials: str) -> None:
    """Set WiFi credentials for commissioning to a new device."""
    client = await client_manager.get_client()
    await client.set_wifi_credentials(ssid, credentials)


@mcp.tool()
async def set_thread_dataset(dataset: str) -> None:
    """Set Thread Operational dataset in the stack."""
    client = await client_manager.get_client()
    await client.set_thread_dataset(dataset)


@mcp.tool()
async def open_commissioning_window(
    node_id: int,
    *,  # Force keyword arguments
    window_timeout: Optional[int] = None,
    iteration: Optional[int] = None,
    option: Optional[int] = None,
    discriminator: Optional[int] = None,
) -> CommissioningParameters:
    """Open a commissioning window on a node."""
    client = await client_manager.get_client()
    async with asyncio.timeout(window_timeout if window_timeout else 300):
        return await client.open_commissioning_window(
            node_id, window_timeout, iteration, option, discriminator
        )


@mcp.tool()
async def discover_commissionable_nodes() -> list[CommissionableNodeData]:
    """Discover Commissionable Nodes."""
    client = await client_manager.get_client()
    return await client.discover_commissionable_nodes()


@mcp.tool()
async def get_matter_fabrics(node_id: int) -> list[MatterFabricData]:
    """Get Matter fabrics from a device"""
    client = await client_manager.get_client()
    return await client.get_matter_fabrics(node_id)


@mcp.tool()
async def remove_matter_fabric(node_id: int, fabric_index: int) -> None:
    """Remove a Matter fabric from a device"""
    client = await client_manager.get_client()
    await client.remove_matter_fabric(node_id, fabric_index)


@mcp.tool()
async def ping_node(node_id: int) -> NodePingResult:
    """Ping node on the currently known IP-address(es)"""
    client = await client_manager.get_client()
    return await client.ping_node(node_id)


@mcp.tool()
async def get_node_ip_addresses(
    node_id: int, prefer_cache: Optional[bool] = None, scoped: Optional[bool] = None
) -> list[str]:
    """Return the currently known IP-address(es)"""
    client = await client_manager.get_client()
    return await client.get_node_ip_addresses(node_id, prefer_cache, scoped)


@mcp.tool()
async def remove_node(node_id: int) -> None:
    """Remove a Matter node/device from the fabric"""
    client = await client_manager.get_client()
    await client.remove_node(node_id)


@mcp.tool()
async def interview_node(node_id: int) -> None:
    """Interview a node"""
    client = await client_manager.get_client()
    await client.interview_node(node_id)


@mcp.tool()
async def import_test_node(dump: str) -> None:
    """Import test node(s) from a HA or Matter server diagnostics dump"""
    client = await client_manager.get_client()
    await client.import_test_node(dump)


@mcp.tool()
async def read_attribute(
    node_id: int, attribute_path: str | Sequence[str]
) -> dict[str, Any]:
    """Read one or more attribute(s) on a node"""
    client = await client_manager.get_client()
    return await client.read_attribute(node_id, attribute_path)


@mcp.tool()
async def write_attribute(node_id: int, attribute_path: str, value: Any) -> None:
    """Write an attribute value on a target node"""
    client = await client_manager.get_client()
    await client.write_attribute(node_id, attribute_path, value)


@mcp.tool()
async def check_node_update(node_id: int) -> Optional[MatterSoftwareVersion]:
    """Check if there is an update for a particular node"""
    client = await client_manager.get_client()
    return await client.check_node_update(node_id)


@mcp.tool()
async def update_node(node_id: int, software_version: int | str) -> None:
    """Update a node to a new software version"""
    client = await client_manager.get_client()
    await client.update_node(node_id, software_version)


@mcp.tool()
async def start_listening() -> list[MatterNodeData]:
    """Start listening for Matter events and get initial node list"""
    client = await client_manager.get_client()
    return await client.start_listening()


def main() -> None:
    """Run the MCP server with specified transport and configuration."""
    parser = argparse.ArgumentParser(description="Matter MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type (stdio or sse)",
    )
    parser.add_argument(
        "--matter-server-url",
        type=str,
        default="ws://localhost:5580/ws",
        help="Matter server WebSocket URL",
    )
    args = parser.parse_args()

    os.environ["MATTER_SERVER_URL"] = args.matter_server_url
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
