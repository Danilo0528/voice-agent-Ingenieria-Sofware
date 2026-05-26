"""Tests del pipeline principal."""

import pytest
from unittest.mock import AsyncMock

from src.core.pipeline import VoicePipeline
from src.core.state import PipelineState, StageStatus


@pytest.fixture
def mock_stt():
    stt = AsyncMock()
    stt.transcribe.return_value = "hola mundo"
    return stt


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.chat.return_value = "hola, ¿en qué te puedo ayudar?"
    return llm


@pytest.fixture
def mock_tts():
    tts = AsyncMock()
    tts.synthesize.return_value = b"FAKE_AUDIO"
    return tts


@pytest.fixture
def pipeline(mock_stt, mock_llm, mock_tts):
    return VoicePipeline(stt=mock_stt, llm=mock_llm, tts=mock_tts)


class TestVoicePipeline:
    async def test_run_returns_audio_bytes(self, pipeline):
        result = await pipeline.run(b"audio_input")
        assert isinstance(result, bytes)
        assert len(result) > 0

    async def test_run_calls_stt_with_audio(self, pipeline, mock_stt):
        await pipeline.run(b"audio_input")
        mock_stt.transcribe.assert_called_once_with(b"audio_input")

    async def test_run_calls_llm_with_transcript(self, pipeline, mock_llm):
        await pipeline.run(b"audio_input")
        mock_llm.chat.assert_called_once_with("hola mundo")

    async def test_run_calls_tts_with_llm_response(self, pipeline, mock_tts):
        await pipeline.run(b"audio_input")
        mock_tts.synthesize.assert_called_once_with("hola, ¿en qué te puedo ayudar?")

    async def test_run_stores_user_turn_in_history(self, pipeline):
        await pipeline.run(b"audio_input")
        user_turns = [t for t in pipeline.state.history if t.role == "user"]
        assert len(user_turns) == 1
        assert user_turns[0].text == "hola mundo"

    async def test_run_stores_assistant_turn_in_history(self, pipeline):
        await pipeline.run(b"audio_input")
        assistant_turns = [t for t in pipeline.state.history if t.role == "assistant"]
        assert len(assistant_turns) == 1
        assert assistant_turns[0].text == "hola, ¿en qué te puedo ayudar?"

    async def test_run_returns_empty_bytes_on_empty_transcript(
        self, pipeline, mock_stt
    ):
        mock_stt.transcribe.return_value = ""
        result = await pipeline.run(b"silence")
        assert result == b""

    async def test_run_returns_empty_bytes_on_whitespace_transcript(
        self, pipeline, mock_stt
    ):
        mock_stt.transcribe.return_value = "   "
        result = await pipeline.run(b"silence")
        assert result == b""

    async def test_state_resets_correctly(self, pipeline):
        await pipeline.run(b"audio_input")
        assert len(pipeline.state.history) == 2

        pipeline.state.reset()
        assert len(pipeline.state.history) == 0
        assert pipeline.state.stt_status == StageStatus.IDLE

    async def test_multiple_turns_accumulate_history(self, pipeline):
        await pipeline.run(b"audio_1")
        await pipeline.run(b"audio_2")
        assert len(pipeline.state.history) == 4  # 2 user + 2 assistant

    async def test_run_with_wav_file(self, pipeline):
        import wave
        import os
        
        wav_path = "tests/fixtures/test_audio.wav"
        assert os.path.exists(wav_path)
        
        with wave.open(wav_path, "rb") as wav:
            audio_bytes = wav.readframes(wav.getnframes())
            
        result = await pipeline.run(audio_bytes)
        assert isinstance(result, bytes)
        assert len(result) > 0
