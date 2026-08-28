import inspect
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable, Any
from app.models.domain import (
    InterviewSession,
    SessionStatus,
    IndependentEvaluation,
    DebateRound,
    DebateArgument,
    StanceCalibration,
    FinalSynthesisDossier
)
from app.models.events import SimulationEvent, EventType
from app.agents.technical_agent import TechnicalArchitectAgent
from app.agents.culture_agent import CultureLeadershipAgent
from app.agents.domain_agent import DomainProductAgent
from app.agents.skeptic_agent import BarRaiserSkepticAgent
from app.engine.barrier import IsolationBarrier
from app.engine.evidence_engine import EvidenceEngine
from app.engine.debate_manager import DebateManager
from app.engine.synthesis_engine import SynthesisEngine

class SimulationOrchestrator:
    def __init__(self, event_emitter: Optional[Callable[[SimulationEvent], Any]] = None):
        self.event_emitter = event_emitter
        self.agents = {
            "technical_architect": TechnicalArchitectAgent(),
            "culture_lead": CultureLeadershipAgent(),
            "domain_specialist": DomainProductAgent(),
            "bar_raiser": BarRaiserSkepticAgent()
        }
        self.synthesis_engine = SynthesisEngine()

    async def emit(self, event_type: EventType, session_id: str, payload: Dict[str, Any]):
        if self.event_emitter:
            event = SimulationEvent(
                event_type=event_type,
                session_id=session_id,
                payload=payload
            )
            if inspect.iscoroutinefunction(self.event_emitter):
                await self.event_emitter(event)
            else:
                res = self.event_emitter(event)
                if inspect.iscoroutine(res):
                    await res

    async def run_full_simulation(self, session: InterviewSession) -> InterviewSession:
        """
        Runs the complete 3-phase multi-agent evaluation pipeline.
        """
        try:
            # 1. State: Indexing
            session.status = SessionStatus.INDEXING
            await self.emit(EventType.SESSION_STATUS_CHANGED, session.id, {"status": session.status})
            
            evidence_engine = EvidenceEngine(session.transcript_turns)
            await asyncio.sleep(0.1)

            # 2. Phase 1: Strict Independent Parallel Evaluations
            session.status = SessionStatus.PHASE_1_INDEPENDENT_EVALUATION
            await self.emit(EventType.SESSION_STATUS_CHANGED, session.id, {"status": session.status})

            for agent_id, agent in self.agents.items():
                await self.emit(EventType.AGENT_THINKING, session.id, {
                    "agent_id": agent_id,
                    "agent_name": agent.persona_name,
                    "status": "Analyzing transcript independently..."
                })

            tasks = [
                agent.evaluate_independently(session.candidate, session.job_description, session.transcript_turns)
                for agent in self.agents.values()
            ]
            evaluations_list = await IsolationBarrier.execute_in_parallel(tasks)

            for ev in evaluations_list:
                session.independent_evaluations[ev.agent_id] = ev
                await self.emit(EventType.AGENT_EVALUATION_COMPLETED, session.id, {
                    "agent_id": ev.agent_id,
                    "evaluation": ev.model_dump(mode="json")
                })

            is_valid = IsolationBarrier.verify_isolation_compliance(evaluations_list)
            if not is_valid:
                raise ValueError("Isolation barrier compliance check failed.")

            await self.emit(EventType.PHASE_COMPLETED, session.id, {
                "phase": "PHASE_1_INDEPENDENT_EVALUATION",
                "verified_agents_count": len(evaluations_list)
            })

            # 3. Phase 2: Structured Multi-Round Debate
            session.status = SessionStatus.PHASE_2_DEBATE
            await self.emit(EventType.SESSION_STATUS_CHANGED, session.id, {"status": session.status})

            debate_manager = DebateManager(self.agents, session.transcript_turns, evidence_engine)

            # Round 1
            await self.emit(EventType.DEBATE_ROUND_STARTED, session.id, {"round_number": 1, "title": "Divergence Mapping"})
            round_1 = await debate_manager.execute_debate_round_1(session.independent_evaluations)
            session.debate_rounds.append(round_1)
            for arg in round_1.arguments:
                await self.emit(EventType.DEBATE_ARGUMENT_GENERATED, session.id, {"argument": arg.model_dump(mode="json")})
                await asyncio.sleep(0.05)

            # Round 2
            await self.emit(EventType.DEBATE_ROUND_STARTED, session.id, {"round_number": 2, "title": "Cross-Examination & Rebuttal"})
            round_2 = await debate_manager.execute_debate_round_2(round_1, session.independent_evaluations)
            session.debate_rounds.append(round_2)
            for arg in round_2.arguments:
                await self.emit(EventType.DEBATE_ARGUMENT_GENERATED, session.id, {"argument": arg.model_dump(mode="json")})
                await asyncio.sleep(0.05)

            # Round 3 & Stance Calibration
            await self.emit(EventType.DEBATE_ROUND_STARTED, session.id, {"round_number": 3, "title": "Epistemic Calibration"})
            all_prior_args = round_1.arguments + round_2.arguments
            round_3, calibrations = await debate_manager.execute_debate_round_3(session.independent_evaluations, all_prior_args)
            session.debate_rounds.append(round_3)
            
            for cal in calibrations:
                await self.emit(EventType.CONFIDENCE_CALIBRATED, session.id, {"calibration": cal.model_dump(mode="json")})
                await asyncio.sleep(0.05)

            await self.emit(EventType.PHASE_COMPLETED, session.id, {
                "phase": "PHASE_2_DEBATE",
                "rounds_completed": 3
            })

            # 4. Phase 3: Non-Averaged Synthesis
            session.status = SessionStatus.PHASE_3_SYNTHESIS
            await self.emit(EventType.SESSION_STATUS_CHANGED, session.id, {"status": session.status})

            synthesis_dossier = await self.synthesis_engine.generate_synthesis(
                session_id=session.id,
                candidate=session.candidate,
                jd=session.job_description,
                evaluations=session.independent_evaluations,
                debate_rounds=session.debate_rounds,
                calibrations=calibrations,
                turns=session.transcript_turns
            )
            session.synthesis = synthesis_dossier
            session.status = SessionStatus.COMPLETED

            await self.emit(EventType.SYNTHESIS_COMPLETED, session.id, {
                "synthesis": synthesis_dossier.model_dump(mode="json")
            })
            await self.emit(EventType.SESSION_STATUS_CHANGED, session.id, {"status": session.status})

            return session

        except Exception as e:
            session.status = SessionStatus.ERROR
            session.error_message = str(e)
            await self.emit(EventType.SIMULATION_ERROR, session.id, {"error": str(e)})
            raise

