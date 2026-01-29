# MCP Commands

**Status:** Approved  
**Author:** a700cli  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-mcp-commands.md

## Problem & Motivation

Users need to see which MCP servers are available and which tools an agent has access to, and to check MCP health. The API exposes list servers, agent tool definitions, and agent MCP health.

## Goals

- List MCP servers: `GET /api/mcp/servers` — show servers (id, name, status, tools count).
- List agent tools: `GET /api/agents/{agentId}/mcp/tool-definitions` — show tool names/descriptions for an agent.
- MCP health: `GET /api/agents/{agentId}/mcp/health` — show health status for agent's MCP.

## Non-Goals

- Adding/removing MCP servers from agents (API exists but out of scope for this spec).
- Calling MCP tools from CLI.

## Requirements

### Functional

- **FR-1 (P1):** CLI MUST support listing MCP servers (e.g., `a700cli --list-mcp-servers`). Calls GET /api/mcp/servers.
- **FR-2 (P1):** CLI MUST support listing MCP tools for an agent (e.g., `a700cli --mcp-tools <agentId>`). Calls GET /api/agents/{agentId}/mcp/tool-definitions.
- **FR-3 (P1):** CLI MUST support MCP health for an agent (e.g., `a700cli --mcp-health <agentId>`). Calls GET /api/agents/{agentId}/mcp/health.

## Acceptance Criteria

- **AC1:** Given valid token, when user runs list MCP servers, then they see servers with id, name, status. Given/When/Then: Given auth, When list MCP servers, Then GET /api/mcp/servers and display.
- **AC2:** Given valid token and agent ID, when user runs MCP tools, then they see tool definitions. Given/When/Then: Given auth and agentId, When MCP tools, Then GET .../mcp/tool-definitions and display.
- **AC3:** Given valid token and agent ID, when user runs MCP health, then they see health status. Given/When/Then: Given auth and agentId, When MCP health, Then GET .../mcp/health and display.

## Test Plan

- **Unit:** mcp_list, mcp_tools, mcp_health call correct endpoints and parse responses.
- **Integration:** Mock API; CLI invocations succeed.
