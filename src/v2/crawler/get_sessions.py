import fastf1
from src.core.config import Settings
import pandas as pd
from src.v2.models.circuit import Circuit as CircuitModel
from src.v2.models.session import Session as SessionModel
from src.core.database.database import SessionLocal
from datetime import datetime, timezone

settings = Settings()
fastf1.set_log_level("ERROR")

session_name_to_session_code = {
  "Practice 1": "FP1",
  "Practice 2": "FP2",
  "Practice 3": "FP3",
  "Sprint Shootout": "SS",
  "Sprint Qualifying": "SQ",
  "Qualifying": "Q",
  "Sprint": "S",
  "Race": "R"
}

session_name_to_session_type = {
  "Practice 1": "Practice",
  "Practice 2": "Practice",
  "Practice 3": "Practice",
  "Sprint Shootout": "Practice",
  "Sprint Qualifying": "Qualifying",
  "Qualifying": "Qualifying",
  "Sprint": "Race",
  "Race": "Race"
}

data_sample = pd.DataFrame()

fastf1.Cache.enable_cache("./cache")

def get_schedules():
  schedules = fastf1.get_event_schedule(settings.now.year)
  schedules = schedules[schedules['RoundNumber'] > 0]
  return schedules

def circuit_id_by_event_name(db, event_name: str):
  circuit = db.query(CircuitModel).filter(CircuitModel.name == event_name).first()
  return circuit

def get_sessions(db):
  schedules = get_schedules()
  print(f"Total Events: {len(schedules)}")
  
  for index, row in schedules.iterrows():
      circuit = circuit_id_by_event_name(db, row['EventName'])
      
      if not circuit:
        print(f"Circuit with name {row['EventName']} not found. Skipping session.")
        continue
      
      for i in range(1, 6):
        session_time = row[f'Session{i}DateUtc'].to_pydatetime() if hasattr(row[f'Session{i}DateUtc'], 'to_pydatetime') else datetime.fromisoformat(str(row[f'Session{i}DateUtc']))
        if session_time.tzinfo is None:
            session_time = session_time.replace(tzinfo=timezone.utc)
        
        try:  
          session = fastf1.get_session(settings.now.year, row['RoundNumber'], session_name_to_session_code[row[f"Session{i}"]])
          session.load()
          weather_data = session.weather_data
          # Convert weather data to a serializable format if it's a pandas DataFrame
          if hasattr(weather_data, 'to_dict'):
              # Convert Timedelta and other non-serializable types to strings
              weather_df = weather_data.copy()
              for col in weather_df.select_dtypes(include=['timedelta64']).columns:
                  weather_df[col] = weather_df[col].astype(str)
              weather_data = weather_df.to_dict(orient='records')
        except Exception as e:
          session = None
          weather_data = None
          print(f"Error loading session {row['RoundNumber']} {session_name_to_session_code[row[f'Session{i}']]}: {str(e)}")
          
        try:
            session_data = {
                "year": settings.now.year,
                "round": int(row['RoundNumber']),
                "session_type": session_name_to_session_type[row[f"Session{i}"]],
                "session_name": row[f"Session{i}"],
                "session_date": session_time,
                "circuit_id": int(circuit.circuit_id),
                "status": "Finished" if session_time < datetime.now(timezone.utc) else "Scheduled",
                "weather": weather_data
            }
        except Exception as e:
            print(f"Error creating session data for {row['EventName']} - {row[f'Session{i}']}: {str(e)}")
            continue
        
        existing_session = db.query(SessionModel).filter(
          SessionModel.year == session_data['year'],
          SessionModel.round == session_data['round'],
          SessionModel.session_type == session_data['session_type'],
          SessionModel.session_name == session_data['session_name'],
          SessionModel.session_date == session_data['session_date'],
          SessionModel.circuit_id == session_data['circuit_id']
        ).first()
        
        if existing_session:
          # Update existing session
          existing_session.updated_at = datetime.now(timezone.utc)
          for key, value in session_data.items():
            setattr(existing_session, key, value)
          db.commit()
          db.refresh(existing_session)
          print(f"Updated session: Round{existing_session.round} - {existing_session.session_type} - {existing_session.session_name}")
        else:
          # Create new session
          session_data['created_at'] = datetime.now(timezone.utc)
          session_data['updated_at'] = datetime.now(timezone.utc)
          new_session = SessionModel(**session_data)
          db.add(new_session)
          db.commit()
          db.refresh(new_session)
          print(f"Added new session: Round{new_session.round} - {new_session.session_type} - {new_session.session_name}")
          
def init_db():
    """Initialize the database by creating all tables."""
    from src.core.database.database import Base, engine
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created!")

if __name__ == "__main__":    
    # Initialize the database first
    init_db()
    
    # Create a database session
    db = SessionLocal()
    
    try:
      get_sessions(db)
    except Exception as e:
        print(f"Error getting schedules: {str(e)}")
        db.rollback()
    finally:
        db.close()
