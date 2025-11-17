from pydantic import BaseModel
from src.v2.models.team import Team as TeamModel

class TeamDto(BaseModel):
  id: int
  constructor_id: str
  name: str
  team_color: str
  nationality: str
  logo_url: str
  country_flag_url: str
  car_url: str
  
  class Config:
    allow_population_by_field_name = True
    
  @classmethod
  def from_model(cls, team: TeamModel) -> 'TeamDto':
    return cls(
      id=team.id,
      constructor_id=team.constructorId,
      name=team.name,
      team_color=team.teamColor,
      nationality=team.nationality,
      logo_url=team.logoURL,
      country_flag_url=team.countryFlagURL,
      car_url=team.carURL
    )