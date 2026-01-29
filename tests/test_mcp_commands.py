"""
Tests for MCP commands (list servers, tools, health).
Spec: docs/specs/2026-01-29-mcp-commands.md
"""
import pytest
from unittest.mock import patch, MagicMock


def test_mcp_list_servers_calls_api():
    """mcp_list_servers calls GET /api/mcp/servers."""
    from a700cli.__main__ import mcp_list_servers

    console = MagicMock()
    with patch("a700cli.__main__.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"servers": [{"id": "s1", "name": "my-mcp", "status": "connected"}]},
        )
        with patch("a700cli.__main__.RICH_AVAILABLE", False):
            result = mcp_list_servers(
                "token", "https://api.agent700.ai", console,
                session_manager=MagicMock(),
            )
        assert result is True
        mock_get.assert_called_once()
        assert "/api/mcp/servers" in mock_get.call_args[0][0]


def test_mcp_tools_calls_api():
    """mcp_tools calls GET /api/agents/{id}/mcp/tool-definitions."""
    from a700cli.__main__ import mcp_tools

    console = MagicMock()
    with patch("a700cli.__main__.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"tools": [{"name": "get_weather", "description": "Get weather"}]},
        )
        result = mcp_tools(
            "token", "https://api.agent700.ai", "agent-123", console,
            session_manager=MagicMock(),
        )
        assert result is True
        mock_get.assert_called_once()
        assert "/api/agents/agent-123/mcp/tool-definitions" in mock_get.call_args[0][0]


def test_mcp_health_calls_api():
    """mcp_health calls GET /api/agents/{id}/mcp/health."""
    from a700cli.__main__ import mcp_health

    console = MagicMock()
    with patch("a700cli.__main__.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"status": "ok"})
        result = mcp_health(
            "token", "https://api.agent700.ai", "agent-123", console,
            session_manager=MagicMock(),
        )
        assert result is True
        mock_get.assert_called_once()
        assert "/api/agents/agent-123/mcp/health" in mock_get.call_args[0][0]
