"""
Tests for app password commands (create/list/delete).
Spec: docs/specs/2026-01-29-app-passwords.md
"""
import pytest
from unittest.mock import patch, MagicMock

from tests.test_utils import MockConsole


def test_app_password_create_calls_api_and_displays_token():
    """app_password_create calls POST /api/auth/app-passwords and displays token."""
    from a700cli.__main__ import app_password_create

    console = MockConsole()
    with patch("a700cli.__main__.requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=201,
            json=lambda: {
                "id": "ap-1",
                "name": "CI",
                "token": "app_a7_secret123",
                "createdAt": "2026-01-29T00:00:00Z",
                "expiresAt": "2027-01-29T00:00:00Z",
                "isActive": True,
                "warning": "Store securely.",
            },
        )
        result = app_password_create(
            "token", "https://api.agent700.ai", "CI", console, session_manager=MagicMock()
        )
        assert result is True
        mock_post.assert_called_once()
        assert "/api/auth/app-passwords" in mock_post.call_args[0][0]
        assert mock_post.call_args[1]["json"] == {"name": "CI"}
        assert "app_a7_secret123" in str(console.output) or "Token:" in str(console.output)


def test_app_password_list_calls_api():
    """app_password_list calls GET /api/auth/app-passwords."""
    from a700cli.__main__ import app_password_list

    console = MagicMock()
    with patch("a700cli.__main__.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: [
                {"id": "ap-1", "name": "CI", "createdAt": "2026-01-29", "isActive": True},
            ],
        )
        with patch("a700cli.__main__.RICH_AVAILABLE", False):
            result = app_password_list(
                "token", "https://api.agent700.ai", console, session_manager=MagicMock()
            )
        assert result is True
        mock_get.assert_called_once()
        assert "/api/auth/app-passwords" in mock_get.call_args[0][0]


def test_app_password_delete_calls_api():
    """app_password_delete calls DELETE /api/auth/app-passwords/{id}."""
    from a700cli.__main__ import app_password_delete

    console = MagicMock()
    with patch("a700cli.__main__.requests.delete") as mock_del:
        mock_del.return_value = MagicMock(status_code=204)
        result = app_password_delete(
            "token", "https://api.agent700.ai", "ap-1", console, session_manager=MagicMock()
        )
        assert result is True
        mock_del.assert_called_once()
        assert "/api/auth/app-passwords/ap-1" in mock_del.call_args[0][0]
