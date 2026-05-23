# [AFK] Captura de Audio con Voice Activity Detection (VAD)

**Labels:** `feature`, `audio`

## Descripción

Implementar el módulo de captura de audio desde el micrófono con detección de actividad
de voz (VAD) para saber cuándo el usuario empieza y termina de hablar.

## El Problema

Sin VAD, el sistema no sabe cuándo enviar el audio al STT. Necesitamos detectar:
- **Inicio de habla**: enviar señal para empezar a grabar
- **Fin de habla**: enviar el chunk de audio al STT (silencio por >500ms)

## Criterios de Aceptación

- [ ] `VoiceActivityDetector` detecta correctamente silencio vs. habla en tests
- [ ] `AudioCapture` puede capturar audio en chunks de 30ms (requerimiento de webrtcvad)
- [ ] El método `capture_utterance()` devuelve bytes de audio de una "utterance" completa
- [ ] Tests unitarios pasan con audio sintético (no requiere micrófono físico)
- [ ] Latencia de detección < 100ms

## Implementación

```
src/audio/capture.py
  ├── class VoiceActivityDetector
  │   ├── __init__(sample_rate=16000, aggressiveness=2)
  │   └── is_speech(audio_chunk: bytes) -> bool
  └── class AudioCapture
      ├── __init__(sample_rate=16000, chunk_duration_ms=30)
      ├── async capture_utterance() -> bytes
      └── async __aenter__ / __aexit__ (context manager)
```

## Notas Técnicas

- `webrtcvad` requiere chunks de exactamente 10, 20 o 30ms
- Sample rate debe ser 8000, 16000, 32000 o 48000 Hz
- Usar `sounddevice.InputStream` con callback para captura no-bloqueante
- "Fin de habla" = 500ms de silencio consecutivo después de haber detectado habla

## Archivos a Crear

- `src/audio/capture.py`
- `tests/test_audio_capture.py`

## Dependencias

- `webrtcvad>=2.0.10`
- `sounddevice>=0.4.6`
- `numpy>=1.26`
