# Development Guide for AI Writer

## Development Environment Setup

### Prerequisites
- Python 3.11+ 
- Git
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- Ollama (for runtime functionality)

### Setting Up

1. Clone the repository:
   ```bash
   git clone https://github.com/Laszlobeer/AI-Writer.git
   cd AI-Writer
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Set up development environment with uv:
   ```bash
   uv sync --dev
   ```

## Project Structure

```
ai-writer/
├── src/ai_writer/          # Main application package
│   ├── config/             # Configuration management
│   ├── core/               # Core business logic
│   ├── ui/                 # User interface components
│   │   ├── components/     # Reusable UI components
│   │   └── styles/         # Theme stylesheets
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
├── scripts/                # Build and development scripts
└── assets/                 # Static assets
```

## Development Workflow

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Linting and code analysis
- **MyPy**: Type checking
- **Pytest**: Testing framework
- **Pre-commit**: Git hooks for automated checks

### Running Tests

```bash
uv run pytest tests/                          # Run all tests
uv run pytest tests/test_config.py           # Run specific test file
uv run pytest tests/ -v                      # Verbose output
uv run pytest tests/ --cov=ai_writer         # With coverage report
```

### Code Formatting

```bash
uv run black src/ tests/ scripts/            # Format all code
uv run ruff check src/ tests/ --fix          # Lint and auto-fix
uv run mypy src/ai_writer/                   # Type checking
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`. To run manually:

```bash
uv run pre-commit run --all-files
```

## Building and Distribution

### Development Installation

Install in development mode (allows editing source files):

```bash
uv sync --dev
```

### Building Packages

```bash
uv run python scripts/build.py
```

This will:
1. Run all tests
2. Perform code quality checks  
3. Build wheel and source distributions

### Running the Application

After installation:

```bash
uv run ai-writer                             # Using entry point
uv run python -m ai_writer.main              # Direct module execution
```

## Architecture

### Configuration Management

The application uses a layered configuration system:

- `ai_writer.config.settings.Settings`: Main configuration class
- Settings are loaded from JSON files in user config directory
- Runtime settings can be saved back to config files
- Default values are provided for all settings

### Core Components

- `OllamaClient`: High-level interface to Ollama API
- `OllamaWorker`: Background thread for async operations
- `FileManager`: Handles document saving/loading
- `MainWindow`: Main UI controller

### UI Architecture

- Separation of UI components into logical modules
- Centralized theme management
- Signal-slot pattern for component communication
- Proper resource cleanup and memory management

## Testing Strategy

### Unit Tests

- Test individual components in isolation
- Mock external dependencies (Ollama API, file system)
- Focus on business logic and edge cases

### UI Tests

- Test user interface interactions
- Use pytest-qt for PyQt5 testing
- Mock heavy operations to keep tests fast

### Integration Tests

- Test component interactions
- Test configuration loading/saving
- Test file operations with temporary files

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards

- Follow PEP 8 (enforced by Black)
- Add type hints to all functions
- Write docstrings for modules, classes, and functions
- Add tests for new functionality
- Keep functions focused and small
- Use descriptive variable names

## Debugging

### Common Issues

**Ollama Connection Errors:**
- Ensure Ollama is running: `ollama serve`
- Check if models are installed: `ollama list`
- Verify connection URL in settings

**PyQt5 Issues:**
- For display issues on high-DPI screens, ensure `QApplication.setAttribute` calls are made
- For theming issues, check CSS selector specificity

**Import Errors:**
- Ensure package is installed in development mode: `pip install -e .`
- Check Python path and virtual environment activation

### Debugging Tools

- Use VS Code debugger with launch configuration
- PyQt5 has built-in debug tools: `export QT_DEBUG_PLUGINS=1`
- Use `pytest --pdb` to drop into debugger on test failures

## Performance Considerations

- Ollama operations run in background threads to avoid UI blocking
- Large text operations use efficient string handling
- UI updates are batched where possible
- Memory usage is monitored for large documents