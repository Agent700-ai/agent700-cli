# Document Parsing

**Status:** Approved  
**Author:** a700cli  
**Last Updated:** 2026-01-29  
**Spec Path:** /docs/specs/2026-01-29-document-parsing.md

## Problem & Motivation

Users want to parse documents (PDF, DOCX, etc.) and optionally feed the extracted text into chat. API: POST /api/helpers/parse-document (multipart/form-data with file).

## Goals

- Add a command to parse a document via POST /api/helpers/parse-document.
- Output extracted text to stdout or file; optional pipe into chat.

## Requirements

- **FR-1 (P1):** CLI MUST support parsing a document file (e.g., `a700cli --parse-document <file>`). Calls POST /api/helpers/parse-document with multipart file. Displays extracted text.
- **FR-2 (P2):** Optional: allow piping parsed output (e.g., `a700cli --parse-document doc.pdf | a700cli -i`). Out of scope for minimal: just --parse-document that prints text.

## Acceptance Criteria

- **AC1:** Given valid token and a file path, when user runs parse-document, then POST with file and display text. Given/When/Then: Given auth and file, When parse-document, Then API called and text printed.

## Test Plan

- **Unit:** parse_document calls POST with multipart file; handles response text.
