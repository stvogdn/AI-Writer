"""Ollama API client and worker threads for AI Writer.

This module provides the interface to communicate with the Ollama API for
model management and text generation.
"""

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from ai_writer.config import get_settings


class OllamaWorker(QThread):
    """Background worker for communicating with Ollama API."""

    # Signals
    models_loaded = pyqtSignal(list)  # List of model names
    finished = pyqtSignal(str)        # Generated text
    error = pyqtSignal(str)           # Error message

    def __init__(
        self,
        endpoint: str,
        model: str | None = None,
        prompt: str | None = None,
        temperature: float | None = None,
        token_limit: int | None = None
    ):
        """Initialize the Ollama worker.

        Args:
            endpoint: Either "scan" for model discovery or "generate" for
                text generation
            model: Model name (required for generation)
            prompt: Input text (required for generation)
            temperature: Generation temperature (optional)
            token_limit: Maximum tokens to generate (optional)
        """
        super().__init__()
        self.endpoint = endpoint
        self.model = model
        self.prompt = prompt
        self.temperature = temperature
        self.token_limit = token_limit

        # Get settings
        settings = get_settings()
        self.ollama_url = settings.ollama.url
        self.timeout = settings.ollama.timeout

    def run(self) -> None:
        """Execute the background task."""
        try:
            if self.endpoint == "scan":
                self._scan_models()
            elif self.endpoint == "generate":
                self._generate_text()
        except requests.exceptions.ConnectionError:
            self.error.emit("Cannot connect to Ollama. Is it running?")
        except Exception as e:
            self.error.emit(str(e))

    def _scan_models(self) -> None:
        """Scan for available Ollama models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                self.models_loaded.emit(models)
            else:
                self.error.emit(f"API Error: {response.status_code}")
        except requests.exceptions.Timeout:
            self.error.emit("Timeout while scanning for models")

    def _generate_text(self) -> None:
        """Generate text using the specified model."""
        if not self.model or not self.prompt:
            self.error.emit("Model and prompt are required for generation")
            return

        # Use provided values or defaults from settings
        settings = get_settings()
        temperature = (
            self.temperature
            if self.temperature is not None
            else settings.generation.default_temperature
        )
        token_limit = (
            self.token_limit
            if self.token_limit is not None
            else settings.generation.default_token_limit
        )

        try:
            system_instruction = (
                "Continue writing from where the text ends naturally. "
                "Do not repeat what was already written. "
                "Do not add explanations, comments, or meta-text. "
                "Just continue the story or sentence seamlessly."
            )
            full_prompt = f"{system_instruction}\n\nText to complete:\n{self.prompt}"

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": token_limit,
                    "temperature": temperature
                }
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                completion = data.get('response', '')
                cleaned = self._clean_completion(self.prompt, completion)
                self.finished.emit(cleaned)
            else:
                self.error.emit(f"Generation Error: {response.status_code}")
        except requests.exceptions.Timeout:
            self.error.emit("Timeout during text generation")

    def _clean_completion(self, original: str, completion: str) -> str:
        """Clean the completion text to remove unwanted artifacts."""
        original_stripped = original.strip()
        completion_stripped = completion.strip()

        # Remove original text if it appears at the start of completion
        if completion_stripped.startswith(original_stripped):
            completion_stripped = completion_stripped[len(original_stripped):].strip()

        # Remove common prefixes that the model might add
        prefixes = [
            "here's the continuation:", "continuation:", "continued:",
            "here is the completion:", "here's the completion:",
            "the continuation is:", "completion:"
        ]
        for prefix in prefixes:
            if completion_stripped.lower().startswith(prefix):
                completion_stripped = completion_stripped[len(prefix):].strip()

        # Handle quote matching
        if completion_stripped.startswith('"') and not original_stripped.endswith('"'):
            completion_stripped = completion_stripped[1:].strip()

        return completion_stripped


class OllamaClient:
    """High-level client for Ollama operations."""

    @staticmethod
    def scan_models() -> OllamaWorker:
        """Create a worker to scan for available models."""
        return OllamaWorker(endpoint="scan")

    @staticmethod
    def generate_text(
        model: str,
        prompt: str,
        temperature: float | None = None,
        token_limit: int | None = None
    ) -> OllamaWorker:
        """Create a worker to generate text.

        Args:
            model: Name of the model to use
            prompt: Input text to continue
            temperature: Generation temperature (optional)
            token_limit: Maximum tokens to generate (optional)

        Returns:
            OllamaWorker instance ready to start
        """
        return OllamaWorker(
            endpoint="generate",
            model=model,
            prompt=prompt,
            temperature=temperature,
            token_limit=token_limit
        )
