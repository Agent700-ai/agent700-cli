# Organizations List

**Status:** Approved  
**Author:** a700cli  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-organizations-list.md

## Problem & Motivation

Users need to see which organizations they belong to (and their org IDs) before creating agents, since agent creation requires an `organizationId`. Today they have no CLI way to list organizations.

## Goals

- Add a command to list the current user's organizations via `GET /api/organizations/my`.
- Output shows org ID, name, and role (e.g., admin, consumer) in table or JSON format.
- Reuse existing auth and session; support token refresh on 401.

## Non-Goals

- Creating or managing organizations (create/add/remove user); only list.
- Changing agent creation flow in this spec.

## Background & Context

- API: `GET /api/organizations/my` returns array of `{ id, name, role }`.
- CLI already has `--list-agents`, `--format table|json`; follow same patterns for orgs.

## Requirements

### Functional

- **FR-1 (P1):** The CLI MUST support a command (e.g., `a700cli orgs list` or `a700cli --list-orgs`) that calls `GET /api/organizations/my` with the current session token.
- **FR-2 (P1):** Output MUST include organization id, name, and role for each org.
- **FR-2 (P2):** Output format MUST support table (default) and JSON (e.g., `--format json`).

### Non-Functional

- On 401, attempt token refresh and retry once (consistent with token refresh spec).

## Acceptance Criteria

- **AC1:** Given the user is authenticated, when they run the orgs list command, then they see a list of organizations with id, name, and role. Given/When/Then: Given valid token, When user runs `a700cli orgs list`, Then the client calls `GET /api/organizations/my` and displays results.
- **AC2:** Given `--format json`, output is valid JSON array of org objects. Given/When/Then: Given `--format json`, When orgs list runs, Then stdout is JSON only (no table).

## Test Plan

- **Unit:** Function that calls API and parses response returns list of orgs; empty list handled.
- **Integration:** Mock GET /api/organizations/my returns 200 with array; CLI invocation shows orgs or JSON.
