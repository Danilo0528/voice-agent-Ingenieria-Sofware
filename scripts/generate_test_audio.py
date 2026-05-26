import wave
import numpy as np

def generate_test_wav(file_path: str, duration_sec: float = 1.0, sample_rate: int = 16000):
    """Genera un archivo WAV de prueba con una onda senoidal de 440Hz."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    audio_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    
    with wave.open(file_path, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

if __name__ == "__main__":
    generate_test_wav("tests/fixtures/test_audio.wav")
