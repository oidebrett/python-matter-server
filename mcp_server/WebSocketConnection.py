import asyncio
import json
import logging
from typing import Optional

import aiohttp
from aiohttp import WSMsgType

# Initialize logging
logger = logging.getLogger(__name__)


class WebSocketConnection:
    """WebSocket connection handler for Matter Control Protocol.

    Manages WebSocket connection to the Matter server, including connection establishment,
    message sending/receiving, and reconnection logic.
    """

    def __init__(self, host: str = "ws://127.0.0.1", port: int = 5580):
        """Initialize the WebSocket connection.

        Args:
            host: WebSocket host address. Defaults to "ws://127.0.0.1".
            port: WebSocket port number. Defaults to 5580.
        """
        self.url = f"{host}:{port}/ws"
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.ready = asyncio.Event()
        self.outgoing_queue: asyncio.Queue = asyncio.Queue()
        self.incoming_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self):
        """Establish WebSocket connection."""
        try:
            self.session = aiohttp.ClientSession()
            self.ws = await self.session.ws_connect(self.url)
            # Ignore initial status message
            await self.ws.receive()
            self.ready.set()
        except (aiohttp.ClientError, aiohttp.WebSocketError, ConnectionError) as err:
            print(f"Connection error: {err}")
            if self.session:
                await self.session.close()
            raise

    async def disconnect(self):
        """Close WebSocket connection."""
        self.ready.clear()
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()

    async def listen(self):
        """Listen for messages from WebSocket and put them in incoming queue."""
        while True:
            try:
                if not self.ws:
                    await asyncio.sleep(1)
                    continue

                msg = await self.ws.receive()
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.incoming_queue.put(data)
                elif msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSE, WSMsgType.ERROR):
                    self.ready.clear()
                    await self.connect()
            except (
                aiohttp.ClientError,
                aiohttp.WebSocketError,
                ConnectionError,
                json.JSONDecodeError,
            ) as err:
                print(f"WebSocket error: {err}")
                await asyncio.sleep(1)

    async def maintain_connection(self):
        """Maintain the WebSocket connection."""
        while True:
            try:
                if not self.ws or self.ws.closed:
                    self.ready.clear()
                    await self.connect()
            except (
                aiohttp.ClientError,
                aiohttp.WebSocketError,
                ConnectionError,
            ) as err:
                print(f"WebSocket error: {err}")
                await asyncio.sleep(1)

    async def send_messages(self):
        """Send messages from the outgoing queue."""
        while True:
            try:
                message = await self.outgoing_queue.get()
                if not self.ws:
                    continue
                await self.ws.send_json(message)
                self.outgoing_queue.task_done()
            except (
                aiohttp.ClientError,
                aiohttp.WebSocketError,
                ConnectionError,
            ) as err:
                print(f"Error sending message: {err}")
                await asyncio.sleep(1)
