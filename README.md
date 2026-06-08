# 🎙️ VoiceAgent — Agente de Voz Conversacional Mínimo

## 📖 Software Journey - Entrega Final (Tarea 3)

La bitácora completa del proyecto y auditoría arquitectónica está aquí:

→ **[Ver Software Journey](/docs/index.md)**

> Python puro · asyncio · Sin frameworks de voz · Arquitectura observable

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-En%20Desarrollo-yellow.svg)]()

---

## 🎯 Objetivo

Construir un agente de voz conversacional **desde cero en Python puro** para entender
la arquitectura interna de frameworks como Pipecat y LiveKit Agents.

```
Micrófono → VAD → STT → LLM → TTS → Altavoz
```

Cada etapa es un módulo independiente conectado mediante **colas asyncio**,
lo que hace el sistema completamente observable y modificable.

---

## 🏗️ Arquitectura

```
voice-agent/
├── src/
│   ├── core/
│   │   ├── pipeline.py      # Orquestador principal del loop (✅ LISTO)
│   │   └── state.py         # Estado compartido de la conversación (✅ LISTO)
│   ├── audio/
│   │   ├── capture.py       # Captura micrófono + VAD (✅ LISTO)
│   │   └── playback.py      # Reproducción de audio (⏳ PENDIENTE)
│   ├── stt/
│   │   └── whisper_stt.py   # Speech-to-Text (Whisper local) (✅ LISTO)
│   ├── llm/
│   │   └── chat.py          # Cliente LLM (OpenAI / Ollama) (✅ LISTO)
│   ├── tts/
│   │   └── synthesizer.py   # Text-to-Speech (✅ LISTO)
│   └── api/
│       └── server.py        # FastAPI + WebSockets (⏳ PRÓXIMAMENTE)
├── frontend/
│   └── index.html           # Panel de monitoreo (⏳ PRÓXIMAMENTE)
├── tests/
│   ├── test_pipeline.py
│   ├── test_stt.py
│   └── test_tts.py
├── issues/
│   ├── prd.md               # Product Requirements Document
│   └── done/                # Issues completadas
├── ralph/
│   ├── prompt.md            # Instrucciones del agente
│   └── once.sh              # Script del agente autónomo
├── .gemini/
│   └── skills/
│       ├── grill-me/        # Skill de interrogación del brief
│       ├── write-a-prd/     # Skill de generación de PRD
│       ├── prd-to-issues/   # Skill de conversión PRD → issues
│       └── tdd/             # Skill de TDD
├── docs/
│   └── CLIENT_BRIEF.md
├── pyproject.toml
└── README.md
```

---

## 🤖 Flujo de Trabajo con Gemini CLI (AFK Agent Methodology)

Este proyecto sigue la metodología **AFK Agent** del workshop
[AI Engineer Workshop 2026](https://www.aihero.dev/ai-engineer-workshop-2026~dwnll)
de Matt Pocock, adaptada a **Gemini CLI** (gratuito).

### Los 5 pasos del flujo

```
1. Setup repo       → Crear estructura base del proyecto
        ↓
2. /grill-me        → Gemini interroga el brief, clarifica ambigüedades
        ↓
3. /write-a-prd     → Gemini genera issues/prd.md con todos los requisitos
        ↓
4. /prd-to-issues   → PRD se convierte en issues de GitHub (kanban)
        ↓
5. ralph/once.sh    → Gemini resuelve issues autónomamente (TDD loop)
```

### Adaptación a Gemini CLI (gratuito)

Como **Gemini CLI es gratuito**, lo usamos en lugar de Claude Code.
Las skills están en `.gemini/skills/` en lugar de `.claude/skills/`.

| Componente Original (Claude Code) | Adaptación (Gemini CLI) |
|----------------------------------|------------------------|
| `.claude/skills/` | `.gemini/skills/` |
| `claude` CLI | `gemini` CLI |
| `--permission-mode acceptEdits` | `--yolo` |

### Instalar Gemini CLI

```bash
npm install -g @google/gemini-cli
gemini auth   # autenticarse con tu cuenta Google
```

---

## ⚡ Instalación

```bash
git clone https://github.com/TU_USUARIO/voice-agent.git
cd voice-agent
pip install -e ".[dev]"
cp .env.example .env
# Edita .env con tus API keys
```

---

## 🚀 Uso

```bash
# Iniciar el pipeline
python -m src.core.pipeline

# Iniciar con panel web
python -m src.api.server
# Abrir http://localhost:8000
```

---

## 🧪 Tests

```bash
pytest
pytest --cov=src --cov-report=html
```

---

## 📚 Referencias

- [AI Engineer Workshop 2026 — Matt Pocock](https://www.aihero.dev/ai-engineer-workshop-2026~dwnll)
- [Running Your AFK Agent](https://www.aihero.dev/running-your-afk-agent-a9l1u)
- [Pipecat — Voice AI Framework](https://github.com/pipecat-ai/pipecat)
- [Whisper — OpenAI STT](https://github.com/openai/whisper)

---

## 📄 Licencia

MIT
