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

        # Colas para conectar etapas
        self._stt_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._llm_queue: asyncio.Queue[str] = asyncio.Queue()
        self._tts_queue: asyncio.Queue[str] = asyncio.Queue()
        self._out_queue: asyncio.Queue[bytes] = asyncio.Queue()

    async def run(self, audio_bytes: bytes) -> bytes:
        """
        Procesa un chunk de audio y devuelve el audio de respuesta.
        Implementado usando colas para cumplir con la arquitectura.
        """
        # Iniciamos workers de forma efímera para este run
        # En una versión de streaming, estos correrían en background
        stt_task = asyncio.create_task(self._stt_worker())
        llm_task = asyncio.create_task(self._llm_worker())
        tts_task = asyncio.create_task(self._tts_worker())

        await self._stt_queue.put(audio_bytes)
        response_audio = await self._out_queue.get()

        # Limpieza (opcional para tracer bullet)
        stt_task.cancel()
        llm_task.cancel()
        tts_task.cancel()
        
        return response_audio

    async def _stt_worker(self) -> None:
        while True:
            audio_bytes = await self._stt_queue.get()
            log = logger.bind(stage="stt")
            log.info("stt_start")
            self.state.update_stage("stt", StageStatus.PROCESSING)
            try:
                transcript = await self.stt.transcribe(audio_bytes)
                if transcript.strip():
                    self.state.add_turn("user", transcript)
                    log.info("stt_done", transcript=transcript)
                    await self._llm_queue.put(transcript)
                else:
                    log.info("stt_empty_transcript")
                    await self._out_queue.put(b"")
            except Exception:
                self.state.update_stage("stt", StageStatus.ERROR)
                log.exception("stt_failed")
                await self._out_queue.put(b"")
            finally:
                if self.state.stt_status != StageStatus.ERROR:
                    self.state.update_stage("stt", StageStatus.IDLE)
                self._stt_queue.task_done()

    async def _llm_worker(self) -> None:
        while True:
            transcript = await self._llm_queue.get()
            log = logger.bind(stage="llm")
            log.info("llm_start", user_text=transcript)
            self.state.update_stage("llm", StageStatus.PROCESSING)
            try:
                response_text = await self.llm.chat(transcript)
                self.state.add_turn("assistant", response_text)
                log.info("llm_done", response=response_text)
                await self._tts_queue.put(response_text)
            except Exception:
                self.state.update_stage("llm", StageStatus.ERROR)
                log.exception("llm_failed")
                await self._out_queue.put(b"")
            finally:
                if self.state.llm_status != StageStatus.ERROR:
                    self.state.update_stage("llm", StageStatus.IDLE)
                self._llm_queue.task_done()

    async def _tts_worker(self) -> None:
        while True:
            text = await self._tts_queue.get()
            log = logger.bind(stage="tts")
            log.info("tts_start", text=text)
            self.state.update_stage("tts", StageStatus.PROCESSING)
            try:
                response_audio = await self.tts.synthesize(text)
                log.info("tts_done", audio_bytes=len(response_audio))
                await self._out_queue.put(response_audio)
            except Exception:
                self.state.update_stage("tts", StageStatus.ERROR)
                log.exception("tts_failed")
                await self._out_queue.put(b"")
            finally:
                if self.state.tts_status != StageStatus.ERROR:
                    self.state.update_stage("tts", StageStatus.IDLE)
                self._tts_queue.task_done()


# ─── Entrypoint ──────────────────────────────────────────────────────────────

async def _demo() -> None:
    """Demo del pipeline con archivo WAV real y stubs."""
    import wave
    import os

    class StubSTT:
        async def transcribe(self, audio_bytes: bytes) -> str:
            return "Hola, esto es una prueba."

    class StubLLM:
        async def chat(self, text: str) -> str:
            return f"He escuchado: {text}"

    class StubTTS:
        async def synthesize(self, text: str) -> bytes:
            return b"FAKE_WAV_HEADER_AND_AUDIO"

    pipeline = VoicePipeline(stt=StubSTT(), llm=StubLLM(), tts=StubTTS())
    
    wav_path = "tests/fixtures/test_audio.wav"
    if not os.path.exists(wav_path):
        print(f"Error: {wav_path} no existe. Corre scripts/generate_test_audio.py primero.")
        return

    print(f"Procesando {wav_path}...")
    with wave.open(wav_path, "rb") as wav:
        audio_bytes = wav.readframes(wav.getnframes())

    result = await pipeline.run(audio_bytes)
    print(f"Pipeline result: {len(result)} bytes de audio")
    print("Historial de conversación:")
    for turn in pipeline.state.history:
        print(f"  {turn.role}: {turn.text}")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(_demo())


if __name__ == "__main__":
    main()
