from fastapi import APIRouter, HTTPException
from app.models.domain import FinalSynthesisDossier
from app.services.session_store import session_store

router = APIRouter(prefix="/sessions/{session_id}/synthesis", tags=["Synthesis"])

@router.get("", response_model=FinalSynthesisDossier)
async def get_synthesis(session_id: str):
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.synthesis:
        raise HTTPException(status_code=400, detail="Synthesis has not been generated for this session yet")
    return session.synthesis

