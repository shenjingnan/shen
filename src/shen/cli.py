"""CLI entry point for Shen."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from shen import __version__
from shen.core.app import ShenApp
from shen.utils.logging import setup_logging

console = Console()


@click.group(invoke_without_command=True)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    help="Show version and exit.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode.",
)
@click.pass_context
def cli(ctx: click.Context, version: bool, debug: bool) -> None:
    """Shen - Your AI assistant for daily non-programming tasks.

    Shen helps you automate various daily tasks such as:
    - Document organization and management
    - System cleanup and maintenance
    - Office document creation
    - Security checks
    - And more!
    """
    if version:
        console.print(f"Shen version {__version__}")
        ctx.exit()

    if ctx.invoked_subcommand is None:
        # Show welcome message when no command is provided
        welcome_text = Text.from_markup(
            "[bold cyan]Shen[/bold cyan] - Your AI assistant for daily tasks\n\n"
            f"Version: {__version__}\n"
            "Type 'shen --help' to see available commands."
        )
        console.print(Panel(welcome_text, title="Welcome", border_style="cyan"))

    # Setup logging
    setup_logging(debug=debug)

    # Initialize app context
    ctx.ensure_object(dict)
    ctx.obj["app"] = ShenApp(debug=debug)


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show information about Shen and its capabilities."""
    app: ShenApp = ctx.obj["app"]
    info_text = app.get_info()
    console.print(Panel(info_text, title="Shen Information", border_style="green"))


@cli.command()
@click.argument("task", type=str)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Run in interactive mode.",
)
@click.pass_context
def run(ctx: click.Context, task: str, interactive: bool) -> None:
    """Run a task or command.

    Examples:
        shen run "organize my downloads folder"
        shen run "check system security" --interactive
    """
    app: ShenApp = ctx.obj["app"]

    with console.status(f"Processing: {task}", spinner="dots"):
        try:
            result = app.run_task(task, interactive=interactive)
            console.print(Panel(result, title="Task Result", border_style="green"))
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            ctx.exit(1)


@cli.command()
@click.pass_context
def plugins(ctx: click.Context) -> None:
    """List available plugins and their capabilities."""
    app: ShenApp = ctx.obj["app"]
    plugins_info = app.list_plugins()
    console.print(Panel(plugins_info, title="Available Plugins", border_style="blue"))


@cli.group()
def mcp() -> None:
    """MCP (Model Context Protocol) service management."""
    pass


@mcp.command("list")
@click.pass_context
def mcp_list(ctx: click.Context) -> None:
    """List MCP services and their status."""
    app: ShenApp = ctx.obj["app"]
    status = app.mcp_manager.get_status()

    if not status:
        console.print("[yellow]No MCP services configured.[/yellow]")
        console.print("Run 'shen mcp add' to configure a service.")
        return

    from rich.table import Table

    table = Table(title="MCP Services")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Transport")
    table.add_column("Status", style="green")
    table.add_column("Enabled")

    for name, info in status.items():
        status_text = "🟢 Connected" if info["connected"] else "🔴 Disconnected"
        enabled_text = "✅" if info["enabled"] else "❌"

        table.add_row(
            name,
            info["description"][:50] + "..."
            if len(info["description"]) > 50
            else info["description"],
            info["transport"],
            status_text,
            enabled_text,
        )

    console.print(table)


@mcp.command("connect")
@click.argument("service_name")
@click.pass_context
def mcp_connect(ctx: click.Context, service_name: str) -> None:
    """Connect to an MCP service."""
    import asyncio

    app: ShenApp = ctx.obj["app"]

    async def connect() -> None:
        success = await app.mcp_manager.connect_service(service_name)
        if success:
            console.print(f"[green]✅ Connected to {service_name}[/green]")
        else:
            console.print(f"[red]❌ Failed to connect to {service_name}[/red]")

    asyncio.run(connect())


@mcp.command("disconnect")
@click.argument("service_name")
@click.pass_context
def mcp_disconnect(ctx: click.Context, service_name: str) -> None:
    """Disconnect from an MCP service."""
    import asyncio

    app: ShenApp = ctx.obj["app"]

    async def disconnect() -> None:
        await app.mcp_manager.disconnect_service(service_name)
        console.print(f"[yellow]Disconnected from {service_name}[/yellow]")

    asyncio.run(disconnect())


@mcp.command("tools")
@click.option("--service", help="Show tools from specific service")
@click.pass_context
def mcp_tools(ctx: click.Context, service: str) -> None:
    """List available MCP tools."""
    import asyncio

    app: ShenApp = ctx.obj["app"]

    async def list_tools() -> None:
        if service:
            client = app.mcp_manager.get_client(service)
            if not client or not client.is_connected:
                console.print(f"[red]Service {service} not connected[/red]")
                return

            try:
                tools = await client.list_tools()
                if not tools:
                    console.print(f"[yellow]No tools available in {service}[/yellow]")
                    return

                from rich.table import Table

                table = Table(title=f"Tools from {service}")
                table.add_column("Name", style="cyan")
                table.add_column("Description")

                for tool in tools:
                    table.add_row(tool.name, tool.description)

                console.print(table)
            except Exception as e:
                console.print(f"[red]Error listing tools: {e}[/red]")
        else:
            all_tools = await app.mcp_manager.list_all_tools()
            if not all_tools:
                console.print("[yellow]No tools available from connected services[/yellow]")
                return

            from rich.table import Table

            table = Table(title="All Available Tools")
            table.add_column("Service", style="magenta")
            table.add_column("Tool", style="cyan")
            table.add_column("Description")

            for service_name, tools in all_tools.items():
                for tool in tools:
                    table.add_row(service_name, tool.name, tool.description)

            console.print(table)

    asyncio.run(list_tools())


def main() -> None:
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
