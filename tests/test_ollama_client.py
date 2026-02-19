"""Test Ollama client functionality."""

from unittest.mock import Mock, patch

from ai_writer.core.ollama_client import OllamaClient, OllamaWorker


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

    @patch("ai_writer.core.ollama_client.requests.get")
    def test_scan_models_success(self, mock_get):
        """Test successful model scanning."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama2:latest"}, {"name": "codellama:13b"}]
        }
        mock_get.return_value = mock_response

        worker = OllamaWorker(endpoint="scan")

        # Mock signals
        worker.models_loaded = Mock()
        worker.error = Mock()

        worker._scan_models()

        worker.models_loaded.emit.assert_called_once_with(
            ["llama2:latest", "codellama:13b"]
        )
        worker.error.emit.assert_not_called()

    @patch("ai_writer.core.ollama_client.requests.get")
    def test_scan_models_failure(self, mock_get):
        """Test failed model scanning."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        worker = OllamaWorker(endpoint="scan")
        worker.models_loaded = Mock()
        worker.error = Mock()

        worker._scan_models()

        worker.models_loaded.emit.assert_not_called()
        worker.error.emit.assert_called_once()

    @patch("ai_writer.core.ollama_client.requests.post")
    def test_generate_text_success(self, mock_post):
        """Test successful text generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is the generated continuation."
        }
        mock_post.return_value = mock_response

        worker = OllamaWorker(
            endpoint="generate",
            model="llama2",
            prompt="Start of text",
            temperature=0.7,
            token_limit=50,
        )

        # Mock the signal emissions
        with (
            patch.object(worker.finished, "emit") as mock_finished,
            patch.object(worker.error, "emit") as mock_error,
        ):
            worker._generate_text()

            mock_finished.assert_called_once()
            mock_error.assert_not_called()

        # Check that the API was called with correct parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]["json"]
        assert call_args["model"] == "llama2"
        assert "Start of text" in call_args["prompt"]
        assert call_args["options"]["temperature"] == 0.7
        assert call_args["options"]["num_predict"] == 50

    def test_clean_completion_removes_original(self):
        """Test that completion cleaning removes original text."""
        worker = OllamaWorker(endpoint="generate")
        original = "Hello world"
        completion = "Hello world! How are you today?"

        cleaned = worker._clean_completion(original, completion)
        assert cleaned == "! How are you today?"

    def test_clean_completion_removes_prefixes(self):
        """Test that completion cleaning removes unwanted prefixes."""
        worker = OllamaWorker(endpoint="generate")
        original = "Start"
        completion = "Here's the continuation: and this is more text."

        cleaned = worker._clean_completion(original, completion)
        assert cleaned == "and this is more text."

    def test_clean_completion_handles_quotes(self):
        """Test that completion cleaning handles quotes correctly."""
        worker = OllamaWorker(endpoint="generate")
        original = "He said"
        completion = '"Hello there"'

        cleaned = worker._clean_completion(original, completion)
        assert cleaned == 'Hello there"'


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
        assert worker.temperature is None  # Will use settings default
        assert worker.token_limit is None  # Will use settings default
