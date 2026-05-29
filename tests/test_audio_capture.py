import pytest
import numpy as np
import asyncio
from unittest.mock import MagicMock
from src.audio.capture import VoiceActivityDetector, AudioCapture

@pytest.mark.asyncio
async def test_audio_capture_utterance(mocker):
    # Mock sounddevice.InputStream
    mock_stream = MagicMock()
    mocker.patch("sounddevice.InputStream", return_value=mock_stream)
    
    sample_rate = 16000
    chunk_duration_ms = 30
    samples_per_chunk = int(sample_rate * chunk_duration_ms / 1000)
    chunk_bytes = samples_per_chunk * 2 # 16-bit
    
    # Create AudioCapture
    capture = AudioCapture(sample_rate=sample_rate, chunk_duration_ms=chunk_duration_ms)
    
    # Prepare mock chunks
    silence_chunk = b'\x00' * chunk_bytes
    t = np.linspace(0, chunk_duration_ms/1000, samples_per_chunk, endpoint=False)
    speech_signal = (np.sin(2 * np.pi * 440 * t) * 30000).astype(np.int16)
    speech_chunk = speech_signal.tobytes()
    
    async with capture:
        import sounddevice as sd
        callback = sd.InputStream.call_args[1]['callback']
        
        # Start capture task
        task = asyncio.create_task(capture.capture_utterance())
        
        # Feed chunks
        # 1. Silence
        for _ in range(5):
            callback(np.frombuffer(silence_chunk, dtype=np.int16).reshape(-1, 1), None, None, None)
            await asyncio.sleep(0.001)
            
        # 2. Speech
        for _ in range(10):
            callback(np.frombuffer(speech_chunk, dtype=np.int16).reshape(-1, 1), None, None, None)
            await asyncio.sleep(0.001)
            
        # 3. Silence
        for _ in range(30):
            callback(np.frombuffer(silence_chunk, dtype=np.int16).reshape(-1, 1), None, None, None)
            await asyncio.sleep(0.001)
            
        utterance = await asyncio.wait_for(task, timeout=2.0)
        assert len(utterance) >= 10 * chunk_bytes

@pytest.mark.asyncio
async def test_audio_capture_multiple_utterances(mocker):
    # Mock sounddevice.InputStream
    mock_stream = MagicMock()
    mocker.patch("sounddevice.InputStream", return_value=mock_stream)
    
    sample_rate = 16000
    chunk_duration_ms = 30
    samples_per_chunk = int(sample_rate * chunk_duration_ms / 1000)
    chunk_bytes = samples_per_chunk * 2
    
    capture = AudioCapture(sample_rate=sample_rate, chunk_duration_ms=chunk_duration_ms)
    
    silence_chunk = b'\x00' * chunk_bytes
    t = np.linspace(0, chunk_duration_ms/1000, samples_per_chunk, endpoint=False)
    speech_signal = (np.sin(2 * np.pi * 440 * t) * 30000).astype(np.int16)
    speech_chunk = speech_signal.tobytes()
    
    async with capture:
        import sounddevice as sd
        callback = sd.InputStream.call_args[1]['callback']
        
        def feed(chunk, count):
            for _ in range(count):
                callback(np.frombuffer(chunk, dtype=np.int16).reshape(-1, 1), None, None, None)

        # 1. First utterance
        feed(speech_chunk, 10)
        feed(silence_chunk, 30)
        
        u1 = await asyncio.wait_for(capture.capture_utterance(), timeout=1.0)
        assert len(u1) >= 10 * chunk_bytes
        
        # 2. Second utterance
        feed(speech_chunk, 10)
        feed(silence_chunk, 30)
        
        u2 = await asyncio.wait_for(capture.capture_utterance(), timeout=1.0)
        assert len(u2) >= 10 * chunk_bytes

def test_vad_detects_silence():
    vad = VoiceActivityDetector(sample_rate=16000, aggressiveness=3)
    silence_chunk = b'\x00' * 960
    assert vad.is_speech(silence_chunk) is False

def test_vad_detects_speech():
    vad = VoiceActivityDetector(sample_rate=16000, aggressiveness=1)
    t = np.linspace(0, 0.030, 480, endpoint=False)
    speech_signal = (np.sin(2 * np.pi * 440 * t) * 30000).astype(np.int16)
    speech_chunk = speech_signal.tobytes()
    assert vad.is_speech(speech_chunk) is True
