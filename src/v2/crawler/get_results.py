import fastf1
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from src.v2.models.driver import Driver as DriverModel
from src.v2.models.result import Result as ResultModel
from src.v2.models.session import Session as SessionModel
from src.core.database.database import SessionLocal
from src.core.config import Settings

settings = Settings()
fastf1.set_log_level("ERROR")

session_name_to_session_code = {
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
    "Sprint Shootout": "SS",
    "Sprint Qualifying": "SQ",
    "Sprint": "S",
    "Qualifying": "Q",
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

fastf1.Cache.enable_cache("./cache")

def get_schedules():
  schedules = fastf1.get_event_schedule(settings.now.year)
  schedules = schedules[schedules['RoundNumber'] > 0]
  return schedules

def get_event_by_round(round):
  event = fastf1.get_event(settings.now.year, round)
  return event

def determine_status(result: Dict[str, Any], q1: Optional[float], q2: Optional[float], 
                   q3: Optional[float], time_val: Optional[float]) -> str:
    if result["Status"] != "":
        return result["Status"]
    return "Finished" if any(x is not None for x in [q1, q2, q3, time_val]) else "Retired"
  
def check_session(db, year, round, session_name):
  session = db.query(SessionModel).filter(
    SessionModel.year == year,
    SessionModel.round == round,
    SessionModel.session_name == session_name,
    SessionModel.session_type == session_name_to_session_type.get(session_name, "Unknown")
  ).first()
  if not session:
    print(f"Session {session_name} not found in database, skipping session.")
    return None
  return session
  
def save_result(db, result_data):
  driver_exists = db.query(DriverModel).filter(DriverModel.permanentNumber == result_data["driver_number"]).first()
  if not driver_exists:
    print(f"Driver number {result_data['driver_number']} not found in database, skipping result.")
    return
  
  existing_result = db.query(ResultModel).filter(
    ResultModel.session_id == result_data["session_id"],
    ResultModel.driver_number == result_data["driver_number"]
  ).first()
  
  if existing_result:
    # Update existing result
    for key, value in result_data.items():
      setattr(existing_result, key, value)
    existing_result.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(existing_result)
    print(f"Updated result for driver {result_data['driver_number']} in session {result_data['session_id']}")
  else:
    # Create new result
    result_data["created_at"] = datetime.now(timezone.utc)
    result_data["updated_at"] = datetime.now(timezone.utc)
    result = ResultModel(**result_data)
    db.add(result)
    db.commit()
    print(f"Saved new result for driver {result_data['driver_number']} in session {result_data['session_id']}")

def main():
  schedules = get_schedules()
  rounds = schedules['RoundNumber'].to_list()
  
  for round in rounds:
    event = get_event_by_round(round)
    session_types = []
    
    for i in range(1, 6):
      session_name = getattr(event, f'Session{i}', None)
      if session_name and pd.notna(session_name):
        session_type = session_name_to_session_code.get(session_name, "Unknown")
        session_types.append((session_name, session_type))
        
    for session_name, session_type in session_types:
      session = event.get_session(session_name)
      session.load()
      print("#" * 50)
      print(f"Processing session: Round {round}, Session: {session_name} (Type: {session_type})")
      print("#" * 50)
      if "FP" in session_type:
        drivers = session.drivers
        
        # Store all driver results to calculate positions later
        driver_results = []
        
        for driver in drivers:
          result = session.laps.pick_drivers(driver).pick_fastest()
          
          time_val = None
          if result is not None and pd.notna(result.get('LapTime')):
            time_val = result['LapTime'].total_seconds()
            
          result_data = {
            "session_id": check_session(db, settings.now.year, round, session_name).id,
            "driver_number": driver,
            "position": None,
            "points": 0,
            "laps_completed": len(session.laps.pick_drivers(driver)),
            "Q1": 0.0,
            "Q2": 0.0,
            "Q3": 0.0,
            "time": time_val if time_val is not None else 0.0,
            "status": "Finished" if time_val is not None and time_val > 0 else "Retired"
          }
          
          driver_results.append(result_data)
        
        # Sort driver results, placing drivers with time=0 at the end
        driver_results.sort(key=lambda x: float('inf') if x["time"] == 0.0 else x["time"])
        
        # Assign positions
        for i, driver_result in enumerate(driver_results, 1):
          # Each driver gets a unique position number
          driver_result["position"] = i
          save_result(db, driver_result)
        
      else:
        results = session.results
        for _, result in results.iterrows():
          q1 = result["Q1"].total_seconds() if pd.notna(result["Q1"]) else None
          q2 = result["Q2"].total_seconds() if pd.notna(result["Q2"]) else None
          q3 = result["Q3"].total_seconds() if pd.notna(result["Q3"]) else None
          
          leader_time = None
          if not results.empty and "Time" in results.columns and len(results) > 0:
              leader_time = results["Time"].iloc[0].total_seconds() if pd.notna(results["Time"].iloc[0]) else None
          
          time_val = None
          if pd.notna(result.get("Time")):
              try:
                  if int(result.get("Position", "")) == 1:  # Leader
                      time_val = leader_time
                  elif leader_time is not None and hasattr(result["Time"], 'total_seconds'):
                      time_val = leader_time + result["Time"].total_seconds()
              except Exception as e:
                  print(f"⚠️  Error calculating time for driver {result['DriverNumber']}: {e}")
          
          
          status = determine_status(result, q1, q2, q3, time_val)
          
          result_data = {
            "session_id": check_session(db, settings.now.year, round, session_name).id,
            "driver_number": result["DriverNumber"],
            "position": result["Position"] if pd.notna(result["Position"]) else 0,
            "points": result["Points"] if pd.notna(result["Points"]) else 0,
            "laps_completed": len(session.laps.pick_drivers(result["DriverNumber"])),
            "Q1": q1 if q1 is not None else 0.0,
            "Q2": q2 if q2 is not None else 0.0,
            "Q3": q3 if q3 is not None else 0.0,
            "time": time_val if time_val is not None else 0.0,
            "status": status,
          }
          
          save_result(db, result_data)
    
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
    main()
  except Exception as e:
    print(f"Error in get_results: {str(e)}")
    raise
  finally:
    db.close()

