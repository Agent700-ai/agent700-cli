# Context Library

**Status:** Approved  
**Author:** a700cli  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-context-library.md

## Problem & Motivation

Users need to list, get, and set context library (alignment) data from the CLI. API: GET /api/alignment-data, POST /api/alignment-data, GET /api/alignment-data/by-key/{key}, DELETE /api/alignment-data/{key}.

## Goals

- List context library entries: GET /api/alignment-data.
- Get by key: GET /api/alignment-data/by-key/{key}.
- Set (create/update): POST /api/alignment-data with key and value.
- Delete: DELETE /api/alignment-data/{key}.

## Requirements

- **FR-1 (P1):** CLI MUST support listing context library (e.g., `a700cli --context-library list`). Calls GET /api/alignment-data.
- **FR-2 (P1):** CLI MUST support getting value by key (e.g., `a700cli --context-library get <key>`). Calls GET /api/alignment-data/by-key/{key}.
- **FR-3 (P1):** CLI MUST support setting key-value (e.g., `a700cli --context-library set <key> <value>`). Calls POST /api/alignment-data.
- **FR-4 (P2):** CLI SHOULD support deleting by key (e.g., `a700cli --context-library delete <key>`). Calls DELETE /api/alignment-data/{key}.

## Acceptance Criteria

- **AC1:** Given valid token, when user runs context-library list, then GET /api/alignment-data and display. Given/When/Then: Given auth, When list, Then display keys/values.
- **AC2:** Given valid token and key, when user runs get, then GET by-key and display value. Given/When/Then: Given auth and key, When get, Then display value.
- **AC3:** Given valid token, key, and value, when user runs set, then POST and success. Given/When/Then: Given auth, key, value, When set, Then entry created/updated.

## Test Plan

- **Unit:** context_library_list, get, set, delete call correct endpoints.
