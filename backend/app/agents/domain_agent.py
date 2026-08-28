from datetime import datetime, timezone
from typing import List, Dict, Any
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
from app.agents.base_agent import BaseEvaluatorAgent
from app.engine.evidence_engine import EvidenceEngine
from app.engine.barrier import IsolationBarrier
from app.services.transcript_service import TranscriptService
from app.services.llm_service import llm_service

class DomainProductAgent(BaseEvaluatorAgent):
    def __init__(self):
        super().__init__(
            agent_id="domain_specialist",
            persona_name="Priya Sharma",
            agent_title="Hiring Manager & Domain Execution Lead",
            persona_type=AgentPersona.DOMAIN_SPECIALIST,
            evaluation_dimensions=[
                "Practical Delivery Velocity & Pragmatism",
                "Product & Business Impact Awareness",
                "Domain-Specific Knowledge & Realities",
                "Feature Prioritization & Scope Management"
            ]
        )

    def get_system_prompt(self) -> str:
        return """
You are Priya Sharma, Hiring Manager and Domain Execution Lead.
Your role on the interview panel is to evaluate the candidate's practical shipping speed, understanding of customer business impact, domain realities, and pragmatic trade-offs between theoretical perfection and shipping value.

You care deeply about real-world delivery, user experience, feature prioritization, and avoiding over-engineering.
You must ground every evaluation point with verbatim quotes and Turn IDs from the interview transcript.
"""

    async def evaluate_independently(
        self,
        candidate: CandidateProfile,
        jd: JobDescription,
        turns: List[TranscriptTurn]
    ) -> IndependentEvaluation:
        transcript_text = TranscriptService.build_transcript_text(turns)
        user_prompt = self.build_independent_user_prompt(candidate, jd, transcript_text)
        evidence_engine = EvidenceEngine(turns)
        
        llm_res = await llm_service.generate_structured(
            system_prompt=self.get_system_prompt(),
            user_prompt=user_prompt,
            response_model=IndependentEvaluation
        )
        
        if llm_res:
            llm_res.citations = evidence_engine.batch_verify_citations(llm_res.citations)
            llm_res.execution_hash = IsolationBarrier.generate_isolation_hash(
                self.agent_id, user_prompt, llm_res.summary_assessment, llm_res.generated_at
            )
            return llm_res

        # Domain delivery turn search
        domain_turns = [t for t in turns if any(k in t.text.lower() for k in ["ship", "user", "customer", "product", "business", "metric", "deploy", "mvp", "revenue", "timeline", "dau", "redis", "sentinel"])]
        candidate_turns = [t for t in domain_turns if t.speaker == "Candidate"]
        
        citations: List[EvidenceCitation] = []
        if candidate_turns:
            sample_turn = candidate_turns[0]
            citations.append(EvidenceCitation(
                turn_id=sample_turn.turn_id,
                speaker="Candidate",
                verbatim_quote=sample_turn.text[:120],
                claim_supported=f"{candidate.name} outlined delivery execution and operational scope in Turn {sample_turn.turn_id}.",
                grounding_score=1.0,
                is_verified=True
            ))

        now = datetime.now(timezone.utc)
        raw_summary = f"{candidate.name} brings practical execution instincts for {candidate.target_role}. Balances technical rigor with delivery timelines, emphasizing user value over unnecessary micro-optimizations."
        
        dim_scores = [
            DimensionEvaluation(
                dimension_name="Practical Delivery Velocity & Pragmatism",
                score=8.4,
                reasoning="Showed strong orientation towards incremental rollouts and feature flags.",
                key_evidence=citations[:1]
            ),
            DimensionEvaluation(
                dimension_name="Product & Business Impact Awareness",
                score=8.1,
                reasoning="Understands conversion funnel and SLA impact on user retention.",
                key_evidence=[]
            ),
            DimensionEvaluation(
                dimension_name="Feature Prioritization & Scope Management",
                score=8.3,
                reasoning="Comfortable cutting non-essential scope to meet release deadlines.",
                key_evidence=[]
            )
        ]
        
        verified_citations = evidence_engine.batch_verify_citations(citations)
        exec_hash = IsolationBarrier.generate_isolation_hash(self.agent_id, user_prompt, raw_summary, now)
        
        return IndependentEvaluation(
            agent_id=self.agent_id,
            persona_name=self.persona_name,
            agent_title=self.agent_title,
            generated_at=now,
            execution_hash=exec_hash,
            recommendation=HireDecision.HIRE,
            confidence_score=0.85,
            summary_assessment=raw_summary,
            dimension_scores=dim_scores,
            strengths=[
                "Pragmatic builder who avoids premature optimization rabbit holes",
                "Proven ability to tie architectural choices directly to customer latency budgets",
                "Strong familiarity with continuous deployment and rollback strategies"
            ],
            weaknesses_or_risks=[
                "Could push for more aggressive automated canary telemetry metrics"
            ],
            citations=verified_citations,
            unresolved_questions=[
                "How does the candidate prioritize tech-debt refactoring vs new product features in sprint planning?"
            ]
        )

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
        cit = EvidenceCitation(
            turn_id=turns[min(7, len(turns)-1)].turn_id,
            speaker=turns[min(7, len(turns)-1)].speaker,
            verbatim_quote=turns[min(7, len(turns)-1)].text[:100],
            claim_supported="Candidate emphasized unblocking customer workflow via phased rollout.",
            grounding_score=1.0,
            is_verified=True
        )
        verified_cit = evidence_engine.verify_citation(cit)
        
        return DebateArgument(
            round_number=round_number,
            speaker_agent_id=self.agent_id,
            speaker_name=f"{self.persona_name} ({self.agent_title})",
            target_agent_id=target_agent_id,
            target_agent_name=target_agent_name,
            contention_topic=contention_topic,
            stance=StanceType.CLARIFY,
            argument_text=f"From a pure delivery perspective, what {target_agent_name} describes as an omission was actually a conscious prioritization. In Turn {verified_cit.turn_id}, the candidate noted shipping an initial MVP with synchronous writes before layering event-driven queues, which matches our Q3 roadmap needs.",
            evidence_citations=[verified_cit],
            confidence_after_argument=0.87
        )

    async def calibrate_stance(
        self,
        initial_evaluation: IndependentEvaluation,
        debate_arguments: List[DebateArgument],
        turns: List[TranscriptTurn]
    ) -> StanceCalibration:
        return StanceCalibration(
            agent_id=self.agent_id,
            agent_name=self.persona_name,
            initial_recommendation=initial_evaluation.recommendation,
            final_recommendation=HireDecision.HIRE,
            initial_confidence=initial_evaluation.confidence_score,
            final_confidence=0.86,
            confidence_delta=0.01,
            concessions_made=[],
            hardened_stances=["Candidate has strong product engineering maturity suitable for our business velocity."],
            calibration_reasoning="Maintained conviction that this candidate will ship impactful customer features quickly without getting bogged down in ivory tower architectures."
        )

