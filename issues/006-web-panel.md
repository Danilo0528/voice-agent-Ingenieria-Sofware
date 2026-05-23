# [HITL] Panel de Monitoreo Web con FastAPI + WebSockets

**Labels:** `feature`, `frontend`, `backend`

## Descripción

Crear un panel web en tiempo real que muestre el estado del pipeline de voz,
las transcripciones y las respuestas del agente.

> ⚠️ **[HITL]** — Esta issue requiere decisiones de diseño de UI. El agente no debe
> resolverla de forma autónoma.

## Criterios de Aceptación

- [ ] `python -m src.api.server` levanta un servidor en `http://localhost:8000`
- [ ] El frontend muestra el estado actual de cada etapa del pipeline
- [ ] Las transcripciones aparecen en tiempo real via WebSocket
- [ ] Panel incluye botones: Start, Stop, Reset conversación
- [ ] El pipeline se puede controlar desde el panel (no solo desde terminal)

## Diseño del Panel

```
┌─────────────────────────────────────────┐
│  🎙️ VoiceAgent Monitor                  │
├─────────────────────────────────────────┤
│  Pipeline Status:                        │
│  [MIC: 🟢] [VAD: 🟡] [STT: ⚪] ...      │
├─────────────────────────────────────────┤
│  Conversation:                           │
│  👤 User: "Hola, ¿cómo estás?"          │
│  🤖 Agent: "¡Bien! ¿En qué te ayudo?"   │
├─────────────────────────────────────────┤
│  [▶ Start] [⏹ Stop] [🔄 Reset]          │
└─────────────────────────────────────────┘
```

## Arquitectura

```
FastAPI server
├── GET /          → sirve index.html
├── WebSocket /ws  → eventos del pipeline en tiempo real
└── POST /control  → start | stop | reset

Eventos WebSocket (JSON):
{"type": "stage_update", "stage": "stt", "status": "processing"}
{"type": "transcript", "text": "hola mundo", "role": "user"}
{"type": "response", "text": "hola!", "role": "assistant"}
```

## Archivos a Crear

- `src/api/server.py`
- `frontend/index.html` (HTML + JS vanilla, sin frameworks)
