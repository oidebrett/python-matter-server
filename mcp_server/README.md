# Matter MCP Server

This is a Matter Control Protocol (MCP) server implementation that wraps the Matter Server WebSocket API. It provides a command-line interface to interact with Matter devices through the Matter Server using aiohttp for WebSocket communication.

## Installation

1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install the required packages:
```bash
source ../.venv/bin/activate
uv add "mcp[cli]" aiohttp
```

## Installing MCP in Claude

5. Edit the claude_desktop_config.json config file

This file is located in different locations depending on your operating system. e.g
Ubuntu: ~/.config/Claude
MacOS: ~/Library/Application Support/Claude
Windows: %APPDATA%\Claude

6. Add the following to claude_desktop_config.json:

```bash
{
    "mcpServers": {
        "matter-mcp-server": {
            "command": "uv",
            "args": [
                "--directory",
                "[REPLACE_WITH_FULL_PATH_TO_YOUR_REPO]",
                "run",
                "matter_mcp_server.py"
            ]
        }
    }
}
```

7. Restart Claude Desktop and wait for mcp tools to load

8. Claude Code - MCP Server install

If you have Claude Code installed then execute the following commands in a terminal

```bash
claude mcp add
```

```bash
mater_mcp_server
```

```bash
uv --directory [REPLACE_WITH_FULL_PATH_TO_YOUR_REPO] run matter_mcp_server.py
```

## Testing
### Testing with a Matter device?

A Matter Virtual Device (MVD) is a software-based emulator provided by Google that simulates Matter-compatible smart home devices for testing and development. It allows developers to validate device behavior without physical hardware. To set it up, use the Matter Virtual Device Tool, follow the steps in the [MVD official guide](https://developers.home.google.com/matter/tools/virtual-device)

Run the MVD
```bash
MVD
```

### Testing with pytest

Ensure you identify the node id and endpoint id and run pytest

```bash
python3 -m pytest --node_id=1 --endpoint_id=13
```


## Requirements

- Python 3.11 or higher
- uv
- Running Matter Server instance
- aiohttp
- MCP CLI package
- python-matter-server package

## Related Projects

- [Matter Server](https://github.com/home-assistant-libs/python-matter-server)
- [Home Assistant Matter Integration](https://www.home-assistant.io/integrations/matter/)
