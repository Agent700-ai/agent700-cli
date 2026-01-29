"""
MCP tool execution: parse <tool_use> blocks and execute tools (remote API).
Spec: docs/specs/2026-01-29-tool-execution.md
"""
import re
import json
import logging
from typing import List, Dict, Any

from .models import ToolCall

logger = logging.getLogger(__name__)

TOOL_USE_PATTERN = re.compile(r'<tool_use>[\s\S]*?</tool_use>', re.IGNORECASE)


def parse_tool_use_blocks(content: str) -> List[ToolCall]:
    """Parse all <tool_use> blocks from content; return list of ToolCall.
    Malformed blocks are skipped (error logged).
    """
    results: List[ToolCall] = []
    for block in TOOL_USE_PATTERN.findall(content):
        try:
            tc = _parse_one_block(block)
            if tc:
                results.append(tc)
        except Exception as e:
            logger.warning("Skip malformed <tool_use> block: %s", e)
    return results


def _parse_one_block(block: str) -> ToolCall:
    """Extract server, tool, arguments from one <tool_use>...</tool_use> block."""
    server = _extract_tag(block, 'server')
    tool = _extract_tag(block, 'tool')
    args_raw = _extract_tag(block, 'arguments')
    call_id = _extract_tag(block, 'id') or None
    if not server or not tool:
        raise ValueError("Missing server or tool in <tool_use> block")
    arguments: Dict[str, Any] = {}
    if args_raw:
        try:
            arguments = json.loads(args_raw.strip())
            if not isinstance(arguments, dict):
                arguments = {"raw": args_raw}
        except json.JSONDecodeError:
            arguments = {"raw": args_raw}
    return ToolCall(server=server, tool=tool, arguments=arguments, id=call_id)


def _extract_tag(block: str, tag: str) -> str:
    """Extract text inside <tag>...</tag> (first occurrence)."""
    pat = re.compile(r'<' + re.escape(tag) + r'>([\s\S]*?)</' + re.escape(tag) + r'>', re.IGNORECASE)
    m = pat.search(block)
    return m.group(1).strip() if m else ""


class McpExecutor:
    """Execute MCP tools via remote API. Local (stdio) is P2/future."""

    def __init__(self, api_base_url: str, access_token: str, agent_uuid: str, agent_config: Dict[str, Any]) -> None:
        self.api_base_url = api_base_url.rstrip('/')
        if not self.api_base_url.endswith('/api'):
            self.api_base_url = self.api_base_url + '/api' if not self.api_base_url.endswith('/') else self.api_base_url + 'api'
        self.access_token = access_token
        self.agent_uuid = agent_uuid
        self.agent_config = agent_config
        self.timeout = 30

    def execute(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute one tool call via remote MCP API. Returns result dict or error dict."""
        return self._call_remote_mcp(tool_call)

    def _call_remote_mcp(self, tool_call: ToolCall) -> Dict[str, Any]:
        """POST to API to execute tool. Spec assumes POST /api/mcp/execute or equivalent."""
        try:
            import requests as _requests
            url = f"{self.api_base_url}/mcp/execute"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "agentId": self.agent_uuid,
                "server": tool_call.server,
                "tool": tool_call.tool,
                "arguments": tool_call.arguments,
            }
            if tool_call.id:
                payload["toolCallId"] = tool_call.id
            resp = _requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                return data if isinstance(data, dict) else {"result": data}
            return {"error": f"HTTP {resp.status_code}", "detail": resp.text}
        except Exception as e:
            logger.exception("Remote MCP execution failed")
            return {"error": str(e)}
