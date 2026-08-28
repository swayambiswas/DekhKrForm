from typing import Dict, List, Optional
from app.models.domain import InterviewSession

class SessionStore:
    def __init__(self):
        self._sessions: Dict[str, InterviewSession] = {}

    def save(self, session: InterviewSession) -> InterviewSession:
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Optional[InterviewSession]:
        return self._sessions.get(session_id)

    def list_all(self) -> List[InterviewSession]:
        return list(self._sessions.values())

session_store = SessionStore()

