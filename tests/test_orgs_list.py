"""
Tests for organizations list (GET /api/organizations/my).
Spec: docs/specs/2026-01-29-organizations-list.md
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from tests.test_utils import MockConsole


def test_list_orgs_calls_api_and_returns_orgs():
    """list_orgs calls GET /api/organizations/my and displays results."""
    from a700cli.__main__ import list_orgs

    console = MockConsole()
    with patch("a700cli.__main__.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: [
                {"id": "org-1", "name": "Acme", "role": "admin"},
                {"id": "org-2", "name": "Beta", "role": "consumer"},
            ],
        )
        with patch("a700cli.__main__.RICH_AVAILABLE", False):
            list_orgs("token", "https://api.agent700.ai", console, output_format="table", session_manager=MagicMock())
        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert "/api/organizations/my" in call_url
        assert "Acme" in str(console.output) or "org-1" in str(console.output)


def test_list_orgs_json_format_outputs_valid_json():
    """With --format json, output is JSON array of orgs."""
    from a700cli.__main__ import list_orgs

    console = MagicMock()
    orgs = [{"id": "org-1", "name": "Acme", "role": "admin"}]
    with patch("a700cli.__main__.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: orgs)
        with patch("builtins.print") as mock_print:
            list_orgs("token", "https://api.agent700.ai", console, output_format="json", session_manager=MagicMock())
            mock_print.assert_called_once()
            printed = mock_print.call_args[0][0]
            parsed = json.loads(printed)
            assert parsed == orgs


def test_list_orgs_retries_on_401_after_refresh():
    """On 401, list_orgs attempts refresh and retries with new token."""
    from a700cli.__main__ import list_orgs

    console = MagicMock()
    session_manager = MagicMock()
    with patch("a700cli.__main__.requests.get") as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=401),
            MagicMock(status_code=200, json=lambda: [{"id": "o1", "name": "Org", "role": "admin"}]),
        ]
        with patch("a700cli.__main__.refresh_access_token") as mock_refresh:
            mock_refresh.return_value = "new_token"
            list_orgs("old_token", "https://api.agent700.ai", console, session_manager=session_manager)
            assert mock_refresh.call_count == 1
            assert mock_get.call_count == 2
            assert mock_get.call_args_list[1][1]["headers"]["Authorization"] == "Bearer new_token"
