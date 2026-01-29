# Client-Side MCP Tool Execution

**Status:** Draft  
**Author:** AI Assistant  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-tool-execution.md

---

## Problem & Motivation

**What problem are we solving?**

The chat API sometimes returns `finish_reason: 'end_turn'` even when the response includes a `<tool_use>` block (e.g., brave-search). The client currently only runs tools when `finish_reason === 'tool_calls'`, so in those cases the tool is never executed. Users see the agent "thinking" and a tool card, but no actual answer.

**Why does it matter now?**

This is a critical usability bug. When tools don't execute, users get incomplete responses and the agent appears broken. The fix requires client-side detection and execution of tools as a fallback when the API incorrectly signals `end_turn` instead of `tool_calls`.

**Who is affected?**

All CLI users who interact with agents that have MCP tools enabled.

---

## Goals

- Detect tool calls when `finish_reason === 'tool_calls'` (primary path)
- Detect tool calls when `finish_reason` is `'end_turn'` or `'STOP'` but content contains `<tool_use>` block (fallback)
- Parse `<tool_use>` blocks to extract server name, tool name, and arguments
- Execute tools client-side via local MCP (stdio subprocess) or remote MCP (API call)
- Implement tool loop: append assistant message + tool result to conversation, continue until final response

---

## Non-Goals

- Fixing the API to always return `finish_reason: 'tool_calls'` (long-term API fix, out of scope)
- Adding new MCP servers to the CLI configuration
- Modifying the HTTP fallback path (WebSocket streaming only for now)
- UI/UX changes beyond basic console status output during tool execution

---

## Background & Context

### Current Behavior

In [`a700cli/core/client.py`](../../a700cli/core/client.py), the `on_chat_response` handler (line 89) only marks response complete on `finish_reason == 'stop'`:

```python
if finish_reason == 'stop':
    self.response_complete = True
    self.response_event.set()
```

There is no handling for:
- `finish_reason == 'tool_calls'`
- `<tool_use>` blocks in streamed content

### Existing MCP Integration

- Agent config includes `enableMcp` and `mcpServerNames` (lines 220-221 of `__main__.py`)
- Event handler `mcp_tool_complete_in_content` exists but receives server-side results (not applicable here)
- CLI has commands `--list-mcp-servers`, `--mcp-tools`, `--mcp-health` for discovery

### Tool Use Block Format

Based on the user's description, the API streams XML-like blocks:

```xml
<tool_use>
  <server>brave-search</server>
  <tool>search</tool>
  <arguments>{"query": "weather today"}</arguments>
</tool_use>
```

[NEEDS CLARIFICATION: Confirm exact XML schema - are there additional fields like `id` or `call_id`?]

---

## Requirements

### Functional Requirements

| ID | Priority | Requirement | Justification |
|----|----------|-------------|---------------|
| FR-001 | P1 | Client MUST detect tool calls when `finish_reason === 'tool_calls'` | Primary detection path |
| FR-002 | P1 | Client MUST detect tool calls when `finish_reason` is `'end_turn'` or `'STOP'` AND content matches `/<tool_use>[\s\S]*?<\/tool_use>/i` | Fallback for API bug |
| FR-003 | P1 | Client MUST parse `<tool_use>` blocks to extract server, tool, and arguments | Required for execution |
| FR-004 | P1 | Client MUST execute tools via remote MCP API (`POST /api/mcp/execute` or equivalent) | Remote tool execution |
| FR-005 | P2 | Client SHOULD support local MCP execution via stdio subprocess | Local tool execution |
| FR-006 | P1 | Client MUST append tool results to conversation and continue loop until final response | Complete the agentic loop |
| FR-007 | P2 | Client SHOULD display tool execution status to console | User feedback |

### Non-Functional Requirements

- **Performance:** Tool execution timeout of 30 seconds (configurable)
- **Reliability:** Graceful error handling for malformed XML, network failures, missing servers
- **Observability:** Log tool calls and results when verbose mode enabled

---

## Design Overview

