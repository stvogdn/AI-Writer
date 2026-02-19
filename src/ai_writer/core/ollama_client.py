"""Ollama API client and worker threads for AI Writer.

This module provides the interface to communicate with the Ollama API for
model management and text generation.
"""

import json
from typing import Generator

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from ai_writer.config import get_settings


class OllamaAPI:
    """Pure Python client for Ollama API operations."""

    def __init__(self, url: str, timeout: int = 10):
        self.url = url
        self.timeout = timeout

    def scan_models(self) -> list[str]:
        """Scan for available Ollama models."""
        response = requests.get(f"{self.url}/api/tags", timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]

    def generate_text_stream(
        self,
        model: str,
        prompt: str,
        temperature: float,
        token_limit: int,
    ) -> Generator[str, None, None]:
        """Generate text as a stream of chunks."""
        system_instruction = (
            "Continue writing from where the text ends naturally. "
            "Do not repeat what was already written. "
            "Do not add explanations, comments, or meta-text. "
            "Just continue the story or sentence seamlessly."
        )
        full_prompt = f"{system_instruction}\n\nText to complete:\n{prompt}"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": True,
            "options": {"num_predict": token_limit, "temperature": temperature},
        }

        response = requests.post(
            f"{self.url}/api/generate",
            json=payload,
            timeout=self.timeout,
            stream=True
        )
        response.raise_for_status()

        is_first_chunk = True
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                chunk = data.get("response", "")
                
                # Clean the first chunk if needed (remove model chatter)
                if is_first_chunk and chunk:
                    chunk = self.clean_completion(prompt, chunk)
                    is_first_chunk = False
                
                if chunk:
                    yield chunk
                    
                if data.get("done"):
                    break

    def generate_text(
        self,
        model: str,
        prompt: str,
        temperature: float,
        token_limit: int,
    ) -> str:
        """Generate complete text at once."""
        system_instruction = (
            "Continue writing from where the text ends naturally. "
            "Do not repeat what was already written. "
            "Do not add explanations, comments, or meta-text. "
            "Just continue the story or sentence seamlessly."
        )
        full_prompt = f"{system_instruction}\n\nText to complete:\n{prompt}"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {"num_predict": token_limit, "temperature": temperature},
        }

        response = requests.post(
            f"{self.url}/api/generate",
            json=payload,
            timeout=self.timeout,
            stream=False
        )
        response.raise_for_status()
        
        data = response.json()
        completion = data.get("response", "")
        return self.clean_completion(prompt, completion)

    @staticmethod
    def clean_completion(original: str, completion: str) -> str:
        """Clean the completion text to remove unwanted artifacts."""
        original_stripped = original.strip()
        completion_stripped = completion.strip()

        # Remove original text if it appears at the start of completion
        if completion_stripped.startswith(original_stripped):
            completion_stripped = completion_stripped[len(original_stripped) :].strip()

        # Remove common prefixes that the model might add
        prefixes = [
            "here's the continuation:",
            "continuation:",
            "continued:",
            "here is the completion:",
            "here's the completion:",
            "the continuation is:",
            "completion:",
        ]
        for prefix in prefixes:
            if completion_stripped.lower().startswith(prefix):
                completion_stripped = completion_stripped[len(prefix) :].strip()

        # Handle quote matching
        if completion_stripped.startswith('"') and not original_stripped.endswith('"'):
            completion_stripped = completion_stripped[1:].strip()

        return completion_stripped


class OllamaWorker(QThread):
    """Background worker for communicating with Ollama API."""

    # Signals
    models_loaded = pyqtSignal(list)  # List of model names
    finished = pyqtSignal(str)  # Generated text
    error = pyqtSignal(str)  # Error message

    text_chunk_received = pyqtSignal(str)  # Real-time text chunks

    def __init__(
        self,
        endpoint: str,
        model: str | None = None,
        prompt: str | None = None,
        temperature: float | None = None,
        token_limit: int | None = None,
        stream: bool = True,
    ):
        """Initialize the Ollama worker.

        Args:
            endpoint: Either "scan" for model discovery or "generate" for
                text generation
            model: Model name (required for generation)
            prompt: Input text (required for generation)
            temperature: Generation temperature (optional)
            token_limit: Maximum tokens to generate (optional)
            stream: Whether to stream the response (default: True)
        """
        super().__init__()
        self.endpoint = endpoint
        self.model = model
        self.prompt = prompt
        self.temperature = temperature
        self.token_limit = token_limit
        self.stream = stream

    def run(self) -> None:
        """Execute the background task."""
        try:
            settings = get_settings()
            api = OllamaAPI(url=settings.ollama.url, timeout=settings.ollama.timeout)
            
            if self.endpoint == "scan":
                models = api.scan_models()
                self.models_loaded.emit(models)
            elif self.endpoint == "generate":
                self._generate_text(api, settings)
        except requests.exceptions.ConnectionError:
            self.error.emit("Cannot connect to Ollama. Is it running?")
        except requests.exceptions.Timeout:
            self.error.emit(f"Timeout during {'model scanning' if self.endpoint == 'scan' else 'text generation'}")
        except requests.exceptions.HTTPError as e:
            self.error.emit(f"API Error: {e.response.status_code}")
        except Exception as e:
            self.error.emit(str(e))

    def _generate_text(self, api: OllamaAPI, settings) -> None:
        """Generate text using the specified model."""
        if not self.model or not self.prompt:
            self.error.emit("Model and prompt are required for generation")
            return

        # Use provided values or defaults from settings
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

        if self.stream:
            full_completion = ""
            for chunk in api.generate_text_stream(
                model=self.model,
                prompt=self.prompt,
                temperature=temperature,
                token_limit=token_limit
            ):
                full_completion += chunk
                self.text_chunk_received.emit(chunk)
            self.finished.emit(full_completion)
        else:
            completion = api.generate_text(
                model=self.model,
                prompt=self.prompt,
                temperature=temperature,
                token_limit=token_limit
            )
            self.finished.emit(completion)


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
        token_limit: int | None = None,
        stream: bool = True,
    ) -> OllamaWorker:
        """Create a worker to generate text.

        Args:
            model: Name of the model to use
            prompt: Input text to continue
            temperature: Generation temperature (optional)
            token_limit: Maximum tokens to generate (optional)
            stream: Whether to stream the response (default: True)

        Returns:
            OllamaWorker instance ready to start
        """
        return OllamaWorker(
            endpoint="generate",
            model=model,
            prompt=prompt,
            temperature=temperature,
            token_limit=token_limit,
            stream=stream,
        )
