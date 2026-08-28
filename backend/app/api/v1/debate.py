from typing import List
from fastapi import APIRouter, HTTPException
from app.models.domain import DebateRound
from app.services.session_store import session_store

router = APIRouter(prefix="/sessions/{session_id}/debate", tags=["Debate"])

@router.get("", response_model=List[DebateRound])
async def get_debate_rounds(session_id: str):
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.debate_rounds

