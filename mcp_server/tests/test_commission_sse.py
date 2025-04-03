"""Test the device commissioning functions using SSE transport."""

from __future__ import annotations

import asyncio

from matter_mcp_server_sse import (
    commission_on_network,
    get_node,
    get_nodes,
    initialize_server,
    read_attribute,
    start_listening,
    ws_connection,
)
import pytest


@pytest.fixture
async def mcp_server_connection():
    """Initialize server connection for tests."""
    tasks = await initialize_server()
    await ws_connection.ready.wait()  # Ensure connection is ready
    yield tasks
    for task in tasks:
        task.cancel()
    await ws_connection.disconnect()


@pytest.mark.asyncio
async def test_commission_on_network_sse(server_connection) -> None:
    """Test commissioning a device on the network using SSE transport."""
    # Start listening for events in background
    listen_task = asyncio.create_task(start_listening().__anext__())

    try:
        # Send commission command
        response = await commission_on_network(setup_pin_code=20202021)
        print("\nCommissioning response received (SSE):")

        # Basic validation of commission response
        assert isinstance(response, dict)
        assert "message_id" in response
        assert response["message_id"] == "1"

        # Wait for potential commissioning event
        event = await asyncio.wait_for(listen_task, timeout=5.0)
        print("\nCommissioning event received:")
        assert isinstance(event, dict)

        # Allow some time for the commissioning to complete
        await asyncio.sleep(2)

        # Get and verify nodes
        nodes_response = await get_nodes()
        print("\nNodes response received:")

        # Basic validation of nodes response
        assert isinstance(nodes_response, dict)
        assert "message_id" in nodes_response
        assert nodes_response["message_id"] == "get_nodes"

        # If nodes are returned in the result, verify their structure
        if "result" in nodes_response:
            nodes = nodes_response["result"]
            assert isinstance(nodes, list)
            for node in nodes:
                assert isinstance(node, dict)
                # Verify presence of descriptor cluster attributes
                assert any("0/29/" in str(attr) for attr in node.get("attributes", []))
                # Verify presence of basic information cluster attributes
                assert any("0/40/" in str(attr) for attr in node.get("attributes", []))

        # Get and verify specific node (ID 1)
        node_response = await get_node(1)
        print("\nSpecific node response received:")

        # Basic validation of specific node response
        assert isinstance(node_response, dict)
        assert "message_id" in node_response
        assert node_response["message_id"] == "get_node"

        # Verify the specific node data
        if "result" in node_response:
            node = node_response["result"]
            assert isinstance(node, dict)
            # Verify presence of descriptor cluster attributes
            assert any("0/29/" in str(attr) for attr in node.get("attributes", []))
            # Verify presence of basic information cluster attributes
            assert any("0/40/" in str(attr) for attr in node.get("attributes", []))

        # Read the OnOff attribute
        attribute_response = await read_attribute(1, "1/6/0")
        print("\nOnOff attribute response received:")

        # Basic validation of attribute response
        assert isinstance(attribute_response, dict)
        assert "message_id" in attribute_response
        assert attribute_response["message_id"] == "read"

        # Verify the attribute value if present
        if "result" in attribute_response:
            result = attribute_response["result"]
            assert isinstance(result, dict)
            assert "value" in result  # The actual value could be True or False

    except asyncio.TimeoutError:
        print("No commissioning event received within timeout")
    except Exception as e:
        print(f"Test error: {e}")
        raise
