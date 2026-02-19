"""AI Writer - A desktop application for AI-assisted writing.

This package provides a PyQt5-based desktop application that integrates with
Ollama for AI text generation and completion.
"""

__version__ = "0.2.0"
__author__ = "Laszlobeer"
__email__ = ""
__description__ = (
    "A sleek desktop application for AI-assisted writing powered by Ollama"
)

from ai_writer.main import main

__all__ = ["main"]
