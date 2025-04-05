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

        // List available tools to verify start_listening is registered
        const toolsResponse = await client.listTools();
        console.log('Tools response type:', typeof toolsResponse);
        console.log('Tools structure:', JSON.stringify(toolsResponse, null, 2));

        // Extract the actual tools array
        const toolsArray = toolsResponse.tools || [];
        console.log('Found tools:', toolsArray.map(t => t.name).join(', '));

        // Check if start_listening is in the list of tools
        const hasStartListening = toolsArray.some(tool => tool.name === 'start_listening');
        console.log('Has start_listening tool:', hasStartListening);

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
        /*
        // Call the commission_on_network tool
        console.log('Calling commission_on_network tool...');
        try {
            const commissionResponse = await client.callTool(
                { 
                    name: 'commission_on_network', 
                    arguments: { setup_pin_code: 20202021  } 
                },
                CallToolResultSchema,
                { 
                    timeout: REQUEST_TIMEOUT, 
                },
            );
            
            console.log('commissionResponse:', commissionResponse);
                          
        } catch (error) {
            console.error('Error calling commission_on_network:', error);
            console.error('Error details:', error.stack);
        }
        // Call the start_listening tool
        console.log('Calling start_listening tool...');
        try {
            const startListeningResponse = await client.callTool(
                { 
                    name: 'start_listening', 
                    arguments: {} 
                },
                CallToolResultSchema,
                { 
                    timeout: REQUEST_TIMEOUT, 
                },
            );
            
            console.log('startListeningResponse:', startListeningResponse);
                          
        } catch (error) {
            console.error('Error calling start_listening:', error);
            console.error('Error details:', error.stack);
        }
        */

    } catch (error) {
        console.error('Error:', error);
    }
}

main();
