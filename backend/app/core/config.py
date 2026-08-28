import os
from typing import Optional

class Settings:
    PROJECT_NAME: str = "Multi-Agent AI Interview Panel Simulator"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # LLM Settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")
    TEMPERATURE: float = 0.2
    
    # Execution Guardrails
    MAX_DEBATE_ROUNDS: int = 3
    MIN_GROUNDING_THRESHOLD: float = 0.75
    ENABLE_STRICT_ISOLATION: bool = True
    SIMULATION_LATENCY_MS: int = int(os.getenv("SIMULATION_LATENCY_MS", "300"))

settings = Settings()

