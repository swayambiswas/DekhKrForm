import pytest
from app.models.domain import (
    InterviewSession,
    CandidateProfile,
    JobDescription,
    TranscriptTurn,
    SessionStatus,
    HireDecision
)
from app.engine.orchestrator import SimulationOrchestrator

@pytest.mark.asyncio
async def test_end_to_end_orchestrator_simulation():
    turns = [
        TranscriptTurn(turn_id=1, speaker="Interviewer", text="Welcome! How would you scale an event streaming bus?"),
        TranscriptTurn(turn_id=2, speaker="Candidate", text="I'd use partitioned Kafka clusters with replication factor of 3 and snappy compression."),
        TranscriptTurn(turn_id=3, speaker="Interviewer", text="What trade-offs did you face?"),
        TranscriptTurn(turn_id=4, speaker="Candidate", text="Higher write latency for durability vs ephemeral in-memory queues.")
    ]

    session = InterviewSession(
        title="Staff Engineer Test Session",
        candidate=CandidateProfile(
            name="Alex Chen",
            target_role="Staff Distributed Systems Engineer",
            target_level="L6",
            experience_years=10,
            resume_summary="Staff engineer"
        ),
        job_description=JobDescription(
            role_title="Staff Distributed Systems Engineer",
            level="L6",
            team="Platform",
            core_responsibilities=["Architecture"],
            required_skills=["Distributed Systems"]
        ),
        transcript_turns=turns,
        status=SessionStatus.CREATED
    )

    events_captured = []
    orchestrator = SimulationOrchestrator(
        event_emitter=lambda ev: events_captured.append(ev)
    )

    completed_session = await orchestrator.run_full_simulation(session)

    # Validate full progression
    assert completed_session.status == SessionStatus.COMPLETED
    assert len(completed_session.independent_evaluations) == 4
    assert len(completed_session.debate_rounds) == 3
    assert completed_session.synthesis is not None
    assert completed_session.synthesis.final_decision in [HireDecision.STRONG_HIRE, HireDecision.HIRE]
    assert len(events_captured) > 10

