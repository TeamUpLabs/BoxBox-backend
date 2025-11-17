from sqlalchemy.orm import Session
from src.v2.models.session import Session as SessionModel
from src.v2.dto.sessions import SessionDto
from typing import List

class SessionRepository:
    def __init__(self, db: Session):
      self.db = db
    
    def get_sessions(self) -> List[SessionDto]:
      sessions = self.db.query(SessionModel).all()
      return [SessionDto.from_model(session) for session in sessions]
    
    def get_session_by_session_id(self, session_id: int) -> SessionDto:
      session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
      return SessionDto.from_model(session)