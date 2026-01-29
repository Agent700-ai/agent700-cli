"""
Tests for client-side tool execution (parse_tool_use_blocks, tool detection, McpExecutor, loop).
Spec: docs/specs/2026-01-29-tool-execution.md
"""
import pytest
from unittest.mock import patch, MagicMock

from a700cli.core.models import ToolCall
from a700cli.core.mcp import parse_tool_use_blocks, McpExecutor


# ---- parse_tool_use_blocks ----

@pytest.mark.unit
def test_parse_tool_use_blocks_valid_single():
    """AC-3: Valid <tool_use> block returns ToolCall with server, tool, arguments."""
    content = """Some text
<tool_use>
  <server>brave-search</server>
  <tool>search</tool>
  <arguments>{"query": "weather today"}</arguments>
</tool_use>
trailing"""
    result = parse_tool_use_blocks(content)
    assert len(result) == 1
    assert result[0].server == "brave-search"
    assert result[0].tool == "search"
    assert result[0].arguments == {"query": "weather today"}


@pytest.mark.unit
def test_parse_tool_use_blocks_multiple():
    """AC-3: Multiple <tool_use> blocks return list of ToolCall."""
    content = """
<tool_use><server>s1</server><tool>t1</tool><arguments>{}</arguments></tool_use>
<tool_use><server>s2</server><tool>t2</tool><arguments>{"k":"v"}</arguments></tool_use>
"""
    result = parse_tool_use_blocks(content)
    assert len(result) == 2
    assert result[0].server == "s1" and result[0].tool == "t1"
    assert result[1].server == "s2" and result[1].tool == "t2" and result[1].arguments == {"k": "v"}


@pytest.mark.unit
def test_parse_tool_use_blocks_malformed_skipped():
    """AC-3: Malformed XML block is skipped (no exception, empty or partial list)."""
    content = "<tool_use><server>only</tool_use>"  # missing </tool> and <arguments>
    result = parse_tool_use_blocks(content)
    assert result == []


@pytest.mark.unit
def test_parse_tool_use_blocks_empty_arguments():
    """Arguments optional; empty or missing becomes {}."""
    content = "<tool_use><server>s</server><tool>t</tool></tool_use>"
    result = parse_tool_use_blocks(content)
    assert len(result) == 1
    assert result[0].arguments == {}


@pytest.mark.unit
def test_parse_tool_use_blocks_no_block():
    """No <tool_use> in content returns empty list."""
    assert parse_tool_use_blocks("hello world") == []
    assert parse_tool_use_blocks("") == []


# ---- Tool detection (client state) ----

@pytest.mark.unit
def test_tool_detection_finish_reason_tool_calls():
    """AC-1: finish_reason='tool_calls' -> tool_call_pending True."""
    from a700cli.core.client import WebSocketClient
    import re
    pat = re.compile(r'<tool_use>[\s\S]*?</tool_use>', re.IGNORECASE)
    tool_pending, resp_complete = WebSocketClient._tool_detection('tool_calls', 'any content', pat)
    assert tool_pending is True
    assert resp_complete is False


@pytest.mark.unit
def test_tool_detection_finish_reason_end_turn_with_tool_use():
    """AC-2: finish_reason='end_turn' and content has <tool_use> -> tool_call_pending True."""
    from a700cli.core.client import WebSocketClient
    import re
    pat = re.compile(r'<tool_use>[\s\S]*?</tool_use>', re.IGNORECASE)
    content = "Here is <tool_use><server>brave</server><tool>search</tool><arguments>{}</arguments></tool_use>"
    tool_pending, resp_complete = WebSocketClient._tool_detection('end_turn', content, pat)
    assert tool_pending is True
    assert resp_complete is False


@pytest.mark.unit
def test_tool_detection_finish_reason_end_turn_no_tool_use():
    """AC-2: finish_reason='end_turn' and no <tool_use> -> response_complete True."""
    from a700cli.core.client import WebSocketClient
    import re
    pat = re.compile(r'<tool_use>[\s\S]*?</tool_use>', re.IGNORECASE)
    tool_pending, resp_complete = WebSocketClient._tool_detection('end_turn', 'Just text.', pat)
    assert tool_pending is False
    assert resp_complete is True


# ---- McpExecutor ----

@pytest.mark.unit
def test_mcp_executor_execute_calls_remote():
    """McpExecutor.execute routes to remote and returns result dict."""
    with patch('requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"result": "ok"})
        executor = McpExecutor("https://api.agent700.ai", "token", "agent-123", {})
        tc = ToolCall(server="brave-search", tool="search", arguments={"query": "x"})
        out = executor.execute(tc)
        assert out == {"result": "ok"}
        mock_post.assert_called_once()
        call_payload = mock_post.call_args[1]["json"]
        assert call_payload["server"] == "brave-search" and call_payload["tool"] == "search"


@pytest.mark.unit
def test_mcp_executor_returns_error_on_http_error():
    """McpExecutor returns error dict on non-200."""
    with patch('requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=500, text="Server error")
        executor = McpExecutor("https://api.agent700.ai", "token", "agent-123", {})
        tc = ToolCall(server="s", tool="t", arguments={})
        out = executor.execute(tc)
        assert "error" in out
        assert "500" in out["error"]
