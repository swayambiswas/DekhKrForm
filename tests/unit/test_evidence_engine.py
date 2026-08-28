import pytest
from app.models.domain import TranscriptTurn, EvidenceCitation
from app.engine.evidence_engine import EvidenceEngine

@pytest.fixture
def sample_turns():
    return [
        TranscriptTurn(
            turn_id=1,
            speaker="Interviewer",
            text="Welcome Alex! Let's start with a design for a globally distributed write-heavy audit logging pipeline at 500k ops/sec."
        ),
        TranscriptTurn(
            turn_id=2,
            speaker="Candidate",
            text="To handle 500k ops/sec write throughput without single-leader write lock contention, I'd decouple write ingestion from persistence using partitioned Kafka topics."
        ),
        TranscriptTurn(
            turn_id=3,
            speaker="Candidate",
            text="In distributed storage, CAP dictates choosing between consistency and availability. Durability is non-negotiable."
        )
    ]

def test_exact_verbatim_quote_verification(sample_turns):
    engine = EvidenceEngine(sample_turns)
    cit = EvidenceCitation(
        turn_id=2,
        speaker="Candidate",
        verbatim_quote="decouple write ingestion from persistence using partitioned Kafka topics",
        claim_supported="Candidate proposed decoupled message queue architecture."
    )
    verified = engine.verify_citation(cit)
    assert verified.is_verified is True
    assert verified.grounding_score == 1.0
    assert "Exact verbatim match" in verified.verification_notes

def test_fuzzy_quote_verification(sample_turns):
    engine = EvidenceEngine(sample_turns)
    # Slight variation in capitalization and punctuation
    cit = EvidenceCitation(
        turn_id=3,
        speaker="Candidate",
        verbatim_quote="In Distributed Storage CAP dictates choosing between Consistency and Availability",
        claim_supported="Candidate understands fundamental CAP theorem constraints."
    )
    verified = engine.verify_citation(cit)
    assert verified.is_verified is True
    assert verified.grounding_score >= 0.85

def test_turn_id_relocation(sample_turns):
    engine = EvidenceEngine(sample_turns)
    # Turn ID is mistakenly given as 1 instead of 3
    cit = EvidenceCitation(
        turn_id=1,
        speaker="Candidate",
        verbatim_quote="In distributed storage, CAP dictates choosing between consistency and availability.",
        claim_supported="Knowledge of CAP theorem."
    )
    verified = engine.verify_citation(cit)
    assert verified.is_verified is True
    assert verified.turn_id == 3  # Successfully relocated to Turn 3
    assert verified.speaker == "Candidate"

def test_hallucinated_quote_flagged(sample_turns):
    engine = EvidenceEngine(sample_turns)
    # Completely made-up quote
    cit = EvidenceCitation(
        turn_id=2,
        speaker="Candidate",
        verbatim_quote="I personally invented the Raft consensus algorithm in 2014.",
        claim_supported="Unverified false claim."
    )
    verified = engine.verify_citation(cit)
    assert verified.is_verified is False
    assert verified.grounding_score < 0.5
    assert "Flagged as unverified" in verified.verification_notes

