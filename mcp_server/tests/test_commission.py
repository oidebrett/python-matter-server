"""Test the device commissioning functions."""

from __future__ import annotations

import asyncio

from matter_mcp_server import commission_on_network
import pytest


@pytest.mark.asyncio
async def test_commission_on_network() -> None:
    """Test commissioning a device on the network with default PIN."""
    response = await commission_on_network(setup_pin_code=20202021)
    print("\nActual response received:")
    assert response == []
    await asyncio.sleep(3)  # Wait for 3 seconds to allow commissioning to complete
