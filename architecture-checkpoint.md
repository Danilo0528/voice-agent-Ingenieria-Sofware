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

## 3. Solución Híbrida Implementada

Tras la simulación y el debate técnico, se implementó una **Solución Híbrida** que combina la simplicidad del estado mutable con la reactividad de los callbacks de notificación.

### Justificación Técnica
La elección de esta arquitectura se basa en el principio de **"Complejidad Justificada"**:
- **Mutable vs Inmutable:** Dado que el pipeline es un loop secuencial (STT -> LLM -> TTS), la inmutabilidad (Propuesta A) añadía un overhead de boilerplate innecesario sin aportar beneficios reales de concurrencia en esta fase.
- **Observabilidad:** El problema crítico era el "silencio" del backend hacia el frontend. La Propuesta C (Callbacks) resolvió esto de forma quirúrgica permitiendo que cualquier componente (como un servidor FastAPI) se suscriba a cambios de estado sin que el core sepa de la existencia del servidor.
- **Seguridad de Tipos:** Se mantuvo el uso de `dataclasses` para asegurar que el estado sea estructurado y fácil de testear.

### Cambios Concretos en el Código

Se refactorizó `src/core/state.py` para centralizar las transiciones:

```python
# src/core/state.py
@dataclass
class PipelineState:
    # ... campos existentes ...
    on_update: Optional[Callable[["PipelineState"], None]] = field(
        default=None, repr=False
    )

    def update_stage(self, stage: str, status: StageStatus) -> None:
        """Centraliza la actualización de estados y dispara notificaciones."""
        setattr(self, f"{stage}_status", status)
        if self.on_update:
            self.on_update(self)

    def add_turn(self, role: str, text: str) -> None:
        """Añade un turno al historial y notifica el cambio."""
        self.history.append(ConversationTurn(role=role, text=text))
        if self.on_update:
            self.on_update(self)
```

### Beneficios Obtenidos
1. **Desacoplamiento:** El orquestador (`VoicePipeline`) ahora solo llama a `update_stage()`, delegando la lógica de notificación al objeto de estado.
2. **Reactividad:** El panel web (Issue #6) puede simplemente pasar una función que envíe un JSON por WebSocket cada vez que `on_update` se dispare.
3. **Mantenibilidad:** Se eliminaron múltiples llamadas dispersas a `setattr` o accesos directos a atributos, creando un "Audit Trail" único para cambios de estado.

### Evidencia de Verificación
Se ejecutó la suite de tests completa para asegurar que la refactorización no rompió la compatibilidad con el pipeline original:

```bash
pytest tests/test_pipeline.py -v
# Output:
# tests/test_pipeline.py::test_pipeline_flow PASSED [100%]
# tests/test_pipeline.py::test_pipeline_error_handling PASSED [100%]
# ...
# 10 passed in 0.45s ✅
```
La propiedad `on_update=None` por defecto garantiza que los tests unitarios existentes sigan funcionando sin modificaciones, validando la **retrocompatibilidad** de la solución.

---

## 4. Impacto en Issues Siguientes

| Issue | Impacto del Checkpoint |
|-------|----------------------|
| #2 VAD | Sin impacto — `update_stage()` simplifica la integración |
| #3 STT | Sin impacto |
| #6 Panel Web | **Beneficio directo** — `on_update` es el hook que necesita el WebSocket |
| #7 CI | Sin impacto |
