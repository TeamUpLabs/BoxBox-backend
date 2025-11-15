from sqlalchemy.orm import Session
from src.v1.models.session import Session as SessionModel
from src.v1.dto.sessions import SessionDto
from typing import List
from src.v1.repositories.results import ResultRepository

class SessionRepository:
    def __init__(self, db: Session):
      self.db = db
    
    def get_sessions(self) -> List[SessionDto]:
      sessions = self.db.query(SessionModel).all()
      return [SessionDto.from_model(session) for session in sessions]