from typing import Dict, List
from fastapi import APIRouter, HTTPException
from app.models.domain import IndependentEvaluation
from app.services.session_store import session_store

router = APIRouter(prefix="/sessions/{session_id}/evaluations", tags=["Evaluations"])

@router.get("/independent", response_model=Dict[str, IndependentEvaluation])
async def get_independent_evaluations(session_id: str):
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.independent_evaluations

