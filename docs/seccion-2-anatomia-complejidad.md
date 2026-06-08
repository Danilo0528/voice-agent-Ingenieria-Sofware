# Sección 2: Anatomía de la Complejidad

John Ousterhout define la complejidad como cualquier cosa relacionada con la estructura de un sistema de software que hace que sea difícil de entender y modificar. En este proyecto, luchamos contra ella aplicando tres pilares: **Módulos Profundos**, eliminación de **Módulos Superficiales** y prevención de **Information Leakage**.

## 🧠 Módulos Profundos (Deep Modules)

Un módulo profundo es aquel que ofrece una interfaz potente y sencilla, pero que oculta una implementación compleja.

### El caso de `PipelineState`
Originalmente, el estado era una simple `dataclass`. Cualquier parte del código podía modificar `stt_status` o `llm_status` directamente. Esto era un **módulo superficial**: no aportaba valor más allá de ser un contenedor de datos y permitía que la lógica de "qué pasa cuando cambia el estado" se dispersara por todo el código (**Information Leakage**).

**Antes (Módulo Superficial):**
```python
@dataclass
class PipelineState:
    stt_status: str = "idle"
    llm_status: str = "idle"

# En pipeline.py (Dispersión de lógica)
state.stt_status = "processing"
print(f"Update: {state}") 
# ¿Y si queremos avisar al frontend? Hay que añadir código en cada sitio que toque el estado.
```

**Después (Módulo Profundo):**
Tras el refactor del **Architecture Checkpoint**, lo convertimos en un módulo profundo:

```python
# src/core/state.py
def update_stage(self, stage: str, status: StageStatus) -> None:
    """Centraliza la actualización de estados y dispara notificaciones."""
    setattr(self, f"{stage}_status", status)
    # Abstracción potente: el que llama no sabe cómo se notifica
    if self.on_update:
        self.on_update(self)
    logger.debug(f"Stage {stage} updated to {status.value}")
```

**Por qué es profundo:** El usuario del módulo solo llama a `update_stage`. No necesita saber que existe un sistema de callbacks, ni cómo se disparan las notificaciones para el frontend (WebSockets), ni cómo se loguean los cambios. La interfaz es mínima (un método), el beneficio es máximo (consistencia total).

---

## 📉 Módulos Superficiales (Shallow Modules)

La IA a menudo tiende a crear demasiados archivos pequeños que solo añaden **Costo Cognitivo**. Si un módulo tiene una interfaz compleja pero hace muy poco, es un módulo superficial.

### Autocrítica: El caso de la Captura de Audio
Inicialmente, la IA generó dos archivos separados: `vad_manager.py` (para detectar silencio) y `audio_input.py` (para leer del micro). Cada uno tenía menos de 30 líneas. Para capturar una frase, el `VoicePipeline` tenía que coordinar manualmente ambos módulos:

**Complejidad en el Orquestador (Error):**
```python
# VoicePipeline
audio = audio_input.read()
if vad_manager.is_speech(audio):
    buffer.append(audio)
```

**Acción Humana:** Forzamos la unificación en `src/audio/capture.py`. Creamos una interfaz de alto nivel donde el pipeline solo llama a `capture_utterance()`. 

```python
# src/audio/capture.py - Unificación de un módulo que era superficial
async def capture_utterance(self) -> bytes:
    # Oculta la complejidad de:
    # 1. Gestión de flujos asíncronos de PyAudio
    # 2. Lógica de WebRTC VAD
    # 3. Buffering de pre-roll (capturar el inicio del habla)
    ...
```

Al ensanchar la "profundidad" de `AudioCapture`, eliminamos la necesidad de que el orquestador entienda qué es un "chunk de 30ms" o un "umbral de silencio". 

---

## 🚿 Ocultamiento de Información vs. Information Leakage

El **Information Leakage** ocurre cuando una decisión de diseño se refleja en múltiples módulos.

### El Error: Fuga de detalles de red
En las primeras versiones, el `VoicePipeline` intentaba manejar errores de conexión de la API de OpenAI. Esto era una fuga de información: el orquestador no debería saber que el LLM es una API de red.

### La Corrección: Abstracción basada en interfaces
Corregimos esto mediante el uso de `Protocols` (Interfaces estructurales de Python).

```python
class LLMProvider(Protocol):
    async def chat(self, user_message: str) -> str:
        ...
```

Ahora, si decidimos cambiar OpenAI por un modelo local de Ollama, el `VoicePipeline` no sufre cambios (**Zero Change Amplification**). El detalle de "cómo se genera el texto" está perfectamente oculto tras la interfaz.
