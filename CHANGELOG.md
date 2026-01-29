# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-01-29

### Changed
- Updated author metadata (Eric Marshall, hello@agent700.ai)
- Updated project URLs to point to agent700.ai
- Replaced examples with customer-friendly, copy-paste CLI examples
- Added `rich` dependency to requirements.txt for consistency with pyproject.toml

### Added
- MIT LICENSE file
- CHANGELOG.md for version tracking
- Quick Start guide in README for faster onboarding
- Troubleshooting / FAQ section in README to reduce support calls
- Support contact information (hello@agent700.ai)

### Removed
- Internal development files (SPEC documents, tools/, applescript_mcp.py)
- Internal documentation (PRODUCT_DESCRIPTION.md, Agent700API.md)
- Broken example scripts that referenced missing modules

### Fixed
- Examples now work out of the box with no missing imports
- .gitignore now excludes .cursor/ directory
