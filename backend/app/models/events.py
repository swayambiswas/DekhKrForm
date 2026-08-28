from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class EventType(str, Enum):
    SESSION_STATUS_CHANGED = "SESSION_STATUS_CHANGED"
    AGENT_THINKING = "AGENT_THINKING"
    AGENT_EVALUATION_COMPLETED = "AGENT_EVALUATION_COMPLETED"
    PHASE_COMPLETED = "PHASE_COMPLETED"
    DEBATE_ROUND_STARTED = "DEBATE_ROUND_STARTED"
    DEBATE_ARGUMENT_GENERATED = "DEBATE_ARGUMENT_GENERATED"
    EVIDENCE_VERIFIED = "EVIDENCE_VERIFIED"
    CONFIDENCE_CALIBRATED = "CONFIDENCE_CALIBRATED"
    SYNTHESIS_STREAM_CHUNK = "SYNTHESIS_STREAM_CHUNK"
    SYNTHESIS_COMPLETED = "SYNTHESIS_COMPLETED"
    SIMULATION_ERROR = "SIMULATION_ERROR"

class SimulationEvent(BaseModel):
    event_type: EventType
    session_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = Field(default_factory=dict)

