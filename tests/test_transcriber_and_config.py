import pytest
from src.core.transcriber import FasterWhisperTranscriber
from src.config import TranscriberConfig
from src.providers.gemini import GeminiProvider
from src.providers.ollama import OllamaProvider
from src.providers.openai import OpenAIProvider

def test_transcriber_mock():
    tw = FasterWhisperTranscriber()
    segments = tw.mock_transcribe("any_audio.mp3")
    assert len(segments) == 5
    assert segments[0].speaker == "Alex"
    assert "sprint review" in segments[0].text

def test_config_defaults():
    cfg = TranscriberConfig()
    assert cfg.provider_name == "rule"
    assert cfg.whisper_model == "base"
    assert cfg.get_provider("rule") is None
    assert cfg.get_provider("ollama") is not None
    assert cfg.get_provider("gemini") is None # without key

def test_provider_initialization():
    with pytest.raises(ValueError):
        GeminiProvider("")
    with pytest.raises(ValueError):
        OpenAIProvider("")
    
    ollama = OllamaProvider()
    assert ollama.name == "ollama"
    
    gemini = GeminiProvider("fake_key")
    assert gemini.name == "gemini"

    openai = OpenAIProvider("fake_key")
    assert openai.name == "openai"

