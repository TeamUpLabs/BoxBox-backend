from fastapi import APIRouter, Depends
from src.v2.repositories.sessions import SessionRepository
from sqlalchemy.orm import Session
from src.core.database.database import get_db
from typing import Optional

router = APIRouter(prefix="/v2/sessions", tags=["sessions"])

@router.get("")
def get_sessions(session_id: Optional[int] = None, db: Session = Depends(get_db)):
  session_repository = SessionRepository(db)
  if session_id:
    return session_repository.get_session_by_session_id(session_id)
  return session_repository.get_sessions()
