# Matter MCP Server

This is a Matter Control Protocol (MCP) server implementation that wraps the Matter Server WebSocket API. It provides a command-line interface to interact with Matter devices through the Matter Server using aiohttp for WebSocket communication.

## Installation

1. Install the required packages:
```bash
pip install mcp[cli] python-matter-server aiohttp
```

## Usage

The MCP server provides an async interface to communicate with Matter devices. Here's a basic example:

```python
import asyncio
from matter_mcp_server import test_light_on

# Turn on a light with node_id 3 and endpoint_id 1
asyncio.run(test_light_on(3, 1))
```

## Available Commands

The MCP server provides the following Matter control commands through WebSocket:

### Device Control
- `device_command`: Send commands to devices (e.g., turn on/off lights)
- `read_attribute`: Read node attributes
- `write_attribute`: Write node attributes

### Device Management
- `commission_with_code`: Commission a device using QR Code or Manual Pairing Code
- `get_node`: Get detailed information about a specific node
- `get_nodes`: Get information about all nodes
- `start_listening`: Start listening for Matter events

### Network Configuration
- `set_wifi_credentials`: Set WiFi credentials for device commissioning
- `set_thread_dataset`: Set Thread Operational dataset

## WebSocket Communication

The server uses aiohttp for WebSocket communication with the Matter Server. Default connection:
- Host: ws://127.0.0.1
- Port: 5580
- Endpoint: /ws

Example WebSocket message format:
```json
{
    "message_id": "1",
    "command": "device_command",
    "args": {
        "endpoint_id": 1,
        "node_id": 3,
        "cluster_id": 6,
        "command_name": "On"
    }
}
```

## Environment Variables

- `MATTER_SERVER_URL`: WebSocket URL of the Matter server (default: ws://localhost:5580/ws)

## Example Usage

```python
from matter_mcp_server import device_command, read_attribute

async def control_light(node_id: int, endpoint_id: int):
    # Turn on light
    response = await device_command(
        endpoint_id=endpoint_id,
        node_id=node_id,
        cluster_id=6,     # OnOff cluster ID
        command_name="On"
    )

    # Read light state
    state = await read_attribute(
        node_id=node_id,
        attribute_path=f"endpoint={endpoint_id};cluster=on_off;attribute=on_off"
    )
```

## Requirements

- Python 3.11 or higher
- Running Matter Server instance
- aiohttp
- MCP CLI package
- python-matter-server package

## Related Projects

- [Matter Server](https://github.com/home-assistant-libs/python-matter-server)
- [Home Assistant Matter Integration](https://www.home-assistant.io/integrations/matter/)
