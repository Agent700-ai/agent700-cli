# App Passwords

**Status:** Approved  
**Author:** a700cli  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-app-passwords.md

## Problem & Motivation

CI/CD and scripts need to authenticate without storing user passwords. App passwords provide SOC2-compliant tokens that can be created, listed, and deleted via API. The CLI should expose these operations.

## Goals

- Create app password: `POST /api/auth/app-passwords` with name (and optional permissions); display token once (API returns token only on creation).
- List app passwords: `GET /api/auth/app-passwords`; show id, name, createdAt, isActive (no token).
- Delete app password: `DELETE /api/auth/app-passwords/{passwordId}`.
- Login with app password: `POST /api/auth/app-login` so users can authenticate with email + app password instead of account password (optional; can be separate flag or env).

## Non-Goals

- Editing app password permissions after creation (API may not support; out of scope).
- Storing app password token in .env by default (user decides).

## Background & Context

- API: Create returns `{ id, name, token, createdAt, expiresAt, isActive, warning }`; token shown only once.
- List returns array of app passwords (no token).
- Auth: `POST /api/auth/app-login` with email + app password token for programmatic login.

## Requirements

### Functional

- **FR-1 (P1):** CLI MUST support creating an app password (e.g., `a700cli app-password create "My Client"`) using current session token; display the new token and warning.
- **FR-2 (P1):** CLI MUST support listing app passwords (e.g., `a700cli app-password list`); output id, name, createdAt, isActive.
- **FR-3 (P1):** CLI MUST support deleting an app password by id (e.g., `a700cli app-password delete <id>`).
- **FR-4 (P2):** CLI SHOULD support login with app password (e.g., env APP_PASSWORD or flag) so scripts can use `POST /api/auth/app-login` instead of password login.

## Acceptance Criteria

- **AC1:** Given authenticated user, when they run app-password create with a name, then the API is called and the new token is printed once. Given/When/Then: Given valid token, When user runs create with name, Then POST /api/auth/app-passwords and display token.
- **AC2:** Given authenticated user, when they run app-password list, then they see a list of app passwords (no tokens). Given/When/Then: Given valid token, When user runs list, Then GET /api/auth/app-passwords and display table.
- **AC3:** Given authenticated user, when they run app-password delete <id>, then the app password is deleted. Given/When/Then: Given valid token, When user runs delete with id, Then DELETE /api/auth/app-passwords/{id}.

## Test Plan

- **Unit:** Functions for create/list/delete call correct endpoints with correct payloads; create displays token.
- **Integration:** Mock API for create/list/delete; CLI invocations succeed and output as expected.
