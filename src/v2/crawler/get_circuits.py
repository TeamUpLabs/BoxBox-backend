from src.core.config import Settings
from src.core.database.database import SessionLocal
from src.v2.models.circuit import Circuit
import requests
import pandas as pd

settings = Settings()

class CircuitInfo:
    def __init__(self, corners=None, marshal_lights=None, marshal_sectors=None, rotation=0.0):
        self.corners = corners if corners is not None else pd.DataFrame()
        self.marshal_lights = marshal_lights if marshal_lights is not None else pd.DataFrame()
        self.marshal_sectors = marshal_sectors if marshal_sectors is not None else pd.DataFrame()
        self.rotation = rotation

def get_circuits():
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://multiviewer.app/',
        'Origin': 'https://multiviewer.app'
    }
    
    try:
        circuit_list_response = requests.get(
            "https://api.multiviewer.app/api/v1/circuits",
            headers=headers
        )
        
        if circuit_list_response.status_code != 200:
            print(f"Error fetching circuits: {circuit_list_response.status_code} - {circuit_list_response.text}")
            return {}
            
        circuit_lists = circuit_list_response.json()
        return circuit_lists
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {}
      
def get_circuit_info(circuit_key: int):
    headers = {
      'User-Agent': 'Mozilla/5.0',
      'Accept': 'application/json',
      'Accept-Language': 'en-US,en;q=0.9',
      'Referer': 'https://multiviewer.app/',
      'Origin': 'https://multiviewer.app'
    }
    
    try:
      circuit_info = requests.get(f"https://api.multiviewer.app/api/v1/circuits/{circuit_key}/{settings.now.year}", headers=headers)
      if circuit_info.status_code != 200:
        print(f"Error fetching circuit: {circuit_info.status_code} - {circuit_info.text}")
        return None
      circuit = circuit_info.json()
      
      circuit_info = {
        "corners": circuit.get("corners", []),
        "marshal_lights": circuit.get("marshalLights", []),
        "marshal_sectors": circuit.get("marshalSectors", []),
        "rotation": circuit.get("rotation", 0.0),
        "x": circuit.get("x", 0.0),
        "y": circuit.get("y", 0.0),
      }
      
      # Handle potential missing fields with .get() and provide defaults
      meeting_name = circuit.get("meetingName")
      country_name = circuit.get("countryName", "")
      
      circuit_data = {
        "circuit_id": circuit.get("circuitKey"),
        "name": meeting_name if meeting_name else f"{country_name} Grand Prix" if country_name else "Unknown Circuit",
        "location": circuit.get("location", ""),
        "country": country_name,
        "country_code": circuit.get("countryIocCode", ""),
        "circuit_info": circuit_info
      }
      return circuit_data
    except Exception as e:
      print(f"Error getting circuit: {str(e)}")
      return None
  

def save_circuit_info(db):
  circuits = get_circuits()
  circuit_keys = [int(key) for key in circuits]
      
  for circuit_key in circuit_keys:
    circuit_data = get_circuit_info(circuit_key)
    if circuit_data:      
      # Check if circuit already exists
      existing_circuit = db.query(Circuit).filter(
        Circuit.circuit_id == circuit_data["circuit_id"],
        Circuit.name == circuit_data["name"],
        Circuit.location == circuit_data["location"],
        Circuit.country == circuit_data["country"],
        Circuit.country_code == circuit_data["country_code"]
      ).first()
      
      if existing_circuit:
        # Update existing circuit
        for key, value in circuit_data.items():
          setattr(existing_circuit, key, value)
        db.commit()
        db.refresh(existing_circuit)
        print(f"Updated circuit: {existing_circuit.name}")
      else:
        # Create new circuit
        new_circuit = Circuit(**circuit_data)
        db.add(new_circuit)
        db.commit()
        db.refresh(new_circuit)
        print(f"Added new circuit: {new_circuit.name}")
    
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
      save_circuit_info(db)
    except Exception as e:
        print(f"Error getting schedules: {str(e)}")
        db.rollback()
    finally:
        db.close()
    