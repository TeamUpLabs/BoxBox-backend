from pydantic import BaseModel
from src.v2.models.circuit import Circuit as CircuitModel

class CircuitDto(BaseModel):
  id: int
  circuit_id: int
  name: str
  location: str
  country: str
  country_code: str
  image: str
  circuit_length: str
  first_grand_prix: int
  number_of_laps: int
  fastest_lap_time: dict
  race_distance: str
  
  @classmethod
  def from_model(cls, circuit: CircuitModel) -> 'CircuitDto':
    return cls(
      id=circuit.id,
      circuit_id=circuit.circuit_id,
      name=circuit.name,
      location=circuit.location,
      country=circuit.country,
      country_code=circuit.country_code,
      image=circuit.image,
      circuit_length=circuit.circuit_length,
      first_grand_prix=circuit.first_grand_prix,
      number_of_laps=circuit.number_of_laps,
      fastest_lap_time=circuit.fastest_lap_time,
      race_distance=circuit.race_distance
    )