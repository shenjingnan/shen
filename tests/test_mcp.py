"""Tests for MCP functionality."""

from pathlib import Path

import pytest
from shen.mcp.manager import MCPManager
from shen.mcp.models import MCPServiceConfig, TransportType


class TestMCPManager:
    """Test MCPManager class."""

    def test_initialization(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test MCP manager initialization."""
        # Use temporary directory for config
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        manager = MCPManager()
        assert manager.config_dir == tmp_path / ".shen" / "mcp"
        assert isinstance(manager.services, dict)
        assert isinstance(manager.clients, dict)

    def test_load_services_creates_example(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that load_services creates example config when none exist."""
        # Use temporary directory for config
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        manager = MCPManager()
        manager.load_services()

        # Should create config directory and example file
        assert manager.config_dir.exists()
        example_file = manager.config_dir / "example-filesystem.json"
        assert example_file.exists()

    def test_add_service(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test adding a new service."""
        # Use temporary directory for config
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        manager = MCPManager()
        manager.load_services()  # Create config dir

        config = MCPServiceConfig(
            name="test-service",
            description="Test service",
            transport=TransportType.HTTP,
            endpoint="http://localhost:8000",
        )

        manager.add_service(config)

        # Check service was added
        assert "test-service" in manager.services
        assert manager.services["test-service"] == config

        # Check config file was created
        config_file = manager.config_dir / "test-service.json"
        assert config_file.exists()

    def test_remove_service(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test removing a service."""
        # Use temporary directory for config
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        manager = MCPManager()
        manager.load_services()  # Create config dir

        # Add a service first
        config = MCPServiceConfig(
            name="test-service",
            description="Test service",
            transport=TransportType.HTTP,
            endpoint="http://localhost:8000",
        )
        manager.add_service(config)

        # Remove the service
        result = manager.remove_service("test-service")
        assert result is True
        assert "test-service" not in manager.services

        # Check config file was removed
        config_file = manager.config_dir / "test-service.json"
        assert not config_file.exists()

        # Test removing non-existent service
        result = manager.remove_service("non-existent")
        assert result is False

    def test_list_services(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test listing services."""
        # Use temporary directory for config
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        manager = MCPManager()

        # Add a service manually for testing
        config = MCPServiceConfig(
            name="test-service",
            description="Test service",
            transport=TransportType.HTTP,
            endpoint="http://localhost:8000",
        )
        manager.add_service(config)

        # Test listing services
        services = manager.list_services()
        assert len(services) == 1
        assert services[0].name == "test-service"

    def test_get_service(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting a specific service."""
        # Use temporary directory for config
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        manager = MCPManager()
        manager.load_services()

        # Get existing service by checking what was actually created
        services = manager.list_services()
        if services:
            service_name = services[0].name
            service = manager.get_service(service_name)
            assert service is not None
            assert service.name == service_name

        # Get non-existent service
        service = manager.get_service("non-existent")
        assert service is None

    def test_get_status(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting service status."""
        # Use temporary directory for config
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        manager = MCPManager()
        manager.load_services()

        status = manager.get_status()
        assert isinstance(status, dict)

        # Check if any services exist and verify their status structure
        if status:
            service_name = list(status.keys())[0]
            service_status = status[service_name]
            assert "name" in service_status
            assert "description" in service_status
            assert "transport" in service_status
            assert "enabled" in service_status
            assert "connected" in service_status
            assert service_status["connected"] is False  # Not connected initially
