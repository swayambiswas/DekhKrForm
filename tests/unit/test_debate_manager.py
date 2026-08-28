import pytest
from app.models.domain import (
    CandidateProfile,
    JobDescription,
    TranscriptTurn,
    IndependentEvaluation,
    HireDecision
)
from app.agents.technical_agent import TechnicalArchitectAgent
from app.agents.culture_agent import CultureLeadershipAgent
from app.agents.domain_agent import DomainProductAgent
from app.agents.skeptic_agent import BarRaiserSkepticAgent
from app.engine.evidence_engine import EvidenceEngine
from app.engine.debate_manager import DebateManager

@pytest.mark.asyncio
async def test_debate_manager_flow():
    turns = [
        TranscriptTurn(turn_id=1, speaker="Interviewer", text="How do you handle split brain?"),
        TranscriptTurn(turn_id=2, speaker="Candidate", text="Using Raft consensus coordinator with odd quorum.")
    ]
    agents = {
        "technical_architect": TechnicalArchitectAgent(),
        "culture_lead": CultureLeadershipAgent(),
        "domain_specialist": DomainProductAgent(),
        "bar_raiser": BarRaiserSkepticAgent()
    }
    evidence_engine = EvidenceEngine(turns)
    debate_manager = DebateManager(agents, turns, evidence_engine)

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

    # Generate initial evaluations
    evals = {}
    for aid, agent in agents.items():
        evals[aid] = await agent.evaluate_independently(cand, jd, turns)

    # Round 1: Divergence detection
    round_1 = await debate_manager.execute_debate_round_1(evals)
    assert round_1.round_number == 1
    assert len(round_1.arguments) > 0

    # Round 2: Cross-examination rebuttal
    round_2 = await debate_manager.execute_debate_round_2(round_1, evals)
    assert round_2.round_number == 2
    assert len(round_2.arguments) > 0

    # Round 3: Stance calibration
    all_args = round_1.arguments + round_2.arguments
    round_3, calibrations = await debate_manager.execute_debate_round_3(evals, all_args)
    assert round_3.round_number == 3
    assert len(calibrations) == 4
    for cal in calibrations:
        assert cal.final_confidence > 0.0

