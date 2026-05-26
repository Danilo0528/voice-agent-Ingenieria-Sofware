# Reporte de Control Arquitectónico Intermedio

> Skill `/improve-codebase-architecture`  
> Ejecutado tras completar Issues #1, #4, #5 (3 issues exitosas)  
> Propósito: detectar módulos superficiales y deuda técnica antes de continuar

---

## 1. Diagnóstico Inicial del Repositorio

El agente exploró el repositorio completo y detectó los siguientes hallazgos:

### Módulos Superficiales Detectados

| Archivo | Problema |
|---------|----------|
| `src/audio/capture.py` (pendiente) | Riesgo de mezclar VAD + captura + playback en un solo archivo plano |
| `src/core/pipeline.py` | El método `run()` hace STT+LLM+TTS secuencialmente — no hay manejo de cancelación |
| `src/core/state.py` | `PipelineState` es un dataclass mutable compartido — riesgo de race conditions si se añade concurrencia |

### Oportunidades de Profundización (Deepening Opportunities)

El agente propuso 4 candidatos. El equipo debatió y eligió el **#2** como prioritario:

1. `VoicePipeline.run()` — lógica de orquestación demasiado lineal, no cancellable
2. **`PipelineState` — estado compartido sin control de acceso** ← **ELEGIDO**
3. `ConversationLLM` — historial como lista simple, sin persistencia ni serialización
4. Ausencia de un `EventBus` — las etapas no pueden emitir eventos al frontend sin acoplamiento

**Justificación de la elección del #2:**  
`PipelineState` es el componente que más issues futuras tocarán (VAD, STT, API server, frontend). Si su interfaz es frágil ahora, cada nueva feature introducirá bugs difíciles de rastrear. Es el riesgo más alto para los próximos sprints.

---

## 2. Simulación Multi-Agente: 3 Propuestas de Interfaz

### Sub-Agente A — "Estado Inmutable con Eventos"

```python
# Propuesta A: PipelineState inmutable + EventEmitter para cambios
from dataclasses import dataclass, replace
from typing import Callable

@dataclass(frozen=True)
class PipelineState:
    mic_status: StageStatus = StageStatus.IDLE
    stt_status: StageStatus = StageStatus.IDLE
    llm_status: StageStatus = StageStatus.IDLE
    tts_status: StageStatus = StageStatus.IDLE
    history: tuple[ConversationTurn, ...] = ()
    running: bool = False

class StateMachine:
    def __init__(self):
        self._state = PipelineState()
        self._listeners: list[Callable] = []

    def transition(self, **kwargs) -> PipelineState:
        self._state = replace(self._state, **kwargs)
        for listener in self._listeners:
            listener(self._state)
        return self._state

    def on_change(self, fn: Callable):
        self._listeners.append(fn)
```

**Ventajas:** Thread-safe, observable, predecible. Patrón Redux.  
**Desventajas:** Más verbose, requiere refactor del pipeline existente.  
**Riesgo:** Overkill para el scope educativo del proyecto.

---

### Sub-Agente B — "Estado Mutable con Locks Asyncio"

```python
# Propuesta B: Estado mutable protegido con asyncio.Lock
import asyncio
from dataclasses import dataclass, field

@dataclass
class PipelineState:
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)
    mic_status: StageStatus = StageStatus.IDLE
    stt_status: StageStatus = StageStatus.IDLE
    llm_status: StageStatus = StageStatus.IDLE
    tts_status: StageStatus = StageStatus.IDLE
    history: list[ConversationTurn] = field(default_factory=list)
    running: bool = False

    async def set_stage(self, stage: str, status: StageStatus):
        async with self._lock:
            setattr(self, f"{stage}_status", status)

    async def add_turn(self, role: str, text: str):
        async with self._lock:
            self.history.append(ConversationTurn(role=role, text=text))
```

**Ventajas:** Seguro para concurrencia asyncio, minimal, compatible con código existente.  
**Desventajas:** Los locks añaden latencia, los tests deben ser async.  
**Riesgo:** Complejidad innecesaria si el pipeline siempre es secuencial.

---

### Sub-Agente C — "Estado Simple con Callbacks de Notificación"

```python
# Propuesta C: Estado mutable simple + callbacks opcionales para el frontend
from dataclasses import dataclass, field
from typing import Callable, Optional

@dataclass
class PipelineState:
    mic_status: StageStatus = StageStatus.IDLE
    stt_status: StageStatus = StageStatus.IDLE
    llm_status: StageStatus = StageStatus.IDLE
    tts_status: StageStatus = StageStatus.IDLE
    history: list[ConversationTurn] = field(default_factory=list)
    running: bool = False
    on_update: Optional[Callable[["PipelineState"], None]] = field(
        default=None, repr=False
    )

    def update_stage(self, stage: str, status: StageStatus):
        setattr(self, f"{stage}_status", status)
        if self.on_update:
            self.on_update(self)

    def add_turn(self, role: str, text: str):
        self.history.append(ConversationTurn(role=role, text=text))
        if self.on_update:
            self.on_update(self)
```

**Ventajas:** Mínimo cambio al código existente, conecta naturalmente con WebSockets del frontend.  
**Desventajas:** El callback puede crear acoplamiento si no se usa con cuidado.  
**Riesgo:** Bajo — es la solución más simple que funciona.

---

## 3. Recomendación Final — Solución Híbrida

El equipo evaluó las 3 propuestas y eligió una **solución híbrida entre B y C**:

**Decisión:** Mantener el estado mutable (no inmutable) pero añadir:
1. Un método `update_stage()` centralizado (de C) para evitar `setattr` disperso
2. Un callback opcional `on_update` (de C) para conectar con el WebSocket del frontend
3. Sin locks por ahora (descartar B) — el pipeline es secuencial, no hay concurrencia real

### Justificación Técnica

> "La propuesta A (inmutable) es elegante pero introduce complejidad innecesaria para un proyecto educativo con pipeline secuencial. La propuesta B (locks) protege contra concurrencia que aún no existe. La propuesta C con el método `update_stage()` resuelve el problema real: el frontend necesita saber cuándo cambia el estado, y hoy no hay ningún mecanismo para eso."

### Cambio Aplicado

```python
# src/core/state.py — versión mejorada post-checkpoint
@dataclass
class PipelineState:
    ...
    on_update: Optional[Callable[["PipelineState"], None]] = field(
        default=None, repr=False
    )

    def update_stage(self, stage: str, status: StageStatus) -> None:
        setattr(self, f"{stage}_status", status)
        if self.on_update:
            self.on_update(self)
```

### Verificación

```bash
pytest tests/ -v
# 10 passed in 0.43s ✅
```

Todos los tests existentes siguen en verde después del cambio. La nueva firma es
retrocompatible — `on_update=None` por defecto.

---

## 4. Impacto en Issues Siguientes

| Issue | Impacto del Checkpoint |
|-------|----------------------|
| #2 VAD | Sin impacto — `update_stage()` simplifica la integración |
| #3 STT | Sin impacto |
| #6 Panel Web | **Beneficio directo** — `on_update` es el hook que necesita el WebSocket |
| #7 CI | Sin impacto |
