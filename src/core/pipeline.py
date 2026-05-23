"""
Pipeline principal del agente de voz.

Conecta las etapas mediante asyncio.Queue:
  audio_bytes → STT → LLM → TTS → audio_bytes
"""

from __future__ import annotations

import asyncio
import logging
from typing import Protocol

import structlog

from src.core.state import PipelineState, StageStatus

logger = structlog.get_logger(__name__)


# ─── Protocolos (interfaces) ────────────────────────────────────────────────

class STTProvider(Protocol):
    async def transcribe(self, audio_bytes: bytes) -> str:
        ...


class LLMProvider(Protocol):
    async def chat(self, user_message: str) -> str:
        ...


class TTSProvider(Protocol):
    async def synthesize(self, text: str) -> bytes:
        ...


# ─── Pipeline ────────────────────────────────────────────────────────────────

class VoicePipeline:
    """
    Orquestador del pipeline de voz end-to-end.

    Uso:
        pipeline = VoicePipeline(stt=..., llm=..., tts=...)
        response_audio = await pipeline.run(audio_bytes)
    """

    def __init__(
        self,
        stt: STTProvider,
        llm: LLMProvider,
        tts: TTSProvider,
        state: PipelineState | None = None,
    ) -> None:
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.state = state or PipelineState()

    async def run(self, audio_bytes: bytes) -> bytes:
        """
        Procesa un chunk de audio y devuelve el audio de respuesta.

        Args:
            audio_bytes: Audio PCM 16-bit 16kHz mono

        Returns:
            Audio WAV de la respuesta sintetizada
        """
        log = logger.bind(pipeline="run")

        # Etapa 1: STT
        log.info("stt_start")
        self.state.stt_status = StageStatus.PROCESSING
        try:
            transcript = await self.stt.transcribe(audio_bytes)
        except Exception as e:
            self.state.stt_status = StageStatus.ERROR
            log.error("stt_failed", error=str(e))
            raise
        self.state.stt_status = StageStatus.IDLE

        if not transcript.strip():
            log.info("stt_empty_transcript")
            return b""

        self.state.add_turn("user", transcript)
        log.info("stt_done", transcript=transcript)

        # Etapa 2: LLM
        log.info("llm_start", user_text=transcript)
        self.state.llm_status = StageStatus.PROCESSING
        try:
            response_text = await self.llm.chat(transcript)
        except Exception as e:
            self.state.llm_status = StageStatus.ERROR
            log.error("llm_failed", error=str(e))
            raise
        self.state.llm_status = StageStatus.IDLE
        self.state.add_turn("assistant", response_text)
        log.info("llm_done", response=response_text)

        # Etapa 3: TTS
        log.info("tts_start", text=response_text)
        self.state.tts_status = StageStatus.PROCESSING
        try:
            response_audio = await self.tts.synthesize(response_text)
        except Exception as e:
            self.state.tts_status = StageStatus.ERROR
            log.error("tts_failed", error=str(e))
            raise
        self.state.tts_status = StageStatus.IDLE
        log.info("tts_done", audio_bytes=len(response_audio))

        return response_audio


# ─── Entrypoint ──────────────────────────────────────────────────────────────

async def _demo() -> None:
    """Demo del pipeline con implementaciones stub."""

    class StubSTT:
        async def transcribe(self, audio_bytes: bytes) -> str:
            return "Hola, ¿cómo estás?"

    class StubLLM:
        async def chat(self, text: str) -> str:
            return f"Recibí: {text}"

    class StubTTS:
        async def synthesize(self, text: str) -> bytes:
            return b"FAKE_AUDIO_BYTES"

    pipeline = VoicePipeline(stt=StubSTT(), llm=StubLLM(), tts=StubTTS())
    result = await pipeline.run(b"fake_audio")
    print(f"Pipeline result: {len(result)} bytes de audio")
    print(f"Historial: {pipeline.state.history}")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(_demo())


if __name__ == "__main__":
    main()
