"""Core functionality for AI Writer."""

from ai_writer.core.file_manager import FileManager
from ai_writer.core.ollama_client import OllamaClient
from ai_writer.core.prompt_manager import PromptManager, get_prompt_manager, initialize_default_prompts
from ai_writer.core.spell_checker import SpellChecker

__all__ = ["OllamaClient", "FileManager", "PromptManager", "get_prompt_manager", "initialize_default_prompts", "SpellChecker"]
