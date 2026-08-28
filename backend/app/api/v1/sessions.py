import asyncio
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from app.models.domain import (
    InterviewSession,
    CandidateProfile,
    JobDescription,
    TranscriptTurn,
    SessionStatus
)
from app.services.session_store import session_store
from app.services.transcript_service import TranscriptService
from app.engine.orchestrator import SimulationOrchestrator
from app.api.ws.stream import manager

router = APIRouter(prefix="/sessions", tags=["Sessions"])

class CreateSessionRequest(BaseModel):
    title: str = "Staff Backend Engineer Interview Simulation"
    candidate: CandidateProfile
    job_description: JobDescription
    raw_transcript: Optional[str] = None
    transcript_turns: Optional[List[TranscriptTurn]] = None

@router.post("", response_model=InterviewSession)
async def create_session(req: CreateSessionRequest):
    turns = req.transcript_turns or []
    if not turns and req.raw_transcript:
        turns = TranscriptService.parse_raw_text_to_turns(req.raw_transcript)
    
    if not turns:
        raise HTTPException(status_code=400, detail="Transcript is required (either raw_transcript or transcript_turns).")

    session = InterviewSession(
        title=req.title,
        candidate=req.candidate,
        job_description=req.job_description,
        transcript_turns=turns,
        status=SessionStatus.CREATED
    )
    session_store.save(session)
    return session

@router.get("", response_model=List[InterviewSession])
async def list_sessions():
    return session_store.list_all()

@router.get("/{session_id}", response_model=InterviewSession)
async def get_session(session_id: str):
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

async def run_simulation_task(session_id: str):
    session = session_store.get(session_id)
    if not session:
        return
    async def emit(event):
        await manager.broadcast_event(session_id, event)
    orchestrator = SimulationOrchestrator(event_emitter=emit)
    await orchestrator.run_full_simulation(session)
    session_store.save(session)

@router.post("/{session_id}/evaluate", response_model=InterviewSession)
async def trigger_evaluation(session_id: str, background_tasks: BackgroundTasks, run_sync: bool = False):
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def emit(event):
        await manager.broadcast_event(session_id, event)

    if run_sync:
        orchestrator = SimulationOrchestrator(event_emitter=emit)
        updated_session = await orchestrator.run_full_simulation(session)
        session_store.save(updated_session)
        return updated_session
    else:
        background_tasks.add_task(run_simulation_task, session_id)
        return session

