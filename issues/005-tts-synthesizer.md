# [AFK] Text-to-Speech con pyttsx3

**Labels:** `feature`, `tts`

## Descripción

Implementar el módulo de síntesis de voz que convierte texto a audio reproducible.
Usar `pyttsx3` como motor local (sin API key, completamente offline).

## Criterios de Aceptación

- [ ] `TTSSynthesizer.synthesize(text)` devuelve bytes de audio WAV
- [ ] Funciona sin conexión a internet (motor local)
- [ ] Configurable: velocidad de habla, voz (si hay múltiples disponibles)
- [ ] Tests unitarios con mock de pyttsx3
- [ ] Método async compatible con el pipeline asyncio

## Interface

```python
class TTSSynthesizer:
    def __init__(self, rate: int = 175, volume: float = 0.9):
        ...

    async def synthesize(self, text: str) -> bytes:
        """
        Convierte texto a audio WAV.

        Returns:
            Bytes del archivo WAV listo para reproducir
        """
        ...
```

## Notas Técnicas

- pyttsx3 es sincrónico → usar `run_in_executor` para no bloquear
- Para guardar audio a bytes: usar `engine.save_to_file()` a un archivo temp, luego leer
- Limpiar archivos temporales después de leer
- Alternativa más rápida si hay tiempo: `edge-tts` (Microsoft TTS, requiere internet)

## Archivos a Crear

- `src/tts/synthesizer.py`
- `tests/test_tts.py`
