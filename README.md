# AI Writer 🖋️

![logo](assets/logo.png)

A sleek desktop application for AI-assisted writing powered by **Ollama** and built with **PyQt5**. Let your local LLM continue your stories, articles, or documents seamlessly.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- **🤖 AI Text Completion** - Continue your writing with local LLM models via Ollama
- **🎨 Light/Dark Theme** - Toggle between beautiful light and dark modes
- **🌡️ Temperature Control** - Adjust creativity vs. focus (0.0 - 2.0)
- **📊 Token Limit** - Control response length (10 - 2000 tokens)
- **📝 Model Selection** - Choose from all your installed Ollama models
- **💾 Multiple Export Formats** - Save as .txt or .docx (Word)
- **🖥️ Modern UI** - Clean, responsive interface with sidebar controls
- **⚙️ Configuration Management** - Persistent settings and preferences
- **🧪 Comprehensive Testing** - Full test suite for reliability

---

## 🚀 Quick Start

### 1. Requirements

- **Python 3.11+**
- **Ollama** installed and running locally ([ollama.ai](https://ollama.ai))

### 2. Installation

```bash
pip install ai-writer
```

### 3. Usage

```bash
ai-writer
```

---

## 🏗️ Development

### Setup

```bash
git clone https://github.com/Laszlobeer/AI-Writer.git
cd AI-Writer
uv sync --dev
```

### Running

```bash
uv run ai-writer
# OR
uv run python -m ai_writer.main
```

### Code Quality

```bash
uv run pytest tests/                      # Run tests
uv run black src/ tests/                  # Format code
uv run ruff check src/ tests/ --fix       # Lint code
uv run mypy src/ai_writer/               # Type checking
```

---

## 📖 Documentation

- **[User Guide](docs/user_guide.md)** - Complete usage instructions
- **[Development Guide](docs/development.md)** - Development setup and architecture
- **[Changelog](CHANGELOG.md)** - Version history and changes

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch
3. Make your changes and add tests
4. Submit a pull request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for the local LLM infrastructure
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the desktop UI framework
