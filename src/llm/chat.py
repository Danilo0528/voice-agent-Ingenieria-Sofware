import os
from typing import Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
import structlog

logger = structlog.get_logger()

class ConversationLLM:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        system_prompt: str = "Eres un asistente de voz conversacional. Responde de forma concisa y natural, como si estuvieras hablando, no escribiendo. Máximo 2-3 oraciones por respuesta. Evita listas y formatos markdown.",
        max_history: int = 10,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.history: list[dict[str, Any]] = []
        
        api_key = os.getenv("OPENAI_API_KEY", "sk-fake")
        base_url = os.getenv("OLLAMA_BASE_URL")
        
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def chat(self, user_message: str) -> str:
        import time
        start_time = time.perf_counter()
        
        # Añadir mensaje del usuario al historial
        self.history.append({"role": "user", "content": user_message})
            
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history) # type: ignore[arg-type]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            latency = time.perf_counter() - start_time
            ai_response = response.choices[0].message.content or ""
            
            logger.info("llm_response_generated", 
                        latency_ms=round(latency * 1000, 2),
                        model=self.model)
            
            # Añadir respuesta del asistente al historial
            self.history.append({"role": "assistant", "content": ai_response})
            
            # Truncar historial si excede max_history turnos (cada turno son 2 mensajes)
            if len(self.history) > self.max_history * 2:
                self.history = self.history[-(self.max_history * 2):]
                
            return ai_response
        except Exception as e:
            logger.error("llm_request_failed", error=str(e))
            raise

    def reset(self) -> None:
        self.history = []
