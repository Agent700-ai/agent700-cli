# QA / Ratings

**Status:** Approved  
**Author:** a700cli  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-qa-ratings.md

## Problem & Motivation

Users need to submit conversation ratings and export ratings CSV from the CLI. API: POST /api/ratings, GET /api/ratings-export, GET /api/agents/{agentId}/qa-sheets.

## Goals

- Submit rating: POST /api/ratings with agentId, agentRevisionId, rating, optional notes.
- Export ratings: GET /api/ratings-export (CSV download).
- List QA sheets for agent: GET /api/agents/{agentId}/qa-sheets.

## Requirements

- **FR-1 (P1):** CLI MUST support submitting a rating (e.g., `a700cli --rate` with --agent-id, --revision-id, --score, optional --notes). Calls POST /api/ratings.
- **FR-2 (P1):** CLI MUST support exporting ratings CSV (e.g., `a700cli --export-ratings`). Calls GET /api/ratings-export and writes to stdout or file.
- **FR-3 (P2):** CLI SHOULD support listing QA sheets for an agent (e.g., `a700cli --qa-sheets <agentId>`). Calls GET /api/agents/{agentId}/qa-sheets.

## Acceptance Criteria

- **AC1:** Given valid token, when user runs rate with required fields, then POST /api/ratings and success message. Given/When/Then: Given auth, When rate with agentId, revisionId, score, Then rating created.
- **AC2:** Given valid token, when user runs export-ratings, then CSV is output. Given/When/Then: Given auth, When export-ratings, Then GET /api/ratings-export and output CSV.

## Test Plan

- **Unit:** rate, export_ratings, qa_sheets_list call correct endpoints.
