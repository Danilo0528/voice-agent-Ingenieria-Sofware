import pytest
from unittest.mock import AsyncMock, patch
from src.llm.chat import ConversationLLM

@pytest.mark.asyncio
async def test_chat_returns_text_and_uses_system_prompt():
    # Arrange
    system_prompt = "Eres un asistente de voz"
    
    # Mock de la respuesta
    mock_completion = AsyncMock()
    mock_completion.choices = [AsyncMock(message=AsyncMock(content="Hola, ¿en qué puedo ayudarte?"))]
    
    with patch("src.llm.chat.AsyncOpenAI") as mock_client_class:
        mock_instance = mock_client_class.return_value
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        llm = ConversationLLM(system_prompt=system_prompt)
        
        # Act
        response = await llm.chat("Hola")
        
        # Assert
        assert response == "Hola, ¿en qué puedo ayudarte?"
        assert mock_instance.chat.completions.create.called
        
        # Verificar que se envió el system prompt y el mensaje del usuario
        args, kwargs = mock_instance.chat.completions.create.call_args
        messages = kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == system_prompt
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hola"

@pytest.mark.asyncio
async def test_history_maintenance():
    # Arrange
    mock_completion = AsyncMock()
    mock_completion.choices = [AsyncMock(message=AsyncMock(content="Respuesta 1"))]
    
    with patch("src.llm.chat.AsyncOpenAI") as mock_client_class:
        mock_instance = mock_client_class.return_value
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        llm = ConversationLLM()
        
        # Act - Primera llamada
        await llm.chat("Pregunta 1")
        
        # Mock para segunda llamada
        mock_completion.choices = [AsyncMock(message=AsyncMock(content="Respuesta 2"))]
        await llm.chat("Pregunta 2")
        
        # Assert
        assert mock_instance.chat.completions.create.call_count == 2
        
        # Verificar mensajes en la segunda llamada
        args, kwargs = mock_instance.chat.completions.create.call_args
        messages = kwargs["messages"]
        
        # System + P1 + R1 + P2
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Pregunta 1"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "Respuesta 1"
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "Pregunta 2"

@pytest.mark.asyncio
async def test_reset_clears_history():
    # Arrange
    mock_completion = AsyncMock()
    mock_completion.choices = [AsyncMock(message=AsyncMock(content="Respuesta 1"))]
    
    with patch("src.llm.chat.AsyncOpenAI") as mock_client_class:
        mock_instance = mock_client_class.return_value
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        llm = ConversationLLM()
        await llm.chat("Hola")
        # Act
        llm.reset()
        
        # Assert
        assert len(llm.history) == 0

@pytest.mark.asyncio
async def test_history_truncation():
    # Arrange
    max_history = 2 # Solo 2 turnos (4 mensajes: 2 user + 2 assistant)
    mock_completion = AsyncMock()
    mock_completion.choices = [AsyncMock(message=AsyncMock(content="Respuesta"))]
    
    with patch("src.llm.chat.AsyncOpenAI") as mock_client_class:
        mock_instance = mock_client_class.return_value
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        llm = ConversationLLM(max_history=max_history)
        
        # Act - Enviar 3 mensajes (supera max_history=2)
        await llm.chat("P1")
        await llm.chat("P2")
        await llm.chat("P3")
        
        # Assert
        # El historial debe tener solo los últimos 2 turnos (4 mensajes)
        # Turno 2 (P2, R2) y Turno 3 (P3, R3)
        assert len(llm.history) == 4
        assert llm.history[0]["content"] == "P2"
        assert llm.history[2]["content"] == "P3"

@pytest.mark.asyncio
async def test_ollama_compatibility():
    # Arrange
    base_url = "http://localhost:11434"
    with patch.dict("os.environ", {"OLLAMA_BASE_URL": base_url}):
        with patch("src.llm.chat.AsyncOpenAI") as mock_client_class:
            ConversationLLM()
            
            # Assert
            from unittest.mock import ANY
            mock_client_class.assert_called_once_with(
                api_key=ANY,
                base_url=base_url
            )
