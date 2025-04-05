import asyncio
from contextlib import suppress
import json
import signal
from typing import Any

import anyio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
from WebSocketConnection import WebSocketConnection

# Initialize FastAPI server and WebSocket connection
app = FastAPI()
ws_connection = WebSocketConnection()
tasks = []


# Add shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when the server shuts down."""
    print("Shutting down server...")
    for task in tasks:
        if not task.done():
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    if ws_connection.ready.is_set():
        print("Disconnecting WebSocket...")
        await ws_connection.disconnect()


async def event_stream():
    """Streams events from WebSocket to SSE clients."""
    counter = 0
    yield "data: Connection established\n\n"  # Initial message

    while True:
        try:
            # Send a heartbeat message every 10 seconds if no other messages
            counter += 1
            yield f"data: Heartbeat {counter}\n\n"  # SSE format

            # Try to get a message from the WebSocket with a timeout
            try:
                if (
                    ws_connection.ready.is_set()
                    and not ws_connection.incoming_queue.empty()
                ):
                    message = ws_connection.incoming_queue.get_nowait()
                    yield f"data: {json.dumps(message)}\n\n"
                    ws_connection.incoming_queue.task_done()
            except asyncio.QueueEmpty:
                pass  # No messages available

            await asyncio.sleep(2)
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
            await asyncio.sleep(5)  # Wait longer after an error


@app.get("/matter_updates")
async def sse_endpoint():
    """SSE endpoint that streams real-time events."""
    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def start_listening() -> dict[str, Any]:
    """Start listening for Matter events and stream them to the
    client when the client calls the url endpoint /sse.
    """
    print("start_listening called!")

    try:
        print("Waiting for WebSocket connection to be ready...")
        # Add a timeout to prevent indefinite waiting
        await asyncio.wait_for(ws_connection.ready.wait(), timeout=5)
        print("WebSocket ready, sending start_listening command...")

        # Send initial "start listening" command
        message = {
            "command": "start_listening",
            "args": {},
            "message_id": "start_listening",
        }

        await ws_connection.outgoing_queue.put(message)
        print("Command sent, waiting for response...")

        # Add timeout for response
        response = await asyncio.wait_for(ws_connection.incoming_queue.get(), timeout=5)
        print(f"Response received: {response}")
        ws_connection.incoming_queue.task_done()
        return response
    except asyncio.TimeoutError:
        print("Timeout while waiting for WebSocket response!")
        return {"status": "timeout"}
    except Exception as e:
        print(f"Error in start_listening: {e}")
        return {"status": "error", "message": str(e)}


async def initialize_server():
    """Initialize the WebSocket connection and start message handling."""
    await ws_connection.connect()
    await start_listening()
    return [
        asyncio.create_task(ws_connection.listen()),
        asyncio.create_task(ws_connection.send_messages()),
    ]


async def start_server():
    """Start the server."""
    tasks = await initialize_server()


if __name__ == "__main__":
    print("Starting application...")

    # Use anyio to run both the websocket connection and the uvicorn server
    async def run_everything():
        """Run both the websocket connection and the uvicorn server."""
        global tasks
        print("Initializing WebSocket connection...")
        tasks = await initialize_server()
        print("WebSocket connection initialized, starting HTTP server...")
        config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="info")
        server = uvicorn.Server(config)
        print("Server configured, starting to serve...")

        # Setup signal handlers for graceful shutdown
        original_handler = signal.getsignal(signal.SIGINT)

        def signal_handler(sig, frame):
            print("Received shutdown signal, cleaning up...")
            asyncio.create_task(shutdown_event())
            # Restore original handler to allow a second Ctrl+C to force exit
            signal.signal(signal.SIGINT, original_handler)

        signal.signal(signal.SIGINT, signal_handler)

        try:
            await server.serve()
        finally:
            print("Server stopped, cleaning up resources...")
            await shutdown_event()

    anyio.run(run_everything)
