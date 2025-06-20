"""MCP (Model Context Protocol) data models."""

from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class TransportType(str, Enum):
    """Supported transport types."""

    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


class MCPCapability(BaseModel):
    """MCP capability definition."""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class MCPTool(BaseModel):
    """MCP tool definition."""

    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)


class MCPResource(BaseModel):
    """MCP resource definition."""

    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None


class MCPPrompt(BaseModel):
    """MCP prompt template definition."""

    name: str
    description: str
    arguments: list[dict[str, Any]] = Field(default_factory=list)


class MCPServerInfo(BaseModel):
    """MCP server information."""

    name: str
    version: str
    protocol_version: str = "2024-11-05"
    capabilities: dict[str, Any] = Field(default_factory=dict)


class MCPMessage(BaseModel):
    """Base MCP message."""

    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None


class MCPRequest(MCPMessage):
    """MCP request message."""

    method: str
    params: Optional[dict[str, Any]] = None


class MCPResponse(MCPMessage):
    """MCP response message."""

    result: Optional[dict[str, Any]] = None
    error: Optional[dict[str, Any]] = None


class MCPNotification(BaseModel):
    """MCP notification message."""

    jsonrpc: str = "2.0"
    method: str
    params: Optional[dict[str, Any]] = None


class MCPServiceConfig(BaseModel):
    """MCP service configuration."""

    name: str
    description: str
    transport: TransportType
    endpoint: str
    timeout: int = 30
    retry_count: int = 3
    enabled: bool = True
    auth: Optional[dict[str, str]] = None
    headers: Optional[dict[str, str]] = None
    args: Optional[list[str]] = None  # For stdio transport
