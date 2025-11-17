from ..utils.load_json import load_json
from pathlib import Path
from src.core.database.database import SessionLocal
from src.v2.models.team import Team

def get_teams(session, teams_data):
  for team_data in teams_data:
    existing_team = session.query(Team).filter(Team.constructorId == team_data["constructorId"]).first()
    if existing_team:
        continue
    team = Team(
        constructorId=team_data["constructorId"],
        name=team_data["name"],
        nationality=team_data["nationality"],
        teamColor=team_data["teamColor"],
        logoURL=team_data["logoURL"],
        carURL=team_data["carURL"],
        countryFlagURL=team_data["countryFlagURL"],
    )
    session.add(team)
    
def init_db():
    """Initialize the database by creating all tables."""
    from src.core.database.database import Base, engine
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created!")
  
if __name__ == "__main__":
  init_db()
  session = SessionLocal()
  try:
    base_path = Path(__file__).parent.parent.parent.parent
    teams_data = load_json(base_path / 'data' / 'F1Teams.json')
    get_teams(session, teams_data)
    session.commit()
    print(f"Processed {len(teams_data)} teams.")
  except Exception as e:
    print(f"An error occurred: {str(e)}")
    session.rollback()
  finally:
    session.close()
  