import asyncio
import math
import sounddevice as sd
import webrtcvad
from typing import Optional, Any, Type, cast

class VoiceActivityDetector:
    def __init__(self, sample_rate: int = 16000, aggressiveness: int = 2):
        """
        Initializes the VAD.
        :param sample_rate: Audio sample rate (8000, 16000, 32000, or 48000 Hz).
        :param aggressiveness: An integer between 0 and 3. 0 is the least filtering out of non-speech, 3 is the most.
        """
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(aggressiveness)

    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Detects if there is speech in the given audio chunk.
        :param audio_chunk: 10, 20, or 30ms of 16-bit PCM audio.
        :return: True if speech is detected, False otherwise.
        """
        return cast(bool, self.vad.is_speech(audio_chunk, self.sample_rate))

class AudioCapture:
    def __init__(self, sample_rate: int = 16000, chunk_duration_ms: int = 30):
        if chunk_duration_ms not in [10, 20, 30]:
            raise ValueError("chunk_duration_ms must be 10, 20, or 30ms for webrtcvad")
            
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        self.vad = VoiceActivityDetector(sample_rate=sample_rate, aggressiveness=2)
        
        self.queue: Optional[asyncio.Queue[bytes]] = None
        self.stream: Optional[sd.InputStream] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def _callback(self, indata: Any, frames: int, time: Any, status: sd.CallbackFlags) -> None:
        if self.loop and self.queue:
            # indata is a numpy array view, must copy to bytes
            data = bytes(indata.tobytes())
            self.loop.call_soon_threadsafe(self.queue.put_nowait, data)

    async def __aenter__(self) -> "AudioCapture":
        self.loop = asyncio.get_running_loop()
        self.queue = asyncio.Queue()
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.chunk_size,
            callback=self._callback
        )
        self.stream.start()
        return self

    async def __aexit__(
        self, 
        exc_type: Optional[Type[BaseException]], 
        exc_val: Optional[BaseException], 
        exc_tb: Any
    ) -> None:
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.queue = None
        self.loop = None

    async def capture_utterance(self) -> bytes:
        """
        Captures a complete "utterance" based on VAD.
        Waits for speech to start, and finishes after ~500ms of silence.
        """
        if self.queue is None:
            raise RuntimeError("AudioCapture must be used as a context manager")

        audio_buffer = []
        is_speaking = False
        silence_threshold_ms = 500
        consecutive_silence_chunks = 0
        max_silence_chunks = math.ceil(silence_threshold_ms / self.chunk_duration_ms)

        while True:
            try:
                chunk = await self.queue.get()
                speech_detected = self.vad.is_speech(chunk)

                if not is_speaking:
                    if speech_detected:
                        is_speaking = True
                        audio_buffer.append(chunk)
                        consecutive_silence_chunks = 0
                else:
                    audio_buffer.append(chunk)
                    if not speech_detected:
                        consecutive_silence_chunks += 1
                        if consecutive_silence_chunks >= max_silence_chunks:
                            # End of speech detected
                            break
                    else:
                        consecutive_silence_chunks = 0
            except Exception:
                break
        
        return b''.join(audio_buffer)
