# Billing Usage

**Status:** Approved  
**Author:** a700cli  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-billing-usage.md

## Problem & Motivation

Users need to see usage and cost from the CLI. The API exposes GET /api/billing/user with optional start_date and end_date query params.

## Goals

- Add a command to get user billing/usage via GET /api/billing/user.
- Support optional date range (--start-date, --end-date).
- Display total cost and billing logs (table or JSON).

## Requirements

- **FR-1 (P1):** CLI MUST support querying billing (e.g., `a700cli --billing-usage` with optional `--start-date`, `--end-date`). Calls GET /api/billing/user.
- **FR-2 (P2):** Output MUST support table (default) and JSON (--format json).

## Acceptance Criteria

- **AC1:** Given valid token, when user runs billing usage with optional dates, then GET /api/billing/user is called and results displayed. Given/When/Then: Given auth, When billing usage, Then display total cost and logs.

## Test Plan

- **Unit:** billing_usage calls correct endpoint with query params; parses response.
