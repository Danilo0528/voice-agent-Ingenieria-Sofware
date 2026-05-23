# Client Brief — Agente de Voz Conversacional Mínimo

## Resumen Ejecutivo

Quiero construir un **agente de voz conversacional mínimo en Python puro** usando `asyncio`
para entender profundamente la arquitectura detrás de frameworks como **Pipecat** y **LiveKit Agents**.

El objetivo no es solo que funcione: es entender *por qué* funciona, capa por capa.

---

## El Problema

Los frameworks de voz modernos (Pipecat, LiveKit Agents, Vocode) abstraen demasiado.
Un desarrollador que los usa no sabe qué pasa cuando el usuario habla:
- ¿Cuándo se corta el audio?
- ¿Cómo se detecta el fin de una frase?
- ¿Cómo se sincroniza el STT con el LLM con el TTS?

Este proyecto resuelve eso construyendo todo desde cero.

---

## El Sistema

Un **loop en tiempo real** con 5 etapas:

```
Micrófono → STT → LLM → TTS → Altavoz
```

### Pipeline Detallado

| Etapa | Tecnología | Rol |
|-------|-----------|-----|
| **Micrófono** | `sounddevice` | Captura audio PCM en chunks |
| **VAD** | WebRTC VAD / energy-based | Detecta inicio/fin de habla |
| **STT** | Whisper (local) o Deepgram | Transcribe audio a texto |
| **LLM** | OpenAI API / Ollama local | Genera respuesta conversacional |
| **TTS** | pyttsx3 / Coqui / ElevenLabs | Sintetiza texto a audio |
| **Altavoz** | `sounddevice` | Reproduce audio generado |

---

## Componentes

### Backend (Python)
- `src/core/pipeline.py` — Orquestador asyncio del pipeline
- `src/audio/capture.py` — Captura de micrófono con VAD
- `src/audio/playback.py` — Reproducción de audio
- `src/stt/whisper_stt.py` — Speech-to-Text con Whisper
- `src/llm/chat.py` — Cliente LLM (OpenAI / Ollama)
- `src/tts/synthesizer.py` — Text-to-Speech
- `src/core/state.py` — Estado de la conversación

### Frontend (Web UI)
- Panel de monitoreo en tiempo real del pipeline
- Visualización del estado de cada etapa
- Log de transcripciones y respuestas
- Controles: start/stop, cambio de modelo

### API
- FastAPI server con WebSockets
- Endpoints para controlar el agente
- Streaming de eventos del pipeline al frontend

---

## Restricciones Técnicas

- Python 3.11+
- Solo `asyncio` nativo (sin threading)
- Latencia target: < 2 segundos end-to-end
- Sin dependencia de frameworks de voz (Pipecat, LiveKit, etc.)

---

## Criterio de Éxito

> El sistema puede mantener una conversación fluida de 5 turnos donde el usuario
> habla, el agente responde por voz, y la latencia percibida es menor a 2 segundos.

---

## Autor

Proyecto integrador — Curso de Desarrollo con IA  
Usando **Gemini CLI** como herramienta principal de desarrollo  
Metodología: AFK Agent Workflow (Matt Pocock / AI Hero)
