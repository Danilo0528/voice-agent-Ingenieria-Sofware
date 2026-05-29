import pytest
from unittest.mock import MagicMock, patch
from src.stt.whisper_stt import WhisperSTT

@pytest.mark.asyncio
async def test_whisper_stt_transcribe_returns_string():
    # Arrange
    with patch("whisper.load_model") as mock_load:
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        mock_model.transcribe.return_value = {"text": "Hola mundo"}
        
        stt = WhisperSTT(model="tiny")
        # 1 second of non-silent audio (simulated with random data)
        import numpy as np
        fake_audio = np.random.randint(-1000, 1000, 16000, dtype=np.int16).tobytes()
        
        # Act
        result = await stt.transcribe(fake_audio)
    
    # Assert
    assert isinstance(result, str)
    assert result == "Hola mundo"

@pytest.mark.asyncio
async def test_whisper_stt_filters_short_audio():
    # Arrange
    with patch("whisper.load_model") as mock_load:
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        # Model returns something even for very short audio (hallucination)
        mock_model.transcribe.return_value = {"text": "Hallucination"}
        
        stt = WhisperSTT(model="tiny")
        # 0.4 seconds of audio (16kHz * 0.4 * 2 bytes/sample = 12800 bytes)
        short_audio = b"\x00" * 12800
        
        # Act
        result = await stt.transcribe(short_audio)
    
    # Assert
    assert result == ""

def test_whisper_stt_loads_correct_model():
    # Arrange & Act
    with patch("whisper.load_model") as mock_load:
        stt = WhisperSTT(model="base")
        
    # Assert
    mock_load.assert_called_once_with("base")
    assert stt.model_name == "base"

@pytest.mark.asyncio
async def test_whisper_stt_filters_silence():
    # Arrange
    with patch("whisper.load_model") as mock_load:
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        # Model should NOT be called if we detect silence
        
        stt = WhisperSTT(model="tiny")
        # 1 second of absolute silence
        silent_audio = b"\x00" * 32000
        
        # Act
        result = await stt.transcribe(silent_audio)
    
    # Assert
    assert result == ""
    mock_model.transcribe.assert_not_called()
