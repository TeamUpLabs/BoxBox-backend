import requests
from datetime import datetime, timezone
from typing import List, Dict
from sqlalchemy.orm import Session
from src.core.database.database import SessionLocal
from src.v1.models.session import Session as SessionModel
from src.v1.models.circuit import Circuit as CircuitModel
from src.v1.models.result import Result as ResultModel
from src.v1.models.driver import Driver as DriverModel
from pathlib import Path
from src.v1.models.team import Team
from src.v1.models.driver import Driver
import json

BASE_URL = "https://api.openf1.org/v1"

def load_json(file_path: str) -> list[dict]:
    """Load driver data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_teams(session: Session, teams_data: list[dict]) -> None:
    """Create team records in the database (idempotent)"""
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


def create_drivers(session: Session, drivers_data: list[dict]) -> None:
    """Create driver records in the database"""
    for driver_data in drivers_data:
        # Check if driverId or permanentNumber already exists
        existing_driver = session.query(Driver).filter(
            (Driver.driverId == driver_data['driverId']) | (Driver.permanentNumber == driver_data['permanentNumber'])
        ).first()
        
        if existing_driver:
            print(f"Driver {driver_data['givenName']} {driver_data['familyName']} or number {driver_data['permanentNumber']} already exists. Skipping...")
            continue
            
        # Create new driver
        driver = Driver(
            driverId=driver_data['driverId'],
            permanentNumber=driver_data['permanentNumber'],
            givenName=driver_data['givenName'],
            familyName=driver_data['familyName'],
            nameAcronym=driver_data['nameAcronym'],
            dateOfBirth=datetime.strptime(driver_data['dateOfBirth'], '%Y-%m-%d'),
            nationality=driver_data['nationality'],
            headshotURL=driver_data['headshotURL'],
            countryFlagURL=driver_data['countryFlagURL'],
            currentTeam=driver_data['currentTeam']
        )
        
        session.add(driver)
        print(f"Added driver: {driver.givenName} {driver.familyName}")


def get_sessions(db: Session, year: int = 2025) -> List[Dict]:
    print(f"Fetching sessions for {year}...")
    response = requests.get(f"{BASE_URL}/sessions?year={year}")
    
    if response.status_code != 200:
        print(f"Error fetching sessions: {response.status_code}")
        return []
    
    sessions = response.json()
    saved_sessions = []
    
    for session in sessions:
        try:
            # Parse date strings to datetime objects
            date_start = datetime.fromisoformat(session["date_start"].replace('Z', '+00:00')) if session.get("date_start") else None
            date_end = datetime.fromisoformat(session["date_end"].replace('Z', '+00:00')) if session.get("date_end") else None
            
            # First, get the circuit by circuit_key to get the correct circuit_id
            circuit = db.query(CircuitModel).filter(
                CircuitModel.circuit_id == session.get("circuit_key")
            ).first()
            
            if not circuit:
                print(f"Circuit with key {session.get('circuit_key')} not found. Skipping session.")
                continue
                
            session_data = {
                "year": int(year) if year else None,
                "round": int(session.get("meeting_key")) if session.get("meeting_key") else None,
                "session_key": int(session.get("session_key")) if session.get("session_key") else None,
                "session_type": str(session.get("session_type", "")),
                "session_name": str(session.get("session_name", "")),
                "session_date": date_start.replace(tzinfo=None) if date_start else None,
                "circuit_id": int(circuit.circuit_id) if circuit and hasattr(circuit, 'circuit_id') else None,
                "status": "Completed" if date_end and date_end < datetime.now(date_end.tzinfo) else "Scheduled",
                "weather": get_session_weather(session.get("session_key")),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Check if session already exists
            existing_session = db.query(SessionModel).filter(
                SessionModel.year == year,
                SessionModel.round == session_data["round"],
                SessionModel.session_key == session_data["session_key"],
                SessionModel.session_type == session_data["session_type"],
                SessionModel.session_name == session_data["session_name"],
                SessionModel.session_date == session_data["session_date"],
                SessionModel.circuit_id == session_data["circuit_id"]
            ).first()
            
            if existing_session:
                # Update existing session
                for key, value in session_data.items():
                    setattr(existing_session, key, value)
                db.commit()
                db.refresh(existing_session)
                saved_sessions.append(existing_session.to_dict())
                print(f"Updated session: {existing_session.session_type} - {existing_session.session_name}")
            else:
                # Create new session
                new_session = SessionModel(**session_data)
                db.add(new_session)
                db.commit()
                db.refresh(new_session)
                saved_sessions.append(new_session.to_dict())
                print(f"Added new session: {new_session.session_type} - {new_session.session_name}")
            
            get_session_results(db=db, session_key=session["session_key"], session_type=session["session_type"])
        except Exception as e:
            print(f"Error processing session {session.get('session_key')}: {str(e)}")
            db.rollback()
    
    return saved_sessions
  
def get_session_weather(session_key: int):
  response = requests.get(f"{BASE_URL}/weather?session_key={session_key}")
  
  if response.status_code != 200:
    print(f"Error fetching session weather: {response.status_code}")
    return []
  
  weather = response.json()
  return weather
  
def get_session_results(db: Session, session_key: int, session_type: str):
    print(f"Fetching results for session {session_key}...")
    
    # First, get session to get meeting_key
    session = db.query(SessionModel).filter(SessionModel.session_key == session_key).first()
    if not session:
        print(f"Session {session_key} not found in database")
        return []
    
    response = requests.get(f"{BASE_URL}/session_result?session_key={session_key}")
    
    if response.status_code != 200:
        print(f"Error fetching session results: {response.status_code}")
        return []
    
    results = response.json()
    saved_results = []
    
    for result in results:
        try:
            # Get status flags
            dnf = result.get("dnf", False)
            dns = result.get("dns", False)
            dsq = result.get("dsq", False)
            
            # Convert numeric strings to proper numeric types for JSON storage
            time_raw = result.get("duration")
            gap_raw = result.get("gap_to_leader")

            def _to_float_if_possible(value):
                try:
                    return float(value) if value is not None and value != "" else None
                except (ValueError, TypeError):
                    return value  # leave as-is (could be list/JSON)

            time_value = _to_float_if_possible(time_raw)
            gap_value = _to_float_if_possible(gap_raw)

            result_data = {
                "session_key": session_key,
                "meeting_key": result.get("meeting_key"),
                "session_type": session_type,
                "driver_number": result.get("driver_number"),
                "position": result.get("position"),
                "points": float(result.get("points", 0)),
                "dnf": dnf,
                "dns": dns,
                "dsq": dsq,
                "status": "Completed" if not dnf and not dns and not dsq else "DNF" if dnf else "DNS" if dns else "DSQ" if dsq else "Finished",
                "laps_completed": result.get("number_of_laps", 0),
                "time": time_value,
                "gap_to_leader": gap_value,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Skip result if driver is not in DB
            driver_exists = db.query(DriverModel).filter(DriverModel.permanentNumber == result_data["driver_number"]).first()
            if not driver_exists:
                print(f"Driver number {result_data['driver_number']} not found in database, skipping result.")
                continue
            
            # Check if result already exists
            existing_result = db.query(ResultModel).filter(
                ResultModel.session_key == session_key,
                ResultModel.driver_number == result_data["driver_number"],
                ResultModel.session_type == result_data["session_type"]
            ).first()
            
            if existing_result:
                # Update existing result
                for key, value in result_data.items():
                    setattr(existing_result, key, value)
                existing_result.updated_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(existing_result)
                saved_results.append(existing_result.to_dict())
                print(f"Updated result for driver {result_data['driver_number']} in session {session_key}")
            else:
                # Create new result
                new_result = ResultModel(**result_data)
                db.add(new_result)
                db.commit()
                db.refresh(new_result)
                saved_results.append(new_result.to_dict())
                print(f"Added new result for driver {result_data['driver_number']} in session {session_key}")
          
        except Exception as e:
            print(f"Error processing result for session {session_key}: {str(e)}")
            print(f"Error details: {e}")
            db.rollback()
    
    return saved_results

def get_circuits(db: Session, year: int = 2025):
    response = requests.get(f"{BASE_URL}/meetings?year={year}")
    if response.status_code != 200:
        print(f"Error fetching circuits: {response.status_code}")
        return []
    
    results = response.json()
    saved_circuits = []
    
    for result in results:
        try:
            circuit_data = {
                "circuit_id": result.get("circuit_key"),
                "circuit_short_name": result.get("circuit_short_name"),
                "name": result.get("meeting_name"),
                "location": result.get("location"),
                "country": result.get("country_name"),
                "country_code": result.get("country_code"),
            }
            
            # Check if circuit already exists
            existing_circuit = db.query(CircuitModel).filter(
                CircuitModel.circuit_id == circuit_data["circuit_id"]
            ).first()
            
            if existing_circuit:
                # Update existing circuit
                for key, value in circuit_data.items():
                    setattr(existing_circuit, key, value)
                db.commit()
                db.refresh(existing_circuit)
                saved_circuits.append(existing_circuit.to_dict())
                print(f"Updated circuit: {existing_circuit.name}")
            else:
                # Create new circuit
                new_circuit = CircuitModel(**circuit_data)
                db.add(new_circuit)
                db.commit()
                db.refresh(new_circuit)
                saved_circuits.append(new_circuit.to_dict())
                print(f"Added new circuit: {new_circuit.name}")
                
        except Exception as e:
            print(f"Error processing circuit {result.get('circuit_key')}: {str(e)}")
            db.rollback()
    
    return saved_circuits

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
        # First, add teams and drivers
        print("Adding teams and drivers...")
        base_path = Path(__file__).parent
        teams_data = load_json(base_path / 'data' / 'F1Teams.json')
        create_teams(db, teams_data)
        drivers_data = load_json(base_path / 'data' / 'F1Drivers.json')
        create_drivers(db, drivers_data)
        db.commit()
        print(f"Processed {len(teams_data)} teams and {len(drivers_data)} drivers.")
        
        # Next, get circuits
        print("Fetching circuits...")
        circuits = get_circuits(db=db, year=2025)
        print(f"Processed {len(circuits)} circuits.")
        
        # Then, get sessions and their results
        print("\nFetching sessions...")
        sessions = get_sessions(db=db, year=2025)
        print(f"Processed {len(sessions)} sessions.")
        
        print("\nData import completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        db.rollback()
    finally:
        db.close()
