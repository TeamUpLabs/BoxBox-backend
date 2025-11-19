from src.core.config import Settings
from src.core.database.database import SessionLocal
from src.v2.models.circuit import Circuit
import requests
import pandas as pd
from bs4 import BeautifulSoup

settings = Settings()

circuit_key = {
  "australia": 10,
  "china": 49,
  "japan": 46,
  "bahrain": 63,
  "saudi-arabia": 149,
  "miami": 151,
  "emiliaromagna": 6,
  "monaco": 22,
  "spain": 15,
  "canada": 23,
  "austria": 19,
  "great-britain": 2,
  "belgium": 7,
  "hungary": 4,
  "netherlands": 55,
  "italy": 39,
  "azerbaijan": 144,
  "singapore": 61,
  "united-states": 9, 
  "mexico": 65,
  "brazil": 14,
  "las-vegas": 152,
  "qatar": 150,
  "united-arab-emirates": 70
}

def convert_lap_time_to_seconds(lap_time_str):
    """Convert lap time format '1:19.813' to seconds as float"""
    if ':' in lap_time_str:
      minutes, seconds = lap_time_str.split(':')
      return float(minutes) * 60 + float(seconds)
    return float(lap_time_str)
  
def get_country_code(country_name: str):
  url = "https://flagsapi.com/"
  response = requests.get(url)
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    div = soup.find_all("div", "item_country")
    for country in div:
      if country.find_all("p")[1].text == country_name:
        return country.find_all("p")[0].text
  else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
    return None
    
def get_circuit_basic_info(circuit_key: int):
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
      
      meeting_name = circuit.get("meetingName")
      country_name = circuit.get("countryName", "")
      if country_name == "Great Britain":
        country_name = "United Kingdom"
      
      if meeting_name == None and country_name == "Japan":
        meeting_name = "Japanese Grand Prix"
      
      circuit_data = {
        "circuit_id": circuit.get("circuitKey"),
        "name": meeting_name if meeting_name else "Unknown Circuit",
        "location": circuit.get("location", ""),
        "country": country_name,
        "country_code": get_country_code(country_name),
      }
      return circuit_data
    except Exception as e:
      print(f"Error getting circuit: {str(e)}")
      return None

def get_formula1_circuit_info_href():
  url = "https://www.formula1.com/en/racing/2025"
  response = requests.get(url)
  hrefs = []

  if response.status_code == 200:
      soup = BeautifulSoup(response.content, "html.parser")
      for i in range(2, 26):
        href = soup.select_one(rf"#maincontent > div > div.Container-module_container__0e4ac.colors-module_bg_colour-surface-neutral-surface-neutral-3__u3lwa > div > div > div.grid.justify-items-stretch.items-center.gap-px-12.\@\[738px\]\/cards\:gap-px-16.lg\:gap-px-24.grid-cols-1.\@\[640px\]\/cards\:grid-cols-2.\@\[1320px\]\/cards\:grid-cols-3 > a:nth-child({i})")['href']
        hrefs.append(href)
  else:
      print(f"Failed to retrieve the page. Status code: {response.status_code}")

  return hrefs

def get_formula1_circuit_info(href):
  url = "https://www.formula1.com" + href
  response = requests.get(url)
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    image = soup.select_one(r"#maincontent > div > div:nth-child(3) > div > div > div > div.w-full.grid.grid-cols-1.md\:grid-cols-2 > div.border-\[rgb\(from_var\(--f1rd-colour-surface-neutral-surface-neutral-11\)_r_g_b_\/_0\.1\)\].border-b-thin.md\:border-b-0.pb-px-48.md\:pb-0.md\:pr-px-32.md\:border-r-thin.min-h-\[300px\].max-h-\[220px\].md\:max-h-inherit.flex.justify-center.items-center > img")['src']
    circuit_length = soup.select_one(r"#maincontent > div > div:nth-child(3) > div > div > div > div.w-full.grid.grid-cols-1.md\:grid-cols-2 > div.pt-px-16.md\:pl-px-32 > dl > div.pt-px-16.pb-px-32.grid.gap-y-px-4.grid-cols-1.grid-rows-subgrid.row-span-3.border-\[rgb\(from_var\(--f1rd-colour-surface-neutral-surface-neutral-11\)_r_g_b_\/_0\.1\)\].col-span-2 > dd").text
    first_grand_prix = int(soup.select_one(r"#maincontent > div > div:nth-child(3) > div > div > div > div.w-full.grid.grid-cols-1.md\:grid-cols-2 > div.pt-px-16.md\:pl-px-32 > dl > div:nth-child(2) > dd").text)
    number_of_laps = int(soup.select_one(r"#maincontent > div > div:nth-child(3) > div > div > div > div.w-full.grid.grid-cols-1.md\:grid-cols-2 > div.pt-px-16.md\:pl-px-32 > dl > div:nth-child(3) > dd").text)
    fastest_lap_time = {
      "lap_time": convert_lap_time_to_seconds(soup.select_one(r"#maincontent > div > div:nth-child(3) > div > div > div > div.w-full.grid.grid-cols-1.md\:grid-cols-2 > div.pt-px-16.md\:pl-px-32 > dl > div:nth-child(4) > dd").text),
      "driver": soup.select_one(r"#maincontent > div > div:nth-child(3) > div > div > div > div.w-full.grid.grid-cols-1.md\:grid-cols-2 > div.pt-px-16.md\:pl-px-32 > dl > div:nth-child(4) > span").text
    }
    race_distance = soup.select_one(r"#maincontent > div > div:nth-child(3) > div > div > div > div.w-full.grid.grid-cols-1.md\:grid-cols-2 > div.pt-px-16.md\:pl-px-32 > dl > div:nth-child(5) > dd").text
    
    circuit_data = get_circuit_basic_info(circuit_key[href.split("/")[-1]])
    
    circuit_info = {
      "circuit_id": circuit_key[href.split("/")[-1]],
      "name": circuit_data.get("name"),
      "location": circuit_data.get("location"),
      "country": circuit_data.get("country"),
      "country_code": circuit_data.get("country_code"),
      "image": image,
      "circuit_length": circuit_length,
      "first_grand_prix": first_grand_prix,
      "number_of_laps": number_of_laps,
      "fastest_lap_time": fastest_lap_time,
      "race_distance": race_distance
    }
    return circuit_info
  

def save_circuit_info(db):
  hrefs = get_formula1_circuit_info_href()
  for href in hrefs:
    circuit_data = get_formula1_circuit_info(href)
    if circuit_data:      
      # Check if circuit already exists
      existing_circuit = db.query(Circuit).filter(
        Circuit.circuit_id == circuit_data["circuit_id"],
        Circuit.name == circuit_data["name"],
        Circuit.location == circuit_data["location"],
        Circuit.country == circuit_data["country"],
        Circuit.country_code == circuit_data["country_code"],
        Circuit.image == circuit_data["image"],
        Circuit.circuit_length == circuit_data["circuit_length"],
        Circuit.first_grand_prix == circuit_data["first_grand_prix"],
        Circuit.number_of_laps == circuit_data["number_of_laps"],
        Circuit.race_distance == circuit_data["race_distance"],
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
    