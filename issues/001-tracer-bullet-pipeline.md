# [AFK] Tracer Bullet: Pipeline de Voz End-to-End Mínimo

**Labels:** `tracer-bullet`, `priority:high`

## Descripción

Implementar el pipeline completo de voz de la forma más simple posible para validar
que la arquitectura funciona end-to-end. No tiene que ser perfecto, solo tiene que correr.

## Objetivo

> "Hacer hablar al sistema por primera vez"

## Criterios de Aceptación

- [ ] `python -m src.core.pipeline` corre sin errores
- [ ] El pipeline procesa un archivo `.wav` de prueba (no micrófono real todavía)
- [ ] El output es texto transcrito por el STT
- [ ] Existe al menos un test de integración que valida el flujo completo con mocks

## Implementación Sugerida

1. `src/core/pipeline.py` — Clase `VoicePipeline` con método `async run(audio_bytes) -> str`
2. Conectar: audio_bytes → STT → LLM → TTS → bytes_de_audio_respuesta
3. Usar mocks para STT, LLM y TTS en los tests
4. El método `main()` corre el pipeline con un archivo de prueba

## Notas Técnicas

- Usar `asyncio.Queue` para conectar las etapas
- No usar threading, solo asyncio
- El audio de prueba puede ser silencio o un `.wav` sintético generado con numpy

## Archivos a Crear

- `src/core/pipeline.py`
- `src/core/state.py`
- `tests/test_pipeline.py`
- `tests/fixtures/test_audio.wav` (generado programáticamente)
