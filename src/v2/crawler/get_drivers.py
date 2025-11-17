from src.v2.models.driver import Driver
from datetime import datetime
from ..utils.load_json import load_json
from pathlib import Path
from src.core.database.database import SessionLocal

def get_drivers(session, drivers_data):
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
    drivers_data = load_json(base_path / 'data' / 'F1Drivers.json')
    get_drivers(session, drivers_data)
    session.commit()
    print(f"Processed {len(drivers_data)} drivers.")
  except Exception as e:
    print(f"An error occurred: {str(e)}")
    session.rollback()
  finally:
    session.close()
  