from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.domain import EvidenceCitation, TranscriptTurn
from app.services.session_store import session_store
from app.engine.evidence_engine import EvidenceEngine

router = APIRouter(prefix="/evidence", tags=["Evidence"])

class VerifyEvidenceRequest(BaseModel):
    session_id: Optional[str] = None
    transcript_turns: Optional[List[TranscriptTurn]] = None
    citation: EvidenceCitation

@router.post("/verify", response_model=EvidenceCitation)
async def verify_evidence(req: VerifyEvidenceRequest):
    turns = req.transcript_turns
    if not turns and req.session_id:
        session = session_store.get(req.session_id)
        if session:
            turns = session.transcript_turns

    if not turns:
        raise HTTPException(status_code=400, detail="Transcript turns or valid session_id is required")

    engine = EvidenceEngine(turns)
    verified = engine.verify_citation(req.citation)
    return verified

