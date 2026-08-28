from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.domain import (
    AgentPersona,
    IndependentEvaluation,
    CandidateProfile,
    JobDescription,
    TranscriptTurn,
    DebateArgument,
    StanceCalibration,
    EvidenceCitation,
    DimensionEvaluation,
    HireDecision,
    StanceType
)
from app.engine.evidence_engine import EvidenceEngine
from app.engine.barrier import IsolationBarrier
from app.services.llm_service import llm_service

class BaseEvaluatorAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        persona_name: str,
        agent_title: str,
        persona_type: AgentPersona,
        evaluation_dimensions: List[str]
    ):
        self.agent_id = agent_id
        self.persona_name = persona_name
        self.agent_title = agent_title
        self.persona_type = persona_type
        self.evaluation_dimensions = evaluation_dimensions

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Returns the specialized persona system prompt and rubrics."""
        pass

    def build_independent_user_prompt(
        self,
        candidate: CandidateProfile,
        jd: JobDescription,
        transcript_text: str
    ) -> str:
        """
        Builds the isolated evaluation prompt.
        CRITICAL: Contains ONLY candidate, JD, and transcript. Zero other agent context.
        """
        return f"""
EVALUATION ASSIGNMENT:
Job Description:
- Title: {jd.role_title} ({jd.level})
- Team: {jd.team}
- Core Responsibilities: {', '.join(jd.core_responsibilities)}
- Required Skills: {', '.join(jd.required_skills)}

Candidate Profile:
- Name: {candidate.name}
- Target Role: {candidate.target_role} ({candidate.target_level})
- Experience: {candidate.experience_years} years
- Resume Summary: {candidate.resume_summary}

Interview Transcript:
{transcript_text}

INSTRUCTIONS:
1. Conduct an exhaustive, independent evaluation strictly according to your persona role: {self.agent_title}.
2. Score your assigned dimensions from 1.0 to 10.0.
3. Every major strength or weakness claim MUST be grounded with direct verbatim quotes and the corresponding Turn ID.
4. Output your recommendation (STRONG_HIRE, HIRE, LEAN_HIRE, LEAN_REJECT, STRONG_REJECT) and confidence score (0.0 to 1.0).
"""

    @abstractmethod
    async def evaluate_independently(
        self,
        candidate: CandidateProfile,
        jd: JobDescription,
        turns: List[TranscriptTurn]
    ) -> IndependentEvaluation:
        """Runs the isolated evaluation."""
        pass

    @abstractmethod
    async def generate_debate_rebuttal(
        self,
        round_number: int,
        contention_topic: str,
        target_agent_id: str,
        target_agent_name: str,
        target_claim: str,
        turns: List[TranscriptTurn],
        evidence_engine: EvidenceEngine
    ) -> DebateArgument:
        """Generates a structured cross-examination challenge or defense."""
        pass

    @abstractmethod
    async def calibrate_stance(
        self,
        initial_evaluation: IndependentEvaluation,
        debate_arguments: List[DebateArgument],
        turns: List[TranscriptTurn]
    ) -> StanceCalibration:
        """Calibrates confidence and final stance following debate."""
        pass

