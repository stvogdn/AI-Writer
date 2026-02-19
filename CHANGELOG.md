# Changelog

All notable changes to AI Writer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-02-19

### Added
- Complete project restructuring into proper Python package
- Configuration management system with JSON persistence
- Comprehensive test suite with pytest
- Development tooling (black, ruff, mypy, pre-commit)
- Modular architecture with separated concerns:
  - Core business logic (Ollama client, file management)
  - UI components (main window, themes)
  - Configuration management
- Type hints throughout codebase
- Documentation (user guide, development guide)
- Build and development scripts
- Proper packaging with entry points

### Changed
- Migrated from monolithic single-file to modular package structure
- Updated Python requirement to 3.11+
- Modernized packaging with pyproject.toml
- Improved error handling and user feedback
- Enhanced code organization and maintainability

### Fixed
- Invalid Python version requirement (was 3.14, now 3.11+)
- Redundant dependency management (removed requirements.txt)
- Configuration hardcoding (now uses centralized settings)

### Technical Improvements
- Separation of UI and business logic
- Background thread management for API calls
- Proper resource cleanup and memory management
- Comprehensive test coverage
- Code quality enforcement with linting and formatting
- Git hooks for automated code quality checks