"""
Tests for agent CRUD (create/update/delete/show).
Spec: docs/specs/2026-01-29-agent-crud.md
"""
import pytest
from unittest.mock import patch, MagicMock

from tests.test_utils import MockConsole


def test_agent_create_calls_post_api():
    """agent_create calls POST /api/agents with org and name."""
    from a700cli.__main__ import agent_create

    console = MockConsole()
    with patch("a700cli.__main__.requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"status": "success", "agent": {"id": "agent-123", "name": "Test"}},
        )
        result = agent_create(
            "token", "https://api.agent700.ai", "org-1", "Test Agent", console,
            session_manager=MagicMock(),
        )
        assert result is True
        mock_post.assert_called_once()
        assert "/api/agents" in mock_post.call_args[0][0]
        assert mock_post.call_args[1]["json"]["organizationId"] == "org-1"
        assert mock_post.call_args[1]["json"]["name"] == "Test Agent"


def test_agent_update_calls_put_api():
    """agent_update calls PUT /api/agents/{id} with payload."""
    from a700cli.__main__ import agent_update

    console = MagicMock()
    with patch("a700cli.__main__.requests.put") as mock_put:
        mock_put.return_value = MagicMock(status_code=200, json=lambda: {"status": "success"})
        result = agent_update(
            "token", "https://api.agent700.ai", "agent-123", console,
            name="Updated Name",
            session_manager=MagicMock(),
        )
        assert result is True
        mock_put.assert_called_once()
        assert "/api/agents/agent-123" in mock_put.call_args[0][0]
        assert mock_put.call_args[1]["json"]["name"] == "Updated Name"


def test_agent_delete_calls_delete_api():
    """agent_delete calls DELETE /api/agents/{id}."""
    from a700cli.__main__ import agent_delete

    console = MagicMock()
    with patch("a700cli.__main__.requests.delete") as mock_del:
        mock_del.return_value = MagicMock(status_code=204)
        result = agent_delete(
            "token", "https://api.agent700.ai", "agent-123", console,
            session_manager=MagicMock(),
        )
        assert result is True
        mock_del.assert_called_once()
        assert "/api/agents/agent-123" in mock_del.call_args[0][0]


def test_agent_show_uses_get_agent_config():
    """agent_show uses get_agent_config and displays details."""
    from a700cli.__main__ import agent_show

    console = MagicMock()
    with patch("a700cli.__main__.get_agent_config") as mock_get:
        mock_get.return_value = {
            "agentName": "My Agent",
            "model": "gpt-4o",
            "temperature": 0.7,
            "maxTokens": 4000,
            "agentRevisionId": 1,
        }
        result = agent_show(
            "token", "https://api.agent700.ai", "agent-123", console,
            session_manager=MagicMock(),
        )
        assert result is True
        mock_get.assert_called_once()
        assert mock_get.call_args[0][1] == "agent-123"
