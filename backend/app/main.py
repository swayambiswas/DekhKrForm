import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api.v1.router import api_router
from app.api.ws.stream import manager
from app.services.session_store import session_store
from app.models.domain import (
    InterviewSession,
    CandidateProfile,
    JobDescription,
    TranscriptTurn,
    SessionStatus
)

def seed_sample_sessions():
    """Pre-seeds canonical candidate benchmarks for instant testing."""
    sample_turns_staff = [
        TranscriptTurn(turn_id=1, speaker="Interviewer", text="Welcome Alex! Let's start with a design for a globally distributed write-heavy audit logging pipeline at 500k ops/sec."),
        TranscriptTurn(turn_id=2, speaker="Candidate", text="Great challenge. To handle 500k ops/sec write throughput without single-leader write lock contention, I'd decouple write ingestion from persistence using partitioned Kafka topics sharded by tenant and event-hash."),
        TranscriptTurn(turn_id=3, speaker="Interviewer", text="How do you ensure exactly-once semantics and avoid data loss during a cluster partition?"),
        TranscriptTurn(turn_id=4, speaker="Candidate", text="In distributed storage, CAP dictates choosing between consistency and availability. For audit logs, durability and ordering are non-negotiable. I would configure Kafka with acks=all, min.insync.replicas=2, and assign monotonic sequence numbers per partition to enable idempotent consumer deduplication at the stateful storage tier."),
        TranscriptTurn(turn_id=5, speaker="Interviewer", text="Tell me about a time you led a team through a significant technical disagreement."),
        TranscriptTurn(turn_id=6, speaker="Candidate", text="When debating between GraphQL and gRPC for internal mesh communication, opinions were entrenched. Rather than enforcing top-down authority, I created a blameless benchmarking spike where each team measured latency, payload size, and developer ergonomic velocity. We aligned on gRPC for internal mesh and GraphQL at the edge gateway."),
        TranscriptTurn(turn_id=7, speaker="Interviewer", text="What happens when your primary database encounters split-brain quorum failure?"),
        TranscriptTurn(turn_id=8, speaker="Candidate", text="We must rely on an odd-numbered Raft or Paxos quorum coordinator. If a network partition isolates a minority node, it immediately steps down from leader writes and rejects mutations with backpressure.")
    ]

    session_staff = InterviewSession(
        id="staff-alex-chen-canonical",
        title="Staff Distributed Systems Architect (Alex Chen)",
        candidate=CandidateProfile(
            name="Alex Chen",
            target_role="Staff Distributed Systems Engineer",
            target_level="L6 / Staff",
            experience_years=10,
            resume_summary="Former Lead Architect at CloudScale Inc. Designed globally replicated distributed messaging brokers handling 2M+ msg/sec.",
            key_skills=["Distributed Systems", "Raft/Paxos", "Kafka", "High Throughput Architecture", "Go/Rust"]
        ),
        job_description=JobDescription(
            role_title="Staff Distributed Systems Engineer",
            level="L6",
            team="Core Infrastructure Platform",
            core_responsibilities=[
                "Lead architecture for multi-region active-active storage",
                "Ensure 99.999% availability and data integrity under network partitions",
                "Mentor senior engineers and set technical bar"
            ],
            required_skills=["Distributed Systems", "Storage Engines", "High Concurrency", "Technical Leadership"]
        ),
        transcript_turns=sample_turns_staff,
        status=SessionStatus.CREATED
    )
    session_store.save(session_staff)

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_sample_sessions()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Seed immediately on module load as well
seed_sample_sessions()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# WebSocket Real-Time Stream
@app.websocket("/api/v1/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)

# Resolve Frontend Path
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# Check root/frontend/static, backend/frontend/static, or ./frontend/static
possible_paths = [
    os.path.abspath(os.path.join(current_file_dir, "..", "..", "frontend", "static")),
    os.path.abspath(os.path.join(current_file_dir, "..", "frontend", "static")),
    os.path.abspath(os.path.join(os.getcwd(), "frontend", "static")),
]

frontend_dir = next((p for p in possible_paths if os.path.exists(p)), None)

if frontend_dir:
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

