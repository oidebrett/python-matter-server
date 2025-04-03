import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js';
import { CallToolResultSchema } from '@modelcontextprotocol/sdk/types.js';
import { EventSource } from 'eventsource';

// Add EventSource to global scope if not available
if (typeof globalThis.EventSource === 'undefined') {
    globalThis.EventSource = EventSource;
}

const SERVER_URL = 'http://localhost:8000/sse';
const REQUEST_TIMEOUT = 120_000; // 2 minutes

async function main() {
    const transport = new SSEClientTransport(
        new URL(SERVER_URL),
        {
            requestInit: {
                headers: {
                    'Accept': 'text/event-stream',
                },
                mode: 'cors',
                credentials: 'omit'
            },
            eventSourceInit: {
                withCredentials: false
            }
        }
    );

    const client = new Client(
        { name: 'simple-mcp-client', version: '1.0.0' },
        {
            capabilities: {},
            schemaValidation: false
        }
    );

    try {
        await client.connect(transport);
        console.log('Connected to MCP server');

        const tools = await client.listTools();
        console.log('Available tools:', tools);


        const result = await client.callTool(
            { name: 'get_nodes', arguments: { } },
            CallToolResultSchema,
            { timeout: REQUEST_TIMEOUT },
        );
        console.log(result)

        const result_node = await client.callTool(
            { name: 'get_node', arguments: { node_id: 1 } },
            CallToolResultSchema,
            { timeout: REQUEST_TIMEOUT },
        );
        console.log(result_node)

    } catch (error) {
        console.error('Error:', error);
    }
}

main();
