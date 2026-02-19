"""Core functionality for AI Writer."""

from ai_writer.core.file_manager import FileManager
from ai_writer.core.ollama_client import OllamaClient

__all__ = ["OllamaClient", "FileManager"]
