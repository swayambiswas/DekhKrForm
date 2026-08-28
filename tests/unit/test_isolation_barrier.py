import pytest
import asyncio
from datetime import datetime
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
from app.engine.barrier import IsolationBarrier

@pytest.fixture
def candidate_and_jd():
    cand = CandidateProfile(
        name="Alex Chen",
        target_role="Staff Distributed Systems Engineer",
        target_level="L6",
        experience_years=10,
        resume_summary="Staff engineer at cloud scale company."
    )
    jd = JobDescription(
        role_title="Staff Distributed Systems Engineer",
        level="L6",
        team="Platform",
        core_responsibilities=["Architecture", "Mentorship"],
        required_skills=["Distributed Systems", "Storage"]
    )
    turns = [
        TranscriptTurn(turn_id=1, speaker="Interviewer", text="Hello Alex."),
        TranscriptTurn(turn_id=2, speaker="Candidate", text="Hello, let's discuss Kafka partition sharding and Raft quorum.")
    ]
    return cand, jd, turns

@pytest.mark.asyncio
async def test_four_agents_parallel_independent_execution(candidate_and_jd):
    cand, jd, turns = candidate_and_jd
    agents = [
        TechnicalArchitectAgent(),
        CultureLeadershipAgent(),
        DomainProductAgent(),
        BarRaiserSkepticAgent()
    ]

    tasks = [agent.evaluate_independently(cand, jd, turns) for agent in agents]
    evaluations = await IsolationBarrier.execute_in_parallel(tasks)

    assert len(evaluations) == 4
    # Ensure all 4 distinct personas evaluated
    agent_ids = {e.agent_id for e in evaluations}
    assert agent_ids == {"technical_architect", "culture_lead", "domain_specialist", "bar_raiser"}

    # Validate isolation hashes
    assert IsolationBarrier.verify_isolation_compliance(evaluations) is True

    # Validate that each evaluation has unique execution hash and generated_at
    hashes = [e.execution_hash for e in evaluations]
    assert len(set(hashes)) == 4

