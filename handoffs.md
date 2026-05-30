# Bitácora de Transferencia de Contexto (Handoffs)

> Skill `/handoff` — Resúmenes ultra-compactos de sesiones del agente  
> Propósito: evitar degradación de contexto entre sesiones largas de Gemini CLI

---

## Handoff #1 — Sesión 1 → Sesión 2

**Fecha:** Sprint 1  
**Issues trabajadas:** #1 (Tracer Bullet Pipeline)  
**Cerradas:** #1 ✅

### ✅ Componentes Construidos

- `src/core/pipeline.py` — Clase `VoicePipeline` con método `async run(audio_bytes) -> bytes`
- `src/core/state.py` — `PipelineState` con enums de estado por etapa y historial de conversación
- `tests/test_pipeline.py` — 10 tests unitarios con mocks de STT, LLM y TTS. Todos en verde ✅

### 🏗️ Decisiones de Arquitectura Consolidadas

- **Protocolo entre etapas:** `asyncio.Queue` — sin threading, todo en el event loop
- **Interfaces como Protocolos:** `STTProvider`, `LLMProvider`, `TTSProvider` definidos con `typing.Protocol` para desacoplamiento total
- **Estado compartido:** `PipelineState` es mutable y se pasa por referencia al pipeline — no hay estado global
- **Manejo de silencio:** Si STT devuelve string vacío, el pipeline retorna `b""` sin llamar LLM ni TTS

### ⏳ Pendiente Exacto para Siguiente Sesión

- `src/audio/capture.py` — VAD con webrtcvad (Issue #2) — **desbloqueada**
- `src/stt/whisper_stt.py` — Whisper local (Issue #3) — **bloqueada hasta tener capture.py**
- `src/llm/chat.py` — Cliente LLM (Issue #4) — **desbloqueada, independiente**
- `src/tts/synthesizer.py` — TTS (Issue #5) — **desbloqueada, independiente**

### ⚠️ Contexto Crítico para el Agente Siguiente

```
El pipeline usa Protocolos de typing, NO clases base abstractas.
No importar ABC. Los mocks en tests usan AsyncMock directamente.
El audio de prueba es b"fake_audio" — no se necesita archivo WAV real.
run_in_executor se usará en STT y TTS para no bloquear el event loop.
```

---

## Handoff #2 — Sesión 2 → Sesión 3

**Fecha:** Sprint 1  
**Issues trabajadas:** #4 (LLM Client), #5 (TTS Synthesizer)  
**Cerradas:** #4 ✅, #5 ✅

### ✅ Componentes Construidos

- `src/llm/chat.py` — `ConversationLLM` con historial FIFO de hasta 10 turnos, compatible con OpenAI y Ollama
- `src/tts/synthesizer.py` — `TTSSynthesizer` con pyttsx3, corre en executor para no bloquear asyncio
- `tests/test_llm.py` — Tests con mock de `openai.AsyncOpenAI`. 6 tests en verde ✅
- `tests/test_tts.py` — Tests con mock de pyttsx3. 4 tests en verde ✅

### 🏗️ Decisiones de Arquitectura Consolidadas

- **LLM historial:** FIFO con `max_history=10` — al superar el límite se elimina el turno más antiguo
- **System prompt:** Hardcodeado en el constructor, configurable por parámetro
- **TTS temp files:** Se crean en `/tmp/` con `tempfile.mkstemp()` y se eliminan después de leer los bytes
- **Error handling:** Todos los métodos async tienen try/except que loggean con structlog y re-lanzan

### ⏳ Pendiente Exacto para Siguiente Sesión

- `src/audio/capture.py` — VAD (Issue #2) — **desbloqueada**
- `src/stt/whisper_stt.py` — Whisper (Issue #3) — **desbloqueada** (pipeline base ya existe)
- `src/api/server.py` + `frontend/index.html` — Panel web (Issue #6) — **HITL, requiere decisión humana**
- `.github/workflows/ci.yml` — CI (Issue #7) — **desbloqueada**

### ⚠️ Contexto Crítico para el Agente Siguiente

```
pyttsx3 es SÍNCRONO — siempre usar loop.run_in_executor(None, fn).
openai.AsyncOpenAI para el cliente LLM — NO openai.OpenAI síncrono.
El historial incluye el system prompt como primer mensaje con role="system".
Tests de TTS mockean engine.save_to_file y engine.runAndWait.
```

---

## Handoff #4 — Sesión 4 → Sesión 5

**Fecha:** Sprint 2  
**Issues trabajadas:** #7 (CI)  
**Cerradas:** #7 ✅

### ✅ Componentes Construidos

- **Orquestación:** `VoicePipeline` (async) y `PipelineState` con hook `on_update` para el frontend.
- **Audio/STT:** `AudioCapture` con VAD (30ms chunks) y `WhisperSTT` (modelo tiny, float32).
- **Cerebro/Voz:** `ConversationLLM` (historial FIFO) y `TTSSynthesizer` (vía `run_in_executor`).
- **Infra:** `.github/workflows/ci.yml` con linting (Ruff), tipos (Mypy) y tests (Pytest + Coverage).

### 🏗️ Decisiones de Arquitectura Consolidadas

- **Reactividad:** `PipelineState.update_stage()` centralizado con callbacks para facilitar integración con WebSockets.
- **Desacoplamiento:** Uso estricto de `typing.Protocol` para todos los proveedores de servicios.
- **Eficiencia:** Procesamiento local (Whisper tiny) para baja latencia educativa.

### ⏳ Pendiente para Siguiente Sesión

- **Issue #6 (Panel Web):** Desarrollo del servidor API (FastAPI) y la interfaz de usuario. Es el último bloque mayor del MVP.

### ⚠️ Contexto Crítico

```
El CI requiere libportaudio2 (instalado en el workflow). 
Todos los módulos de IA/Voz corren en executors para no congelar el loop de asyncio.
El pipeline está listo para ser consumido por un servidor web.
```