### High-Level Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    send_message() loop                       │
├─────────────────────────────────────────────────────────────┤
│  1. Send message via WebSocket                              │
│  2. Stream response, accumulate in full_response            │
│  3. On finish_reason received:                              │
│     - 'tool_calls' → set tool_call_pending = True           │
│     - 'end_turn'/'STOP' + <tool_use> → tool_call_pending    │
│     - 'stop' (no tools) → response_complete = True          │
│  4. If tool_call_pending:                                   │
│     a. Parse <tool_use> blocks → List[ToolCall]             │
│     b. For each ToolCall: execute via McpExecutor           │
│     c. Append assistant msg + tool results to messages      │
│     d. Reset and continue loop (goto 1)                     │
│  5. If response_complete: return AgentResponse              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **ToolCall dataclass** (`a700cli/core/models.py`)
   ```python
   @dataclass
   class ToolCall:
       server: str
       tool: str
       arguments: Dict[str, Any]
       id: Optional[str] = None
   ```

2. **parse_tool_use_blocks()** function
   - Regex to find all `<tool_use>...</tool_use>` blocks
   - XML parsing to extract server, tool, arguments
   - Returns `List[ToolCall]`

3. **McpExecutor class** (`a700cli/core/mcp.py`)
   - `execute(tool_call: ToolCall) -> dict` - route to local or remote
   - `_call_remote_mcp()` - POST to API endpoint
   - `_call_local_mcp()` - stdio subprocess (P2, future)

4. **Updated WebSocketClient** (`a700cli/core/client.py`)
   - New state: `tool_call_pending: bool`
   - Updated `on_chat_response` handler for tool detection
   - Updated `send_message` with tool execution loop

### Trade-offs

- **Remote-first:** Start with remote MCP execution only (P1), defer local stdio (P2)
- **Regex + XML parsing:** Hybrid approach for robustness; pure regex may miss edge cases
- **Single-threaded execution:** Execute tools sequentially for simplicity

---

## Risks & Open Questions

| Risk/Question | Status | Notes |
|---------------|--------|-------|
| Exact `<tool_use>` XML schema | [NEEDS CLARIFICATION] | Does it include `id` field? Are there variants? |
| Remote MCP API endpoint | [NEEDS CLARIFICATION] | Is it `POST /api/mcp/execute`? What's the request/response format? |
| Local vs remote server identification | [NEEDS CLARIFICATION] | How to determine if a server is local (stdio) vs remote (API)? |
| Multiple tools in one response | Low risk | Design handles `List[ToolCall]` |
| Malformed XML | Low risk | Graceful error handling with fallback |

---

## Acceptance Criteria

### Story 1: Tool Detection via finish_reason

- **Given** the API returns `finish_reason: 'tool_calls'`, **When** the response is received, **Then** the client sets `tool_call_pending = True` and proceeds to tool execution.

### Story 2: Fallback Tool Detection via Content

- **Given** the API returns `finish_reason: 'end_turn'` AND the content contains `<tool_use>...</tool_use>`, **When** the response is received, **Then** the client sets `tool_call_pending = True` (fallback detection).
- **Given** the API returns `finish_reason: 'end_turn'` AND the content does NOT contain `<tool_use>`, **When** the response is received, **Then** the client sets `response_complete = True` (no tools).

### Story 3: Tool Parsing

- **Given** content contains a valid `<tool_use>` block, **When** parsed, **Then** a `ToolCall` is returned with correct `server`, `tool`, and `arguments`.
- **Given** content contains multiple `<tool_use>` blocks, **When** parsed, **Then** a list of `ToolCall` objects is returned.
- **Given** content contains malformed XML, **When** parsed, **Then** an error is logged and the block is skipped.

### Story 4: Tool Execution Loop

- **Given** `tool_call_pending = True`, **When** the loop continues, **Then** tools are executed via McpExecutor and results appended to messages.
- **Given** tool execution returns a result, **When** appended to messages, **Then** the next API request includes the tool result.
- **Given** final response (no tools), **When** received, **Then** `AgentResponse` is returned to the user.

---

## Success Criteria

- Tools execute correctly when API returns `finish_reason: 'tool_calls'`
- Tools execute correctly when API incorrectly returns `finish_reason: 'end_turn'` but content has `<tool_use>`
- User sees tool execution status in console
- No regression in existing chat functionality

---

## Test Plan

| Type | Coverage |
|------|----------|
| **Unit** | `parse_tool_use_blocks()` - valid XML, multiple blocks, malformed XML |
| **Unit** | Tool detection logic - `finish_reason` variants + content fallback |
| **Unit** | `McpExecutor` - mock API responses, error handling |
| **Integration** | Full tool loop with mocked WebSocket and API |
| **Integration** | Fallback to HTTP when WebSocket fails (existing behavior preserved) |
