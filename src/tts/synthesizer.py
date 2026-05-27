import asyncio
import os
import tempfile
import pyttsx3

class TTSSynthesizer:
    """Sintetizador de texto a voz usando pyttsx3."""

    def __init__(self, rate: int = 175, volume: float = 0.9, voice_id: str | None = None):
        """
        Inicializa el sintetizador.
        
        Args:
            rate: Velocidad del habla.
            volume: Volumen (0.0 a 1.0).
            voice_id: ID de la voz a usar (opcional).
        """
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id

    async def synthesize(self, text: str) -> bytes:
        """
        Convierte texto a audio WAV de forma asíncrona.
        
        Args:
            text: El texto a convertir.
            
        Returns:
            Bytes del archivo WAV generado.
        """
        # Ejecutamos la lógica síncrona en un hilo aparte para no bloquear el loop
        return await asyncio.to_thread(self._synthesize_sync, text)

    async def get_available_voices(self) -> list[dict[str, any]]:
        """
        Obtiene la lista de voces disponibles en el sistema.
        
        Returns:
            Lista de diccionarios con la información de cada voz.
        """
        return await asyncio.to_thread(self._get_voices_sync)

    def _get_voices_sync(self) -> list[dict[str, any]]:
        """Lógica síncrona para obtener voces."""
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        return [
            {
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages,
                "gender": voice.gender
            }
            for voice in voices
        ]

    def _synthesize_sync(self, text: str) -> bytes:
        """Lógica síncrona para pyttsx3."""
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.setProperty('volume', self.volume)
        if self.voice_id:
            engine.setProperty('voice', self.voice_id)
        
        # Crear un archivo temporal único
        fd, temp_filename = tempfile.mkstemp(suffix=".wav")
        os.close(fd) # Cerramos el descriptor de archivo para que pyttsx3 pueda escribir
        
        try:
            engine.save_to_file(text, temp_filename)
            engine.runAndWait()
            
            # Leer el archivo generado
            with open(temp_filename, "rb") as f:
                audio_data = f.read()
            return audio_data
        finally:
            # Limpieza del archivo temporal
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
