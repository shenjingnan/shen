"""MCP service manager."""

import asyncio
import json
from pathlib import Path
from typing import Optional

from shen.mcp.client import MCPClient, MCPClientError
from shen.mcp.models import MCPServiceConfig, MCPTool, TransportType
from shen.utils.logging import get_logger

logger = get_logger(__name__)


class MCPManager:
    """Manages MCP services and connections."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize MCP manager.

        Args:
            config_dir: Directory containing MCP service configurations
        """
        self.config_dir = config_dir or Path.home() / ".shen" / "mcp"
        self.services: dict[str, MCPServiceConfig] = {}
        self.clients: dict[str, MCPClient] = {}
        self._lock = asyncio.Lock()

    def load_services(self) -> None:
        """Load MCP service configurations from config directory."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self._create_example_config()
            return

        config_files = list(self.config_dir.glob("*.json"))
        if not config_files:
            self._create_example_config()
            return

        for config_file in config_files:
            try:
                with open(config_file) as f:
                    config_data = json.load(f)

                config = MCPServiceConfig.model_validate(config_data)
                self.services[config.name] = config
                logger.info(f"Loaded MCP service config: {config.name}")
            except Exception as e:
                logger.error(f"Failed to load config {config_file}: {e}")

    def _create_example_config(self) -> None:
        """Create example MCP service configuration."""
        example_config = MCPServiceConfig(
            name="example-filesystem",
            description="Example filesystem MCP server",
            transport=TransportType.STDIO,
            endpoint="npx @modelcontextprotocol/server-filesystem /path/to/directory",
            args=["npx", "@modelcontextprotocol/server-filesystem", "/tmp"],
            enabled=False,
        )

        config_file = self.config_dir / "example-filesystem.json"
        with open(config_file, "w") as f:
            json.dump(example_config.model_dump(), f, indent=2)

        logger.info(f"Created example config: {config_file}")

    def add_service(self, config: MCPServiceConfig) -> None:
        """Add a new MCP service configuration.

        Args:
            config: MCP service configuration
        """
        self.services[config.name] = config

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Save to file
        config_file = self.config_dir / f"{config.name}.json"
        with open(config_file, "w") as f:
            json.dump(config.model_dump(), f, indent=2)

        logger.info(f"Added MCP service: {config.name}")

    def remove_service(self, name: str) -> bool:
        """Remove an MCP service configuration.

        Args:
            name: Service name

        Returns:
            True if service was removed
        """
        if name not in self.services:
            return False

        # Disconnect if connected (only if there's a running event loop)
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self.disconnect_service(name))
        except RuntimeError:
            # No event loop running, just clean up the client
            self.clients.pop(name, None)

        # Remove from memory
        del self.services[name]

        # Remove config file
        config_file = self.config_dir / f"{name}.json"
        if config_file.exists():
            config_file.unlink()

        logger.info(f"Removed MCP service: {name}")
        return True

    def list_services(self) -> list[MCPServiceConfig]:
        """List all MCP service configurations.

        Returns:
            List of service configurations
        """
        return list(self.services.values())

    def get_service(self, name: str) -> Optional[MCPServiceConfig]:
        """Get MCP service configuration by name.

        Args:
            name: Service name

        Returns:
            Service configuration or None
        """
        return self.services.get(name)

    async def connect_service(self, name: str) -> bool:
        """Connect to an MCP service.

        Args:
            name: Service name

        Returns:
            True if connected successfully
        """
        async with self._lock:
            if name in self.clients:
                return self.clients[name].is_connected

            config = self.services.get(name)
            if not config or not config.enabled:
                logger.warning(f"Service {name} not found or disabled")
                return False

            try:
                client = MCPClient(config)
                await client.connect()
                self.clients[name] = client
                logger.info(f"Connected to MCP service: {name}")
                return True
            except MCPClientError as e:
                logger.error(f"Failed to connect to {name}: {e}")
                return False

    async def disconnect_service(self, name: str) -> None:
        """Disconnect from an MCP service.

        Args:
            name: Service name
        """
        async with self._lock:
            client = self.clients.pop(name, None)
            if client:
                await client.disconnect()
                logger.info(f"Disconnected from MCP service: {name}")

    async def disconnect_all(self) -> None:
        """Disconnect from all MCP services."""
        async with self._lock:
            for name in list(self.clients.keys()):
                await self.disconnect_service(name)

    def get_client(self, name: str) -> Optional[MCPClient]:
        """Get MCP client by service name.

        Args:
            name: Service name

        Returns:
            MCP client or None
        """
        return self.clients.get(name)

    async def list_all_tools(self) -> dict[str, list[MCPTool]]:
        """List tools from all connected services.

        Returns:
            Dictionary mapping service name to tools
        """
        all_tools = {}

        for name, client in self.clients.items():
            if client.is_connected:
                try:
                    tools = await client.list_tools()
                    all_tools[name] = tools
                except MCPClientError as e:
                    logger.error(f"Failed to list tools from {name}: {e}")
                    all_tools[name] = []

        return all_tools

    async def call_tool(self, service_name: str, tool_name: str, arguments: dict) -> dict:
        """Call a tool on a specific service.

        Args:
            service_name: MCP service name
            tool_name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        client = self.clients.get(service_name)
        if not client or not client.is_connected:
            raise MCPClientError(f"Service {service_name} not connected")

        return await client.call_tool(tool_name, arguments)

    async def auto_connect_enabled(self) -> None:
        """Auto-connect to all enabled services."""
        for name, config in self.services.items():
            if config.enabled:
                success = await self.connect_service(name)
                if success:
                    logger.info(f"Auto-connected to {name}")
                else:
                    logger.warning(f"Failed to auto-connect to {name}")

    def get_status(self) -> dict[str, dict]:
        """Get status of all services.

        Returns:
            Dictionary with service status information
        """
        status = {}

        for name, config in self.services.items():
            client = self.clients.get(name)
            status[name] = {
                "name": name,
                "description": config.description,
                "transport": config.transport.value,
                "endpoint": config.endpoint,
                "enabled": config.enabled,
                "connected": client.is_connected if client else False,
                "server_info": client.server_info.model_dump()
                if client and client.server_info
                else None,
            }

        return status
