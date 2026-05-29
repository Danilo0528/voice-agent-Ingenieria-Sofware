import asyncio
import whisper
import numpy as np
import time
import structlog

logger = structlog.get_logger(__name__)

class WhisperSTT:
    def __init__(self, model: str = "tiny"):
        self.model_name = model
        self._model = whisper.load_model(model)

    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio PCM a texto.

        Args:
            audio_bytes: Audio en formato PCM 16-bit, 16kHz, mono

        Returns:
            Texto transcrito, string vacío si no hay habla detectada
        """
        # Filter very short audio (<0.5s) to avoid hallucinations
        # 16000 samples/sec * 2 bytes/sample * 0.5 sec = 16000 bytes
        if len(audio_bytes) < 16000:
            logger.debug("audio_too_short", length=len(audio_bytes))
            return ""

        # Convert PCM 16-bit to float32 for processing
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        # Simple silence detection: if RMS is very low, skip
        rms = np.sqrt(np.mean(audio_np**2))
        if rms < 0.001:  # Threshold for silence
            logger.debug("silence_detected", rms=rms)
            return ""

        start_time = time.time()
        
        loop = asyncio.get_event_loop()
        # Whisper.transcribe expect a numpy array or path to file
        result = await loop.run_in_executor(None, lambda: self._model.transcribe(audio_np))
        
        duration = time.time() - start_time
        logger.info("transcription_completed", duration_sec=round(duration, 3), model=self.model_name)
        
        return result.get("text", "").strip()
