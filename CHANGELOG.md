# Changelog

All notable changes to AI Writer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-19

### Added

- **Streaming Support**: Real-time text generation
  - AI responses now appear incrementally in the editor as they are generated
  - Improved perceived responsiveness and user experience
  - Real-time status bar updates during the generation process

### Fixed

- **Syntax Errors**: Fixed critical syntax errors in `prompt_manager.py` and `prompt_selector.py` that prevented the application from launching.
- **Test Suite Stability**: Resolved multiple issues in the test suite
  - Fixed `TypeError` in main window tests related to mocking settings
  - Fixed `AttributeError` in Ollama client tests by correctly mocking signal objects
  - Improved `FileManager` test reliability and cleanup

### Changed

- **Consolidated Documentation**: Cleaned up `README.md` to remove redundant sections and improve clarity.
- **Improved FileManager**: Refactored internal methods for better maintainability and test compatibility.

## [0.2.0] - 2026-02-19

### Added

- **Prompt Management System**: Store and manage multiple prompt templates
  - Create, edit, delete, and organize custom prompt templates
  - Model-specific prompt filtering (prompts can target specific language models or "all")
  - Prompt selection UI integrated into main window sidebar
  - Default prompt templates included for common use cases
  - Persistent storage of prompts in settings

- **Spell Checking**: Basic spell checking functionality with PyEnchant
  - Real-time spell checking with visual highlighting of misspelled words
  - Background threading to avoid UI blocking
  - Configurable spell check language selection
  - Enable/disable toggle in sidebar
  - Graceful fallback when PyEnchant is not available

- **Splash Screen**: Professional startup experience
  - Animated loading screen with AI Writer branding
  - Progress indication during application initialization
  - Clean, modern design with gradient background

- **Enhanced File Management**: Remember last save location
  - Automatically remembers the folder where files were last saved
  - Uses remembered location as default for subsequent saves
  - Improves workflow efficiency

### Enhanced

- **Settings System**: Extended configuration management
  - Added spell check settings (language, enable/disable, colors)
  - Added prompt management settings with full serialization
  - Enhanced settings persistence with backward compatibility

- **User Interface Improvements**:
  - Added Ollama URL configuration field in sidebar
  - Integrated prompt selector with model-aware filtering  
  - Added spell check controls when PyEnchant is available
  - Improved sidebar organization with better spacing

- **Text Generation Workflow**:
  - Integrated prompt templates with text generation
  - Automatic prompt template application based on selection
  - Model-specific prompt filtering for better organization

### Technical Improvements

- Added PyEnchant dependency for spell checking
- Enhanced settings serialization with complex data structures
- Improved error handling and user feedback
- Background threading for spell checking operations
- Modular UI components for better maintainability

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
