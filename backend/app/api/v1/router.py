from fastapi import APIRouter
from app.api.v1.sessions import router as sessions_router
from app.api.v1.evaluations import router as evaluations_router
from app.api.v1.debate import router as debate_router
from app.api.v1.synthesis import router as synthesis_router
from app.api.v1.evidence import router as evidence_router

api_router = APIRouter()
api_router.include_router(sessions_router)
api_router.include_router(evaluations_router)
api_router.include_router(debate_router)
api_router.include_router(synthesis_router)
api_router.include_router(evidence_router)

