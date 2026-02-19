"""Test Ollama client functionality."""

from unittest.mock import Mock, patch

import pytest
import requests

from ai_writer.core.ollama_client import OllamaAPI, OllamaClient, OllamaWorker


class TestOllamaAPI:
    """Test OllamaAPI class."""

    def test_init(self):
        """Test initialization of OllamaAPI."""
        api = OllamaAPI(url="http://test:11434")
        assert api.url == "http://test:11434"
        assert api.timeout == 10

    @patch("ai_writer.core.ollama_client.requests.get")
    def test_scan_models_success(self, mock_get):
        """Test successful model scanning in API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama2:latest"}, {"name": "codellama:13b"}]
        }
        mock_get.return_value = mock_response

        api = OllamaAPI(url="http://test")
        models = api.scan_models()
        assert models == ["llama2:latest", "codellama:13b"]

    @patch("ai_writer.core.ollama_client.requests.post")
    def test_generate_text_stream(self, mock_post):
        """Test streaming text generation in API."""
        mock_response = Mock()
        mock_response.status_code = 200
        import json
        chunks = [
            {"response": "This is", "done": False},
            {"response": " the", "done": False},
            {"response": " continuation.", "done": True}
        ]
        mock_response.iter_lines.return_value = [json.dumps(c).encode("utf-8") for c in chunks]
        mock_post.return_value = mock_response

        api = OllamaAPI(url="http://test")
        result_chunks = list(api.generate_text_stream("model", "Start", 0.7, 50))
        assert result_chunks == ["This is", " the", " continuation."]

    @patch("ai_writer.core.ollama_client.requests.post")
    def test_generate_text_batch(self, mock_post):
        """Test batch text generation in API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "This is the continuation."}
        mock_post.return_value = mock_response

        api = OllamaAPI(url="http://test")
        result = api.generate_text("model", "Start", 0.7, 50)
        assert result == "This is the continuation."

    def test_clean_completion_removes_original(self):
        """Test that completion cleaning removes original text."""
        original = "Hello world"
        completion = "Hello world! How are you today?"
        cleaned = OllamaAPI.clean_completion(original, completion)
        assert cleaned == "! How are you today?"

    def test_clean_completion_removes_prefixes(self):
        """Test that completion cleaning removes unwanted prefixes."""
        original = "Start"
        completion = "Here's the continuation: and this is more text."
        cleaned = OllamaAPI.clean_completion(original, completion)
        assert cleaned == "and this is more text."

    def test_clean_completion_handles_quotes(self):
        """Test that completion cleaning handles quotes correctly."""
        original = "He said"
        completion = '"Hello there"'
        cleaned = OllamaAPI.clean_completion(original, completion)
        assert cleaned == 'Hello there"'


class TestOllamaWorker:
    """Test OllamaWorker class."""

    def test_init_scan_endpoint(self):
        """Test initialization for model scanning."""
        worker = OllamaWorker(endpoint="scan")
        assert worker.endpoint == "scan"
        assert worker.model is None
        assert worker.prompt is None

    def test_init_generate_endpoint(self):
        """Test initialization for text generation."""
        worker = OllamaWorker(
            endpoint="generate",
            model="llama2",
            prompt="Test prompt",
            temperature=0.8,
            token_limit=100,
        )
        assert worker.endpoint == "generate"
        assert worker.model == "llama2"
        assert worker.prompt == "Test prompt"
        assert worker.temperature == 0.8
        assert worker.token_limit == 100

    @patch("ai_writer.core.ollama_client.get_settings")
    @patch("ai_writer.core.ollama_client.OllamaAPI")
    def test_scan_models_success(self, mock_api_class, mock_get_settings):
        """Test successful model scanning through worker."""
        mock_api = mock_api_class.return_value
        mock_api.scan_models.return_value = ["model1", "model2"]

        worker = OllamaWorker(endpoint="scan")
        worker.models_loaded = Mock()
        worker.error = Mock()

        worker.run()
        worker.models_loaded.emit.assert_called_once_with(["model1", "model2"])
        worker.error.emit.assert_not_called()

    @patch("ai_writer.core.ollama_client.get_settings")
    @patch("ai_writer.core.ollama_client.OllamaAPI")
    def test_scan_models_failure(self, mock_api_class, mock_get_settings):
        """Test failed model scanning through worker."""
        mock_api = mock_api_class.return_value
        # Use HTTPError which accepts constructor args compatible with what we throw
        mock_api.scan_models.side_effect = requests.exceptions.ConnectionError("Connection refused")

        worker = OllamaWorker(endpoint="scan")
        worker.models_loaded = Mock()
        worker.error = Mock()

        worker.run()
        worker.models_loaded.emit.assert_not_called()
        worker.error.emit.assert_called_once()

    @patch("ai_writer.core.ollama_client.get_settings")
    @patch("ai_writer.core.ollama_client.OllamaAPI")
    def test_generate_text_success_stream(self, mock_api_class, mock_settings):
        """Test successful text streaming through worker."""
        mock_api = mock_api_class.return_value
        mock_api.generate_text_stream.return_value = iter(["chunk1", "chunk2"])
        mock_settings_obj = Mock()
        mock_settings_obj.generation.default_temperature = 0.7
        mock_settings_obj.generation.default_token_limit = 100
        mock_settings.return_value = mock_settings_obj

        worker = OllamaWorker(
            endpoint="generate",
            model="llama2",
            prompt="Start",
            stream=True
        )
        worker.text_chunk_received = Mock()
        worker.finished = Mock()
        worker.error = Mock()

        worker.run()

        assert worker.text_chunk_received.emit.call_count == 2
        worker.finished.emit.assert_called_once_with("chunk1chunk2")
        worker.error.emit.assert_not_called()


class TestOllamaClient:
    """Test OllamaClient static methods."""

    def test_scan_models_returns_worker(self):
        """Test that scan_models returns an OllamaWorker."""
        worker = OllamaClient.scan_models()
        assert isinstance(worker, OllamaWorker)
        assert worker.endpoint == "scan"

    def test_generate_text_returns_worker(self):
        """Test that generate_text returns an OllamaWorker."""
        worker = OllamaClient.generate_text(
            model="test-model", prompt="test prompt", temperature=0.5, token_limit=200
        )
        assert isinstance(worker, OllamaWorker)
        assert worker.endpoint == "generate"
        assert worker.model == "test-model"
        assert worker.prompt == "test prompt"
        assert worker.temperature == 0.5
        assert worker.token_limit == 200

    def test_generate_text_with_defaults(self):
        """Test generate_text with default parameters."""
        worker = OllamaClient.generate_text(model="test-model", prompt="test prompt")
        assert worker.temperature is None
        assert worker.token_limit is None
