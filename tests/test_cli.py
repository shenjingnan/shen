"""Tests for CLI functionality."""

from click.testing import CliRunner
from shen import __version__
from shen.cli import cli


def test_version() -> None:
    """Test version display."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert f"Shen version {__version__}" in result.output


def test_help() -> None:
    """Test help display."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Shen - Your AI assistant for daily non-programming tasks" in result.output
    assert "Show version and exit" in result.output


def test_info_command() -> None:
    """Test info command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["info"])
    assert result.exit_code == 0
    assert "Shen Information" in result.output
    assert f"Shen v{__version__}" in result.output


def test_plugins_command() -> None:
    """Test plugins command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["plugins"])
    assert result.exit_code == 0
    assert "Available Plugins" in result.output


def test_run_command() -> None:
    """Test run command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "test task"])
    assert result.exit_code == 0
    assert "Task Result" in result.output
    assert "test task" in result.output


def test_run_command_interactive() -> None:
    """Test run command with interactive flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "test task", "--interactive"])
    assert result.exit_code == 0
    assert "Task Result" in result.output
    assert "Interactive mode not yet implemented" in result.output


def test_no_command_shows_welcome() -> None:
    """Test that running without command shows welcome message."""
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert "Welcome" in result.output
    assert "Shen - Your AI assistant for daily tasks" in result.output
