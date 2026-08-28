import pytest
from datetime import datetime
from app.models.domain import (
    CandidateProfile,
    JobDescription,
    TranscriptTurn,
    IndependentEvaluation,
    HireDecision,
    StanceCalibration,
    EvidenceCitation,
    DebateRound,
    DebateArgument,
    StanceType
)
from app.engine.synthesis_engine import SynthesisEngine

@pytest.fixture
def base_context():
    cand = CandidateProfile(
        name="Alex Chen",
        target_role="Staff Distributed Systems Engineer",
        target_level="L6",
        experience_years=10,
        resume_summary="Staff engineer"
    )
    jd = JobDescription(
        role_title="Staff Distributed Systems Engineer",
        level="L6",
        team="Platform",
        core_responsibilities=["Architecture"],
        required_skills=["Distributed Systems"]
    )
    turns = [
        TranscriptTurn(turn_id=1, speaker="Interviewer", text="Tell us about your architecture."),
        TranscriptTurn(turn_id=2, speaker="Candidate", text="I designed the multi-region storage layer using Raft.")
    ]
    return cand, jd, turns

@pytest.mark.asyncio
async def test_non_averaging_bar_raiser_veto(base_context):
    cand, jd, turns = base_context
    engine = SynthesisEngine()

    now = datetime.utcnow()
    # 3 Agents gave HIRE/STRONG_HIRE, but Bar Raiser gave STRONG_REJECT with fatal red flag
    evaluations = {
        "technical_architect": IndependentEvaluation(
            agent_id="technical_architect",
            persona_name="Elena",
            agent_title="Technical Architect",
            generated_at=now,
            execution_hash="hash1",
            recommendation=HireDecision.STRONG_HIRE,
            confidence_score=0.9,
            summary_assessment="Great technical skills",
            dimension_scores=[],
            strengths=["Good"],
            weaknesses_or_risks=[],
            citations=[]
        ),
        "culture_lead": IndependentEvaluation(
            agent_id="culture_lead",
            persona_name="Marcus",
            agent_title="Culture Lead",
            generated_at=now,
            execution_hash="hash2",
            recommendation=HireDecision.STRONG_HIRE,
            confidence_score=0.95,
            summary_assessment="Great culture",
            dimension_scores=[],
            strengths=["Good"],
            weaknesses_or_risks=[],
            citations=[]
        ),
        "domain_specialist": IndependentEvaluation(
            agent_id="domain_specialist",
            persona_name="Priya",
            agent_title="Hiring Manager",
            generated_at=now,
            execution_hash="hash3",
            recommendation=HireDecision.HIRE,
            confidence_score=0.85,
            summary_assessment="Great delivery",
            dimension_scores=[],
            strengths=["Good"],
            weaknesses_or_risks=[],
            citations=[]
        ),
        "bar_raiser": IndependentEvaluation(
            agent_id="bar_raiser",
            persona_name="Kaelen",
            agent_title="Bar Raiser",
            generated_at=now,
            execution_hash="hash4",
            recommendation=HireDecision.STRONG_REJECT,
            confidence_score=0.99,
            summary_assessment="Fatal integrity / disqualifying claim falsification detected.",
            dimension_scores=[],
            strengths=[],
            weaknesses_or_risks=["Falsified system metrics"],
            citations=[]
        )
    }

    calibrations = [
        StanceCalibration(
            agent_id="bar_raiser",
            agent_name="Kaelen",
            initial_recommendation=HireDecision.STRONG_REJECT,
            final_recommendation=HireDecision.STRONG_REJECT,
            initial_confidence=0.99,
            final_confidence=0.99,
            confidence_delta=0.0,
            concessions_made=[],
            hardened_stances=["Veto maintained"],
            calibration_reasoning="Critical unmitigated integrity violation."
        )
    ]

    synthesis = await engine.generate_synthesis(
        session_id="test-veto-session",
        candidate=cand,
        jd=jd,
        evaluations=evaluations,
        debate_rounds=[],
        calibrations=calibrations,
        turns=turns
    )

    # In a naive average system: (10 + 10 + 8 + 1) / 4 = 7.25 -> HIRE.
    # In our Delphi synthesis: Bar Raiser veto MUST result in STRONG_REJECT.
    assert synthesis.final_decision == HireDecision.STRONG_REJECT
    assert "Bar Raiser veto" in synthesis.decision_summary
    assert "non-averaging" in synthesis.decision_summary.lower()

