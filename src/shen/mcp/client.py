"""MCP client implementation."""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx
import websockets

from shen.mcp.models import (
    MCPMessage,
    MCPRequest,
    MCPResponse,
    MCPServerInfo,
    MCPServiceConfig,
    MCPTool,
    TransportType,
)
from shen.utils.logging import get_logger

logger = get_logger(__name__)


class MCPClientError(Exception):
    """MCP client error."""

    pass


class MCPTransport(ABC):
    """Abstract MCP transport."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the MCP server."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        pass

    @abstractmethod
    async def send_message(self, message: MCPMessage) -> None:
        """Send a message to the server."""
        pass

    @abstractmethod
    async def receive_message(self) -> MCPMessage:
        """Receive a message from the server."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if transport is connected."""
        pass


class HTTPTransport(MCPTransport):
    """HTTP transport for MCP."""

    def __init__(self, config: MCPServiceConfig) -> None:
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> None:
        """Connect to HTTP endpoint."""
        headers = self.config.headers or {}
        headers.setdefault("Content-Type", "application/json")

        self.client = httpx.AsyncClient(
            base_url=self.config.endpoint,
            headers=headers,
            timeout=self.config.timeout,
        )

    async def disconnect(self) -> None:
        """Disconnect HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def send_message(self, message: MCPMessage) -> None:
        """Send HTTP request."""
        if not self.client:
            raise MCPClientError("Not connected")

        response = await self.client.post("/", json=message.model_dump())
        response.raise_for_status()

    async def receive_message(self) -> MCPMessage:
        """HTTP doesn't support receiving unsolicited messages."""
        raise NotImplementedError("HTTP transport doesn't support receiving messages")

    @property
    def is_connected(self) -> bool:
        """Check if HTTP client is available."""
        return self.client is not None


class WebSocketTransport(MCPTransport):
    """WebSocket transport for MCP."""

    def __init__(self, config: MCPServiceConfig) -> None:
        self.config = config
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None

    async def connect(self) -> None:
        """Connect to WebSocket endpoint."""
        try:
            self.websocket = await websockets.connect(
                self.config.endpoint,
                timeout=self.config.timeout,
            )
        except Exception as e:
            raise MCPClientError(f"Failed to connect to WebSocket: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect WebSocket."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def send_message(self, message: MCPMessage) -> None:
        """Send WebSocket message."""
        if not self.websocket:
            raise MCPClientError("Not connected")

        await self.websocket.send(json.dumps(message.model_dump()))

    async def receive_message(self) -> MCPMessage:
        """Receive WebSocket message."""
        if not self.websocket:
            raise MCPClientError("Not connected")

        data = await self.websocket.recv()
        message_data = json.loads(data)

        if "result" in message_data or "error" in message_data:
            return MCPResponse.model_validate(message_data)
        else:
            return MCPRequest.model_validate(message_data)

    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.websocket is not None and not self.websocket.closed


class MCPClient:
    """MCP client for communicating with MCP servers."""

    def __init__(self, config: MCPServiceConfig) -> None:
        self.config = config
        self.transport = self._create_transport()
        self.server_info: Optional[MCPServerInfo] = None
        self._request_id = 0
        self._pending_requests: dict[str, asyncio.Future] = {}

    def _create_transport(self) -> MCPTransport:
        """Create transport based on configuration."""
        if self.config.transport == TransportType.HTTP:
            return HTTPTransport(self.config)
        elif self.config.transport == TransportType.WEBSOCKET:
            return WebSocketTransport(self.config)
        else:
            raise MCPClientError(f"Unsupported transport: {self.config.transport}")

    async def connect(self) -> None:
        """Connect to MCP server and initialize."""
        try:
            await self.transport.connect()

            # Initialize connection
            await self._initialize()

            logger.info(f"Connected to MCP server: {self.config.name}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.config.name}: {e}")
            raise MCPClientError(f"Connection failed: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        await self.transport.disconnect()
        self.server_info = None
        self._pending_requests.clear()
        logger.info(f"Disconnected from MCP server: {self.config.name}")

    async def _initialize(self) -> None:
        """Initialize MCP connection."""
        # Send initialize request
        response = await self.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {},
                },
                "clientInfo": {
                    "name": "shen",
                    "version": "0.0.0-beta.0",
                },
            },
        )

        if response.error:
            raise MCPClientError(f"Initialization failed: {response.error}")

        # Store server info
        if response.result:
            self.server_info = MCPServerInfo.model_validate(response.result.get("serverInfo", {}))

        # Send initialized notification
        await self.send_notification("notifications/initialized")

    def _next_request_id(self) -> str:
        """Generate next request ID."""
        self._request_id += 1
        return str(self._request_id)

    async def send_request(
        self, method: str, params: Optional[dict[str, Any]] = None
    ) -> MCPResponse:
        """Send a request and wait for response."""
        request_id = self._next_request_id()

        request = MCPRequest(
            id=request_id,
            method=method,
            params=params,
        )

        # Create future for response
        future: asyncio.Future[MCPResponse] = asyncio.Future()
        self._pending_requests[request_id] = future

        try:
            await self.transport.send_message(request)

            # Wait for response (with timeout)
            response = await asyncio.wait_for(future, timeout=self.config.timeout)
            return response
        except asyncio.TimeoutError as e:
            self._pending_requests.pop(request_id, None)
            raise MCPClientError(f"Request timeout: {method}") from e
        except Exception as e:
            self._pending_requests.pop(request_id, None)
            raise MCPClientError(f"Request failed: {e}") from e

    async def send_notification(self, method: str, params: Optional[dict[str, Any]] = None) -> None:
        """Send a notification (no response expected)."""
        notification = MCPRequest(method=method, params=params)
        await self.transport.send_message(notification)

    async def list_tools(self) -> list[MCPTool]:
        """List available tools from the server."""
        response = await self.send_request("tools/list")

        if response.error:
            raise MCPClientError(f"Failed to list tools: {response.error}")

        tools = response.result.get("tools", []) if response.result else []
        return [MCPTool.model_validate(tool) for tool in tools]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool on the server."""
        response = await self.send_request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments,
            },
        )

        if response.error:
            raise MCPClientError(f"Tool call failed: {response.error}")

        return response.result or {}

    async def list_resources(self) -> list[dict[str, Any]]:
        """List available resources from the server."""
        response = await self.send_request("resources/list")

        if response.error:
            raise MCPClientError(f"Failed to list resources: {response.error}")

        return response.result.get("resources", []) if response.result else []

    async def read_resource(self, uri: str) -> dict[str, Any]:
        """Read a resource from the server."""
        response = await self.send_request("resources/read", {"uri": uri})

        if response.error:
            raise MCPClientError(f"Failed to read resource: {response.error}")

        return response.result or {}

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.transport.is_connected
