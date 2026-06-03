# Bitácora de Transferencia de Contexto (Handoffs)

> Skill `/handoff` — Resúmenes ultra-compactos de sesiones del agente  
> Propósito: evitar degradación de contexto entre sesiones largas de Gemini CLI

---

## Handoff #1 — Sesión 1 → Sesión 2

**Fecha:** Sprint 1  
**Issues trabajadas:** #1 (Tracer Bullet Pipeline)  
**Cerradas:** #1 ✅

### ✅ Componentes Construidos
- `src/core/pipeline.py` — Clase `VoicePipeline` con orquestación async.
- `src/core/state.py` — `PipelineState` para gestión de estados y conversación.
- `tests/test_pipeline.py` — Tests unitarios iniciales con mocks.

### 🏗️ Decisiones de Arquitectura Consolidadas
- **Protocolos:** Desacoplamiento total usando `typing.Protocol`.
- **Asyncio:** Uso de `asyncio.Queue` para comunicación entre etapas.
- **Estado:** Centralizado en `PipelineState` sin variables globales.

---

## Handoff #2 — Sesión 2 → Sesión 3

**Fecha:** Sprint 1  
**Issues trabajadas:** #4 (LLM Client), #5 (TTS Synthesizer)  
**Cerradas:** #4 ✅, #5 ✅

### ✅ Componentes Construidos
- `src/llm/chat.py` — `ConversationLLM` con historial FIFO y soporte OpenAI/Ollama.
- `src/tts/synthesizer.py` — `TTSSynthesizer` usando `pyttsx3` en executors.
- `tests/test_llm.py` & `tests/test_tts.py` — Cobertura completa de lógica conversacional y síntesis.

### 🏗️ Decisiones de Arquitectura Consolidadas
- **Historial:** Límite de 10 turnos (FIFO) para control de tokens.
- **Concurrencia:** `run_in_executor` para librerías síncronas (TTS).

---

## Handoff #3 — Sesión 3 → Sesión 4

**Fecha:** Sprint 2  
**Issues trabajadas:** #2 (Audio Capture), #3 (STT Whisper)  
**Cerradas:** #2 ✅, #3 ✅

### ✅ Componentes Construidos
- `src/audio/capture.py` — `AudioCapture` con VAD dinámico (webrtcvad).
- `src/stt/whisper_stt.py` — `WhisperSTT` con modelo local 'tiny' para latencia mínima.
- `tests/test_audio_capture.py` — Verificación de detección de silencio y habla.

### 🏗️ Decisiones de Arquitectura Consolidadas
- **Chunks:** Ventanas de 30ms para compatibilidad estricta con VAD industrial.
- **Limpieza:** Filtrado de audio <0.5s en STT para evitar alucinaciones de Whisper.

---

## Handoff #4 — Sesión 4 → Sesión 5

**Fecha:** Sprint 2  
**Issues trabajadas:** #7 (CI GitHub Actions)  
**Cerradas:** #7 ✅

### ✅ Componentes Construidos
- `.github/workflows/ci.yml` — Pipeline de CI completo (Lint, Types, Tests).
- `src/api/` — Estructura base para el servidor FastAPI.

### 🏗️ Decisiones de Arquitectura Consolidadas
- **Quality Gates:** Ruff para estilo, Mypy para seguridad de tipos (strict=True).
- **Entorno:** Automatización de dependencias de sistema (libportaudio2) en CI.

### ⏳ Pendiente Exacto para Siguiente Sesión
- **Issue #6 (Panel Web):** Implementar `src/api/server.py` y el frontend HTML/JS.
- **Integración Final:** Loop completo de extremo a extremo con hardware real.

### ⚠️ Contexto Crítico
```
El pipeline está 100% funcional en backend. El frontend debe consumir 
el callback PipelineState.on_update para reflejar cambios en tiempo real.
Se recomienda usar WebSockets para la comunicación bidireccional de estados.
```

