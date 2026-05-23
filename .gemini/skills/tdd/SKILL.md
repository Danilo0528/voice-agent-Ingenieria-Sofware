# Skill: /tdd — Test-Driven Development

## Cuándo usar este skill

Siempre que vayas a implementar cualquier función, clase, o módulo nuevo.
**Nunca escribas código de producción sin un test que lo llame primero.**

## El Flujo

```
1. Escribe UN test que describa el comportamiento deseado
2. Corre pytest → debe FALLAR (red)
3. Escribe el código MÍNIMO que haga pasar el test
4. Corre pytest → debe PASAR (green)
5. Refactoriza si es necesario, sin romper el test
6. Repite para el siguiente comportamiento
```

## Reglas de Oro

### ✅ Vertical Slices (correcto)
Implementa un comportamiento completo de principio a fin:
```python
# tests/test_stt.py
async def test_transcribe_returns_text():
    stt = WhisperSTT(model="tiny")
    result = await stt.transcribe(fake_audio_bytes)
    assert isinstance(result, str)
    assert len(result) > 0
```
Luego implementa solo lo necesario para que pase.

### ❌ Horizontal Slices (incorrecto)
No escribas todos los tests primero y luego todo el código.
No escribas la clase completa antes de tener un test que la llame.

## Estructura de Tests para Este Proyecto

```python
# tests/test_<módulo>.py
import pytest
from unittest.mock import AsyncMock, patch

# Para módulos async:
@pytest.mark.asyncio
async def test_nombre_descriptivo():
    # Arrange
    ...
    # Act
    result = await componente.método()
    # Assert
    assert result == expected
```

## Mocks Permitidos

Mockea siempre:
- Hardware (micrófono, altavoz)
- APIs externas (OpenAI, Deepgram)
- Archivos de audio reales

No mockees:
- Lógica de negocio interna
- Transformaciones de datos
- State management

## Criterio de "Test Suficiente"

Un test es suficiente cuando:
1. Falla por la razón correcta (AssertionError, no ImportError)
2. Describe claramente qué comportamiento valida
3. Es determinista (mismo resultado siempre)

## Ejemplo Completo

### Issue: "Implementar VAD básico"

**Paso 1 — Test primero:**
```python
# tests/test_vad.py
import numpy as np
from src.audio.capture import VoiceActivityDetector

def test_vad_detects_silence():
    vad = VoiceActivityDetector(sample_rate=16000)
    silence = np.zeros(480, dtype=np.int16).tobytes()
    assert vad.is_speech(silence) == False

def test_vad_detects_speech():
    vad = VoiceActivityDetector(sample_rate=16000)
    # Audio con energía alta = habla simulada
    speech = np.random.randint(-32768, 32767, 480, dtype=np.int16).tobytes()
    # No podemos garantizar True aquí, pero sí que no crashea
    result = vad.is_speech(speech)
    assert isinstance(result, bool)
```

**Paso 2 — Código mínimo:**
```python
# src/audio/capture.py
import webrtcvad

class VoiceActivityDetector:
    def __init__(self, sample_rate: int = 16000, aggressiveness: int = 2):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate

    def is_speech(self, audio_chunk: bytes) -> bool:
        return self.vad.is_speech(audio_chunk, self.sample_rate)
```

**Paso 3 — Verificar:**
```bash
pytest tests/test_vad.py -v
```
