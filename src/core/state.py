"""Estado compartido del pipeline de voz."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Literal


class StageStatus(Enum):
    IDLE = auto()
    PROCESSING = auto()
    ERROR = auto()


@dataclass
class ConversationTurn:
    role: Literal["user", "assistant"]
    text: str


@dataclass
class PipelineState:
    """Estado mutable del pipeline. Compartido entre todas las etapas."""

    # Estado de cada etapa
    mic_status: StageStatus = StageStatus.IDLE
    vad_status: StageStatus = StageStatus.IDLE
    stt_status: StageStatus = StageStatus.IDLE
    llm_status: StageStatus = StageStatus.IDLE
    tts_status: StageStatus = StageStatus.IDLE

    # Historial de la conversación
    history: list[ConversationTurn] = field(default_factory=list)

    # Si el pipeline está corriendo
    running: bool = False

    def add_turn(self, role: Literal["user", "assistant"], text: str) -> None:
        self.history.append(ConversationTurn(role=role, text=text))

    def reset(self) -> None:
        self.history.clear()
        self.running = False
        self.mic_status = StageStatus.IDLE
        self.vad_status = StageStatus.IDLE
        self.stt_status = StageStatus.IDLE
        self.llm_status = StageStatus.IDLE
        self.tts_status = StageStatus.IDLE
