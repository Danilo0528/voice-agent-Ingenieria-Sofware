import pytest
import sys
from unittest.mock import MagicMock, patch, mock_open

# Mock pyttsx3 module before importing the synthesizer
mock_pyttsx3 = MagicMock()
sys.modules["pyttsx3"] = mock_pyttsx3

from src.tts.synthesizer import TTSSynthesizer  # noqa: E402

@pytest.mark.asyncio
async def test_synthesize_returns_bytes():
    """Valida que el sintetizador devuelva bytes de audio."""
    # Arrange
    text = "Hola, esto es una prueba."
    synth = TTSSynthesizer()
    
    # Configuramos el mock de pyttsx3
    mock_engine = MagicMock()
    mock_pyttsx3.init.return_value = mock_engine
        
    # Simulamos que save_to_file se llama y luego runAndWait
    # En la implementación real, save_to_file creará un archivo que luego leeremos.
    # Para el test, podemos mockear la lectura del archivo.
    
    with patch("builtins.open", mock_open(read_data=b"fake audio data")):
        with patch("os.remove"): # Evitar que intente borrar un archivo real
            with patch("os.path.exists", return_value=True):
                # Act
                result = await synth.synthesize(text)
                
                # Assert
                assert isinstance(result, bytes)
                assert result == b"fake audio data"
                mock_engine.save_to_file.assert_called_once()
                mock_engine.runAndWait.assert_called_once()

def test_init_sets_properties():
    """Valida que el init guarde correctamente rate, volume y voice_id."""
    synth = TTSSynthesizer(rate=200, volume=0.8, voice_id="spanish_voice")
    assert synth.rate == 200
    assert synth.volume == 0.8
    assert synth.voice_id == "spanish_voice"

@pytest.mark.asyncio
async def test_synthesize_sets_engine_properties():
    """Valida que se configuren las propiedades en el engine de pyttsx3."""
    synth = TTSSynthesizer(rate=200, volume=0.8, voice_id="test_voice")
    
    mock_engine = MagicMock()
    mock_pyttsx3.init.return_value = mock_engine
    
    with patch("builtins.open", mock_open(read_data=b"data")):
        with patch("os.remove"):
            with patch("os.path.exists", return_value=True):
                await synth.synthesize("test")
                
                # Verificar que setProperty fue llamado con los valores correctos
                mock_engine.setProperty.assert_any_call('rate', 200)
                mock_engine.setProperty.assert_any_call('volume', 0.8)
                mock_engine.setProperty.assert_any_call('voice', "test_voice")

@pytest.mark.asyncio
async def test_get_available_voices():
    """Valida que devuelva una lista de voces."""
    synth = TTSSynthesizer()
    
    mock_engine = MagicMock()
    mock_pyttsx3.init.return_value = mock_engine
    
    # Mocking voices property
    mock_voice = MagicMock()
    mock_voice.id = "voice_id_1"
    mock_voice.name = "Voice Name"
    mock_voice.languages = ["es-ES"]
    mock_engine.getProperty.return_value = [mock_voice]
    
    voices = await synth.get_available_voices()
    
    assert len(voices) == 1
    assert voices[0]["id"] == "voice_id_1"
    assert voices[0]["name"] == "Voice Name"
    mock_engine.getProperty.assert_called_with("voices")
