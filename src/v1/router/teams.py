from fastapi import APIRouter, Depends
from src.v1.repositories.teams import TeamRepository
from typing import Optional
from sqlalchemy.orm import Session
from src.core.database.database import get_db

router = APIRouter(prefix="/v1/teams", tags=["teams"])

@router.get("")
def get_teams(
  name: Optional[str] = None,
  db: Session = Depends(get_db)
):
  team_repository = TeamRepository(db)
  if name:
    return team_repository.get_team_by_name(name)
  return team_repository.get_teams()
