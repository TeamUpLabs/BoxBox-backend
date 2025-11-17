from typing import List, Optional
from sqlalchemy.orm import Session
from src.v2.models.team import Team as TeamModel
from src.v2.dto.teams import TeamDto

class TeamRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_teams(self) -> List[TeamDto]:
        teams = self.db.query(TeamModel).all()
        return [TeamDto.from_model(team) for team in teams]
    
    def get_team_by_name(self, name: str) -> Optional[TeamDto]:
        team = self.db.query(TeamModel).filter_by(constructorId=name).first()
        if not team:
            return None
        return TeamDto.from_model(team)
