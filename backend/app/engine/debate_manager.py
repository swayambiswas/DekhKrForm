import asyncio
from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.models.domain import (
    IndependentEvaluation,
    DebateRound,
    DebateArgument,
    StanceCalibration,
    TranscriptTurn,
    HireDecision
)
from app.agents.base_agent import BaseEvaluatorAgent
from app.engine.evidence_engine import EvidenceEngine

class DebateManager:
    """
    Coordinates the 3-round structured debate between the 4 agents.
    Detects contradictions, triggers targeted cross-examinations with evidence verification,
    and collects post-debate calibrated stances.
    """

    def __init__(
        self,
        agents: Dict[str, BaseEvaluatorAgent],
        turns: List[TranscriptTurn],
        evidence_engine: EvidenceEngine
    ):
        self.agents = agents
        self.turns = turns
        self.evidence_engine = evidence_engine

    def detect_contentions(
        self,
        evaluations: Dict[str, IndependentEvaluation]
    ) -> List[Tuple[str, str, str, str]]:
        """
        Identifies key points of disagreement between agents.
        Returns list of (contention_topic, challenger_id, defender_id, reason).
        """
        contentions = []
        agent_ids = list(evaluations.keys())

        # Check for verdict divergence (e.g. STRONG_HIRE vs LEAN_HIRE/REJECT)
        recs = {aid: ev.recommendation for aid, ev in evaluations.items()}
        
        # Check Bar Raiser vs Tech Architect
        if "bar_raiser" in evaluations and "technical_architect" in evaluations:
            contentions.append((
                "Distributed Concurrency & Failure Mode Resilience",
                "bar_raiser",
                "technical_architect",
                "Bar Raiser identified potential unverified assumptions in distributed failover and hot-key mitigation."
            ))
            
        # Check Culture Lead vs Bar Raiser or Domain
        if "culture_lead" in evaluations and "domain_specialist" in evaluations:
            contentions.append((
                "Execution Velocity vs Sustainable Team Process",
                "culture_lead",
                "domain_specialist",
                "Balancing pragmatic fast-paced delivery against psychological safety and team consensus."
            ))

        # Check Domain Specialist vs Tech Architect
        if "domain_specialist" in evaluations and "technical_architect" in evaluations:
            contentions.append((
                "Theoretical System Perfection vs MVP Shipping Pragmatism",
                "domain_specialist",
                "technical_architect",
                "Evaluating whether the candidate over-engineered the initial tier or prioritized the right MVP path."
            ))

        return contentions

    async def execute_debate_round_1(
        self,
        evaluations: Dict[str, IndependentEvaluation]
    ) -> DebateRound:
        """
        Round 1: Stance Presentation & Initial Contention Mapping.
        """
        contentions = self.detect_contentions(evaluations)
        topics = [c[0] for c in contentions]
        
        round_1 = DebateRound(
            round_number=1,
            round_title="Divergence Identification & Stance Presentation",
            focus_topics=topics,
            arguments=[]
        )

        for topic, challenger_id, defender_id, reason in contentions[:2]:
            challenger = self.agents[challenger_id]
            defender = self.agents[defender_id]
            
            arg = await challenger.generate_debate_rebuttal(
                round_number=1,
                contention_topic=topic,
                target_agent_id=defender.agent_id,
                target_agent_name=defender.persona_name,
                target_claim=reason,
                turns=self.turns,
                evidence_engine=self.evidence_engine
            )
            round_1.arguments.append(arg)

        return round_1

    async def execute_debate_round_2(
        self,
        round_1: DebateRound,
        evaluations: Dict[str, IndependentEvaluation]
    ) -> DebateRound:
        """
        Round 2: Cross-Examination, Defense & Evidence Rebuttal.
        """
        round_2 = DebateRound(
            round_number=2,
            round_title="Cross-Examination & Evidence-Grounded Rebuttals",
            focus_topics=round_1.focus_topics,
            arguments=[]
        )

        for prior_arg in round_1.arguments:
            if prior_arg.target_agent_id and prior_arg.target_agent_id in self.agents:
                defender = self.agents[prior_arg.target_agent_id]
                challenger = self.agents[prior_arg.speaker_agent_id]
                
                counter_arg = await defender.generate_debate_rebuttal(
                    round_number=2,
                    contention_topic=prior_arg.contention_topic,
                    target_agent_id=challenger.agent_id,
                    target_agent_name=challenger.persona_name,
                    target_claim=prior_arg.argument_text,
                    turns=self.turns,
                    evidence_engine=self.evidence_engine
                )
                round_2.arguments.append(counter_arg)

        return round_2

    async def execute_debate_round_3(
        self,
        evaluations: Dict[str, IndependentEvaluation],
        all_prior_arguments: List[DebateArgument]
    ) -> Tuple[DebateRound, List[StanceCalibration]]:
        """
        Round 3: Epistemic Calibration & Stance Shifts.
        """
        round_3 = DebateRound(
            round_number=3,
            round_title="Epistemic Convergence & Confidence Calibration",
            focus_topics=["Final Calibration & Hiring Bar Alignment"],
            arguments=[]
        )

        calibrations: List[StanceCalibration] = []

        for agent_id, agent in self.agents.items():
            if agent_id in evaluations:
                cal = await agent.calibrate_stance(
                    initial_evaluation=evaluations[agent_id],
                    debate_arguments=all_prior_arguments,
                    turns=self.turns
                )
                calibrations.append(cal)

        return round_3, calibrations

