from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

class HireDecision(str, Enum):
    STRONG_HIRE = "STRONG_HIRE"
    HIRE = "HIRE"
    LEAN_HIRE = "LEAN_HIRE"
    LEAN_REJECT = "LEAN_REJECT"
    STRONG_REJECT = "STRONG_REJECT"

class StanceType(str, Enum):
    DEFEND = "DEFEND"
    CONCEDE = "CONCEDE"
    CHALLENGE = "CHALLENGE"
    CLARIFY = "CLARIFY"

class AgentPersona(str, Enum):
    TECHNICAL_ARCHITECT = "technical_architect"
    CULTURE_LEAD = "culture_lead"
    DOMAIN_SPECIALIST = "domain_specialist"
    BAR_RAISER = "bar_raiser"
    SUPREME_ARBITER = "supreme_arbiter"

class TranscriptTurn(BaseModel):
    turn_id: int = Field(..., description="1-indexed monotonic turn number")
    speaker: str = Field(..., description="'Interviewer' or 'Candidate'")
    timestamp_start: Optional[str] = None
    timestamp_end: Optional[str] = None
    text: str = Field(..., description="Verbatim dialogue content")
    token_count: Optional[int] = None

class CandidateProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    target_role: str
    target_level: str
    experience_years: int
    resume_summary: str
    key_skills: List[str] = Field(default_factory=list)

class JobDescription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role_title: str
    level: str
    team: str
    core_responsibilities: List[str]
    required_skills: List[str]
    evaluation_criteria: Dict[str, str] = Field(default_factory=dict)

class EvidenceCitation(BaseModel):
    citation_id: str = Field(default_factory=lambda: f"cit_{uuid.uuid4().hex[:8]}")
    turn_id: int = Field(..., description="Referenced turn ID in transcript")
    speaker: str = Field("Candidate", description="Speaker associated with this quote")
    verbatim_quote: str = Field(..., description="Exact or near-exact quote from transcript")
    claim_supported: str = Field(..., description="Agent claim supported by this quote")
    grounding_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Verification confidence score")
    is_verified: bool = Field(default=True, description="True if quote exists in transcript")
    verification_notes: Optional[str] = None

class DimensionEvaluation(BaseModel):
    dimension_name: str
    score: float = Field(..., ge=1.0, le=10.0, description="Score from 1 to 10")
    reasoning: str
    key_evidence: List[EvidenceCitation] = Field(default_factory=list)

class IndependentEvaluation(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: f"eval_{uuid.uuid4().hex[:8]}")
    agent_id: str
    persona_name: str
    agent_title: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_hash: str = Field(..., description="SHA-256 hash certifying zero-knowledge isolation")
    recommendation: HireDecision
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in assessment (0.0 to 1.0)")
    summary_assessment: str
    dimension_scores: List[DimensionEvaluation]
    strengths: List[str]
    weaknesses_or_risks: List[str]
    citations: List[EvidenceCitation] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)

class DebateArgument(BaseModel):
    argument_id: str = Field(default_factory=lambda: f"arg_{uuid.uuid4().hex[:8]}")
    round_number: int
    speaker_agent_id: str
    speaker_name: str
    target_agent_id: Optional[str] = None
    target_agent_name: Optional[str] = None
    contention_topic: str
    stance: StanceType
    argument_text: str
    evidence_citations: List[EvidenceCitation] = Field(default_factory=list)
    confidence_after_argument: float = Field(..., ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DebateRound(BaseModel):
    round_number: int
    round_title: str
    focus_topics: List[str]
    arguments: List[DebateArgument] = Field(default_factory=list)

class StanceCalibration(BaseModel):
    agent_id: str
    agent_name: str
    initial_recommendation: HireDecision
    final_recommendation: HireDecision
    initial_confidence: float
    final_confidence: float
    confidence_delta: float
    concessions_made: List[str] = Field(default_factory=list)
    hardened_stances: List[str] = Field(default_factory=list)
    calibration_reasoning: str

class FinalSynthesisDossier(BaseModel):
    session_id: str
    final_decision: HireDecision
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    decision_summary: str
    non_averaging_rationale: str = Field(
        ..., 
        description="Explicit explanation of how evidence, Bar Raiser vetoes, and debate shifts governed the decision rather than score averages"
    )
    calibrated_rubric_scores: Dict[str, float]
    primary_strengths: List[str]
    critical_risks_and_mitigations: List[str]
    decisive_evidence: List[EvidenceCitation]
    dissenting_opinions: List[Dict[str, str]]
    agent_calibrations: List[StanceCalibration]
    debate_summary: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SessionStatus(str, Enum):
    CREATED = "CREATED"
    INDEXING = "INDEXING"
    PHASE_1_INDEPENDENT_EVALUATION = "PHASE_1_INDEPENDENT_EVALUATION"
    PHASE_2_DEBATE = "PHASE_2_DEBATE"
    PHASE_3_SYNTHESIS = "PHASE_3_SYNTHESIS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class InterviewSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: SessionStatus = SessionStatus.CREATED
    candidate: CandidateProfile
    job_description: JobDescription
    transcript_turns: List[TranscriptTurn]
    independent_evaluations: Dict[str, IndependentEvaluation] = Field(default_factory=dict)
    debate_rounds: List[DebateRound] = Field(default_factory=list)
    synthesis: Optional[FinalSynthesisDossier] = None
    error_message: Optional[str] = None

