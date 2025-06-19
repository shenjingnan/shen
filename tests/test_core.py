"""Tests for core functionality."""

from pathlib import Path

import pytest
from shen.core.app import ShenApp
from shen.core.config import Config, ShenSettings
from shen.core.plugin_manager import PluginManager


class TestShenApp:
    """Test ShenApp class."""

    def test_initialization(self) -> None:
        """Test app initialization."""
        app = ShenApp(debug=False)
        assert app.debug is False
        assert isinstance(app.config, Config)
        assert isinstance(app.plugin_manager, PluginManager)

    def test_debug_mode(self) -> None:
        """Test app in debug mode."""
        app = ShenApp(debug=True)
        assert app.debug is True

    def test_get_info(self) -> None:
        """Test get_info method."""
        app = ShenApp()
        info = app.get_info()
        assert "Shen v" in info
        assert "Capabilities:" in info
        assert "Document organization" in info

    def test_run_task(self) -> None:
        """Test run_task method."""
        app = ShenApp()
        result = app.run_task("test task")
        assert "Task execution not yet implemented" in result
        assert "test task" in result

    def test_run_task_interactive(self) -> None:
        """Test run_task in interactive mode."""
        app = ShenApp()
        result = app.run_task("test task", interactive=True)
        assert "Interactive mode not yet implemented" in result
        assert "test task" in result

    def test_list_plugins(self) -> None:
        """Test list_plugins method."""
        app = ShenApp()
        result = app.list_plugins()
        assert "Plugin system under development" in result or "No plugins" in result


class TestConfig:
    """Test Config class."""

    def test_initialization(self, tmp_path: Path) -> None:
        """Test config initialization."""
        config = Config()
        assert isinstance(config.settings, ShenSettings)
        assert config.config_dir == Path.home() / ".shen"

    def test_get_default_values(self) -> None:
        """Test getting default configuration values."""
        config = Config()
        assert config.get("debug") is False
        assert config.get("mcp_enabled") is False
        assert config.get("nonexistent", "default") == "default"

    def test_set_and_get_values(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test setting and getting configuration values."""
        # Use temporary directory for config
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config = Config()
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"

        # Test persistence
        config2 = Config()
        config2.load()
        assert config2.get("test_key") == "test_value"


class TestPluginManager:
    """Test PluginManager class."""

    def test_initialization(self) -> None:
        """Test plugin manager initialization."""
        manager = PluginManager()
        assert isinstance(manager.plugins, dict)
        assert len(manager.plugins) == 0

    def test_get_plugin_not_found(self) -> None:
        """Test getting non-existent plugin."""
        manager = PluginManager()
        plugin = manager.get_plugin("nonexistent")
        assert plugin is None

    def test_find_plugins_for_task_empty(self) -> None:
        """Test finding plugins when none exist."""
        manager = PluginManager()
        plugins = manager.find_plugins_for_task("test task")
        assert len(plugins) == 0
