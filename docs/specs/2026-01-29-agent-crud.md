# Agent CRUD

**Status:** Approved  
**Author:** a700cli  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-agent-crud.md

## Problem & Motivation

Users need to create, update, delete, and inspect agents from the CLI without using the web UI. Agent creation requires an organization ID (available via `--list-orgs`).

## Goals

- Create agent: `POST /api/agents` with organizationId (required), name, masterPrompt, model, temperature, etc.
- Update agent: `PUT /api/agents/{agentId}` to create a new revision (same fields as create).
- Delete agent: `DELETE /api/agents/{agentId}`.
- Show agent: formatted display of current agent config (reuse GET /api/agents/{agentId} already used elsewhere).

## Non-Goals

- QA sheets, sharing, or workflow management in this spec; only core CRUD.

## Background & Context

- API create requires `organizationId`; optional fields include name, masterPrompt, model, temperature, maxTokens, enableMcp, mcpServerNames, etc.
- Update creates a new revision; same request body shape.
- CLI already calls GET /api/agents/{agentId} for config; show can reuse that and display in table/JSON.

## Requirements

### Functional

- **FR-1 (P1):** CLI MUST support creating an agent (e.g., `a700cli --create-agent` with `--org`, `--name`; optional `--model`, `--prompt`). Calls POST /api/agents.
- **FR-2 (P1):** CLI MUST support updating an agent by ID (e.g., `a700cli --update-agent <id>` with optional `--name`, `--temperature`, etc.). Calls PUT /api/agents/{agentId}.
- **FR-3 (P1):** CLI MUST support deleting an agent by ID (e.g., `a700cli --delete-agent <id>`). Calls DELETE /api/agents/{agentId}.
- **FR-4 (P1):** CLI MUST support showing agent details by ID (e.g., `a700cli --show-agent <id>`). Calls GET /api/agents/{agentId} and displays config.

## Acceptance Criteria

- **AC1:** Given valid token and org ID, when user runs create with --org and --name, then POST /api/agents is called and agent id is shown. Given/When/Then: Given auth and orgId, When create with required fields, Then agent is created and id displayed.
- **AC2:** Given valid token and agent ID, when user runs show, then GET /api/agents/{id} and formatted output. Given/When/Then: Given auth and agentId, When show, Then agent config is displayed.
- **AC3:** Given valid token and agent ID, when user runs delete, then DELETE /api/agents/{id} and success message.

## Test Plan

- **Unit:** agent_create/update/delete/show call correct endpoints with correct payloads.
- **Integration:** Mock API for create/update/delete/show; CLI invocations succeed.
