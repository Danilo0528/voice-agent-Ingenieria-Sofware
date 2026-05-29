# [AFK] Speech-to-Text con Whisper (Local)

**Labels:** `feature`, `stt`

## Descripción

Implementar el módulo de transcripción de voz usando **Whisper de OpenAI** corriendo
localmente. Debe ser async-compatible para integrarse con el pipeline asyncio.

## Criterios de Aceptación

- [x] `WhisperSTT.transcribe(audio_bytes)` devuelve texto transcrito
- [x] Funciona con audio PCM en formato bytes (16-bit, 16kHz, mono)
- [x] Configurable: modelo "tiny" (rápido) o "base"/"small" (más preciso)
- [x] Tests unitarios con mock del modelo Whisper (no descarga el modelo en CI)
- [x] Manejo de errores cuando el audio es muy corto o silencioso
- [x] Logging del tiempo de transcripción para medir latencia

## Interface

```python
class WhisperSTT:
    def __init__(self, model: str = "tiny"):
        ...

    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio PCM a texto.

        Args:
            audio_bytes: Audio en formato PCM 16-bit, 16kHz, mono

        Returns:
            Texto transcrito, string vacío si no hay habla detectada
        """
        ...
```

## Notas Técnicas

- Whisper necesita audio en float32, no int16 → convertir con numpy
- Correr Whisper en executor para no bloquear el event loop:
  ```python
  loop = asyncio.get_event_loop()
  result = await loop.run_in_executor(None, self._model.transcribe, audio_np)
  ```
- El modelo "tiny" tiene ~150ms de latencia en CPU, suficiente para el prototipo
- Audio muy corto (<0.5s) puede generar alucinaciones → filtrar

## Archivos a Crear

- `src/stt/whisper_stt.py`
- `tests/test_stt.py`

## Dependencias

- `openai-whisper>=20231117`
- `numpy>=1.26`
