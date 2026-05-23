# [AFK] Cliente LLM con Historial de Conversación

**Labels:** `feature`, `llm`

## Descripción

Implementar el cliente LLM que mantiene el historial de la conversación y genera
respuestas en texto para el agente de voz.

## Criterios de Aceptación

- [ ] `ConversationLLM.chat(user_message)` devuelve respuesta de texto
- [ ] Mantiene historial de la conversación en memoria (últimos N turnos)
- [ ] Compatible con OpenAI API y Ollama (local) mediante variable de entorno
- [ ] Respuestas son cortas por defecto (max 2-3 oraciones, apropiado para voz)
- [ ] Tests unitarios con mock del cliente OpenAI
- [ ] Método `reset()` para limpiar el historial

## Interface

```python
class ConversationLLM:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        system_prompt: str = "Eres un asistente de voz amigable...",
        max_history: int = 10,
    ):
        ...

    async def chat(self, user_message: str) -> str:
        """Envía mensaje y devuelve respuesta del LLM."""
        ...

    def reset(self) -> None:
        """Limpia el historial de conversación."""
        ...
```

## System Prompt por Defecto

```
Eres un asistente de voz conversacional. Responde de forma concisa y natural,
como si estuvieras hablando, no escribiendo. Máximo 2-3 oraciones por respuesta.
Evita listas y formatos markdown.
```

## Notas Técnicas

- Usar `openai.AsyncOpenAI` para compatibilidad con async/await
- Para Ollama: misma API que OpenAI, cambiar `base_url`
- Truncar historial cuando exceda `max_history` turnos (FIFO)
- Medir y loggear latencia de la llamada API

## Archivos a Crear

- `src/llm/chat.py`
- `tests/test_llm.py`

## Variables de Entorno

```env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
OLLAMA_BASE_URL=http://localhost:11434  # alternativa local
```
