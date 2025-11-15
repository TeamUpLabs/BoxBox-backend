from fastapi import APIRouter, Depends
from src.v1.repositories.sessions import SessionRepository
from sqlalchemy.orm import Session
from src.core.database.database import get_db

router = APIRouter(prefix="/v1/sessions", tags=["sessions"])

@router.get("")
def get_sessions(db: Session = Depends(get_db)):
  session_repository = SessionRepository(db)
  return session_repository.get_sessions()
