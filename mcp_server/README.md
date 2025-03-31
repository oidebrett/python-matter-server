# Matter MCP Server

This is a Matter Control Protocol (MCP) server implementation that wraps the Matter Server WebSocket API. It provides a command-line interface to interact with Matter devices through the Matter Server.

## Installation

1. Install the MCP CLI package:
```bash
pip install mcp[cli]
```

2. Install the Matter Server client:
```bash
pip install python-matter-server
```

## Usage

The MCP server can be run in two transport modes:

### STDIO Transport

This mode is useful for direct command-line interaction or when integrating with other tools that communicate via standard input/output.

```bash
python mcp_stdio_example.py
```

Or with custom Matter server URL:
```bash
MATTER_SERVER_URL="ws://custom-host:5580/ws" python mcp_stdio_example.py
```

### SSE (Server-Sent Events) Transport

This mode is useful for web applications or services that need to consume Matter server events.

```bash
python mcp_sse_example.py
```

Or with command-line arguments:
```bash
python mcp_server.py --transport sse --matter-server-url ws://localhost:5580/ws
```

## Available Commands

The MCP server provides the following Matter control commands:

- `commission_with_code`: Commission a device using QR Code or Manual Pairing Code
- `set_wifi_credentials`: Set WiFi credentials for device commissioning
- `set_thread_dataset`: Set Thread Operational dataset
- `open_commissioning_window`: Open a commissioning window on a node
- `discover_commissionable_nodes`: Discover available Matter devices
- `get_matter_fabrics`: Get Matter fabrics from a device
- `remove_matter_fabric`: Remove a Matter fabric from a device
- `ping_node`: Ping a node
- `get_node_ip_addresses`: Get IP addresses for a node
- `remove_node`: Remove a Matter node from the fabric
- `interview_node`: Interview a node
- `import_test_node`: Import test nodes from a dump
- `read_attribute`: Read node attributes
- `write_attribute`: Write node attributes
- `check_node_update`: Check for node updates
- `update_node`: Update a node
- `start_listening`: Start listening for Matter events

## Requirements

- Python 3.11 or higher
- Running Matter Server instance (default: ws://localhost:5580/ws)
- MCP CLI package
- python-matter-server package

## Environment Variables

- `MATTER_SERVER_URL`: WebSocket URL of the Matter server (default: ws://localhost:5580/ws)

## Example Usage

Using STDIO transport with MCP CLI:

```bash
# Start the server
python mcp_stdio_example.py

# In another terminal, use MCP CLI to interact
mcp commission-with-code "MT:Y.K9042C00KA0661B00" false
mcp read-attribute 1 "endpoint=1;cluster=basic;attribute=vendor_name"
```

Using SSE transport for web applications:

```bash
# Start the server with SSE transport
python mcp_sse_example.py

# Connect to the SSE endpoint (typically http://localhost:5001/events)
# and consume events in your web application
```

## Related Projects

- [Matter Server](https://github.com/home-assistant-libs/python-matter-server)
- [Home Assistant Matter Integration](https://www.home-assistant.io/integrations/matter/)
