from typing import Dict, List
from app.models.domain import (
    FinalSynthesisDossier,
    IndependentEvaluation,
    DebateRound,
    StanceCalibration,
    CandidateProfile,
    JobDescription,
    TranscriptTurn
)
from app.agents.arbiter_agent import SupremeArbiterAgent

class SynthesisEngine:
    """
    Coordinates the final deliberation and produces the non-averaged synthesis dossier.
    """
    def __init__(self):
        self.arbiter = SupremeArbiterAgent()

    async def generate_synthesis(
        self,
        session_id: str,
        candidate: CandidateProfile,
        jd: JobDescription,
        evaluations: Dict[str, IndependentEvaluation],
        debate_rounds: List[DebateRound],
        calibrations: List[StanceCalibration],
        turns: List[TranscriptTurn]
    ) -> FinalSynthesisDossier:
        return self.arbiter.synthesize(
            session_id=session_id,
            candidate=candidate,
            jd=jd,
            evaluations=evaluations,
            debate_rounds=debate_rounds,
            calibrations=calibrations,
            turns=turns
        )

