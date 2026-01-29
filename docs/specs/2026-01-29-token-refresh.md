# Token Refresh

**Status:** Approved  
**Author:** a700cli  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-token-refresh.md

## Problem & Motivation

When the access token expires, the CLI fails with 401 and the user must re-enter credentials. Long-running or scripted use benefits from automatically refreshing the token using the refresh token so that re-authentication is not required.

## Goals

- On 401 from any API call, attempt to refresh the access token via `POST /api/auth/refresh` before failing.
- Persist refresh token (or cookies) from login so refresh can be performed without user interaction.
- After successful refresh, retry the original request with the new access token.
- Keep session persistence compatible with existing `.agent700_session.dat` format where possible.

## Non-Goals

- Changing the login flow UI.
- Supporting refresh when the API does not return a refresh token (e.g., app-login); in that case 401 continues to require re-login.

## Background & Context

- `SessionManager` in `a700cli/core/session.py` persists `access_token` and `email` via pickle.
- The Agent700 API refresh endpoint uses an httpOnly refreshToken cookie; login response may set `Set-Cookie` with `refreshToken`.
- All API calls in `__main__.py` use `requests` with `Authorization: Bearer {access_token}`.

## Requirements

### Functional

- **FR-1 (P1):** When an API request returns 401, the client MUST attempt token refresh (e.g., call `POST /api/auth/refresh`) with stored session data (cookies or refresh token) before surfacing 401 to the user.
- **FR-2 (P1):** If refresh succeeds, the client MUST update the stored access token and retry the original request once.
- **FR-3 (P1):** If refresh fails or is not possible (no refresh data), the client MUST surface 401/authentication error and not retry indefinitely.
- **FR-4 (P2):** Login flow MUST use a persistent session (e.g., `requests.Session`) and store cookies so that refresh can send the same cookies on `POST /api/auth/refresh`.

### Non-Functional

- Security: Do not log or print refresh tokens or cookies.
- Backward compatibility: Existing sessions without refresh data continue to work until token expires; then user re-authenticates as today.

## Acceptance Criteria

- **AC1:** Given a valid session with refresh token/cookies, when a request returns 401, the client calls refresh and retries. Given/When/Then: Given stored session has refresh capability, When any API call returns 401, Then refresh is attempted and on success the original request is retried with the new token.
- **AC2:** Given refresh fails (e.g., 401 from refresh), the user sees an authentication error and is not stuck in a retry loop. Given/When/Then: Given refresh returns 401, When the client handles the response, Then the user is prompted or informed to re-authenticate and no infinite retry occurs.

## Test Plan

- **Unit:** SessionManager stores and loads cookie/session data used for refresh; refresh helper returns new token or None.
- **Integration:** Mock API: first request 401, refresh 200 with new token, retry succeeds; or refresh 401 → error path.
