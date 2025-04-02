"""Test the light control functions."""

from __future__ import annotations

from matter_mcp_server import device_command, read_attribute
import pytest


@pytest.mark.asyncio
async def test_onoffcluster_on(node_id, endpoint_id) -> None:
    """Test turning on a onoffcluster and verifying its state."""
    # Turn on the onoffcluster
    response = await device_command(
        endpoint_id=endpoint_id,
        node_id=node_id,
        cluster_id=6,  # OnOff cluster ID
        command_name="On",
    )
    assert response == [{"message_id": "device_command", "result": None}]

    # Read the onoffcluster state
    state = await read_attribute(
        node_id=node_id,
        attribute_path=f"{endpoint_id}/6/0",  # endpoint/cluster/attribute format
    )
    assert "/6/0': True" in str(state)


@pytest.mark.asyncio
async def test_onoffcluster_off(node_id, endpoint_id) -> None:
    """Test turning off a onoffcluster and verifying its state."""
    # Turn off the onoffcluster
    response = await device_command(
        endpoint_id=endpoint_id,
        node_id=node_id,
        cluster_id=6,  # OnOff cluster ID
        command_name="Off",
    )
    assert response == [{"message_id": "device_command", "result": None}]

    # Read the onoffcluster state
    state = await read_attribute(
        node_id=node_id,
        attribute_path=f"{endpoint_id}/6/0",  # endpoint/cluster/attribute format
    )
    assert "/6/0': False" in str(state)
