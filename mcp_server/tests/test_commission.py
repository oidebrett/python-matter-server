"""Test the device commissioning functions."""

from __future__ import annotations

import asyncio

from matter_mcp_server import commission_on_network
import pytest


@pytest.mark.asyncio
async def test_commission_on_network_stdio() -> None:
    """Test commissioning a device on the network with stdio transport."""
    response = await commission_on_network(setup_pin_code=20202021)
    print("\nActual response received (stdio):")
    assert response == []
    await asyncio.sleep(30)
