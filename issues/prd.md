# PRD: Agente de Voz Conversacional Mínimo

> Generado con la skill `/write-a-prd` tras interrogación con `/grill-me`

---

## 1. Problema

Los frameworks de voz modernos (Pipecat, LiveKit Agents) abstraen completamente
la arquitectura interna. Un desarrollador que los usa no entiende qué ocurre cuando
el usuario habla: cómo se segmenta el audio, cómo se detecta el fin de una frase,
cómo se sincronizan las etapas asíncronas.

**El problema concreto:** No existe una implementación de referencia minimalista
en Python puro que muestre la arquitectura de un agente de voz sin capas de abstracción.

---

## 2. Usuarios

**Usuario primario:** Desarrollador de software con conocimientos básicos de Python
que quiere entender la arquitectura de los agentes de voz modernos.

**Contexto de uso:** Entorno de desarrollo local, Python 3.11+, con micrófono y altavoz.
No es una aplicación de producción — es una herramienta educativa y de referencia.

---

## 3. Solución Propuesta

Un pipeline de voz en tiempo real implementado con `asyncio` nativo:

```
Micrófono → VAD → STT → LLM → TTS → Altavoz
```

Cada etapa es un módulo independiente conectado por `asyncio.Queue`.
El sistema es completamente observable: cada etapa loggea su estado.

Panel web opcional para monitorear el pipeline en tiempo real.

---

## 4. Arquitectura del Pipeline

```
AudioCapture (sounddevice)
    │  chunks PCM 30ms
    ▼
VoiceActivityDetector (webrtcvad)
    │  utterance completa (bytes)
    ▼
WhisperSTT (openai-whisper local)
    │  texto transcrito
    ▼
ConversationLLM (OpenAI API / Ollama)
    │  respuesta en texto
    ▼
TTSSynthesizer (pyttsx3 local)
    │  audio WAV bytes
    ▼
AudioPlayback (sounddevice)
```

Comunicación entre etapas: `asyncio.Queue` — sin threading.

---

## 5. Módulos a Construir

| Módulo | Archivo | Responsabilidad |
|--------|---------|-----------------|
| Pipeline | `src/core/pipeline.py` | Orquestador del loop |
| State | `src/core/state.py` | Estado compartido |
| AudioCapture | `src/audio/capture.py` | Mic + VAD |
| AudioPlayback | `src/audio/playback.py` | Reproducción |
| WhisperSTT | `src/stt/whisper_stt.py` | Speech-to-Text |
| ConversationLLM | `src/llm/chat.py` | Cliente LLM |
| TTSSynthesizer | `src/tts/synthesizer.py` | Text-to-Speech |
| API Server | `src/api/server.py` | FastAPI + WebSockets |
| Frontend | `frontend/index.html` | Panel de monitoreo |

---

## 6. User Stories

1. Como desarrollador, quiero correr `python -m src.core.pipeline` y ver el pipeline
   procesando audio de prueba, para validar que la arquitectura funciona end-to-end.

2. Como desarrollador, quiero hablar al micrófono y que el sistema detecte
   automáticamente cuándo terminé de hablar, para no tener que presionar ningún botón.

3. Como desarrollador, quiero que el texto que digo sea transcrito localmente
   (sin internet), para entender cómo funciona Whisper.

4. Como desarrollador, quiero que el agente responda con voz sintetizada localmente,
   para tener un loop completo sin dependencias de API externas.

5. Como desarrollador, quiero ver en un panel web el estado de cada etapa del pipeline
   en tiempo real, para entender qué ocurre en cada momento.

---

## 7. Criterios de Aceptación

| Story | Criterio |
|-------|----------|
| Pipeline E2E | `python -m src.core.pipeline` corre sin errores con audio mock |
| VAD | Detecta fin de habla con < 100ms de latencia |
| STT | Transcribe correctamente frases cortas en español |
| LLM | Responde en < 3 segundos con `gpt-4o-mini` |
| TTS | Sintetiza audio sin dependencia de internet |
| Latencia total | < 5 segundos end-to-end en hardware modesto |
| Tests | `pytest` pasa al 100% sin hardware real (usando mocks) |

---

## 8. Decisiones Técnicas

| Decisión | Elección | Razón |
|----------|----------|-------|
| Concurrencia | `asyncio` nativo | Sin threading, máxima legibilidad |
| STT | Whisper `tiny` local | Sin API key, funciona offline |
| LLM | OpenAI `gpt-4o-mini` | Barato, rápido; Ollama como alternativa |
| TTS | `pyttsx3` | Completamente local, sin internet |
| Audio | `sounddevice` | Cross-platform, asyncio-friendly |
| VAD | `webrtcvad` | Estándar de la industria, ligero |
| API | FastAPI + WebSockets | Async nativo, panel en tiempo real |
| Config | `.env` + `python-dotenv` | Simple, estándar |

---

## 9. Decisiones de Testing

- **Sin hardware real en tests** — todo mockeado con `unittest.mock`
- **Sin modelos descargados en CI** — Whisper mockeado
- **Sin API keys reales en CI** — variable de entorno fake
- **Framework:** `pytest` + `pytest-asyncio`
- **Cobertura mínima:** 70% en `src/core/` y `src/stt/`

---

## 10. Fuera de Alcance

- Soporte multi-usuario
- Persistencia de conversaciones en base de datos
- Streaming de STT (chunk por chunk)
- Wake word detection
- Deployment en producción / cloud
- Autenticación en el panel web

---

## 11. Riesgos Técnicos

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| Whisper muy lento en CPU 2 cores | Alta | Usar modelo `tiny`, mockear en tests |
| `webrtcvad` incompatible con OS | Media | Fallback a detección por energía |
| `pyttsx3` sin voces en Linux | Media | Documentar instalación de `espeak` |
| Latencia > 5s en hardware bajo | Alta | Aceptable para propósito educativo |
