"""Pytest configuration for MCP server tests."""

import pytest


def pytest_addoption(parser):
    """Add command line options to pytest."""
    parser.addoption(
        "--node_id",
        action="store",
        default="1",
        type=int,
        help="Node ID to use for testing (default: 1)",
    )
    parser.addoption(
        "--endpoint_id",
        action="store",
        default="1",
        type=int,
        help="Endpoint ID to use for testing (default: 1)",
    )


@pytest.fixture
def node_id(request):
    """Fixture to get the node ID from command line or use default."""
    return request.config.getoption("--node_id")


@pytest.fixture
def endpoint_id(request):
    """Fixture to get the endpoint ID from command line or use default."""
    return request.config.getoption("--endpoint_id")
