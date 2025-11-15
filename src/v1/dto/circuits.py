from pydantic import BaseModel
from src.v1.models.circuit import Circuit as CircuitModel

class CircuitDto(BaseModel):
  id: int
  circuit_id: int
  circuit_short_name: str
  name: str
  location: str
  country: str
  country_code: str
  
  class Config:
    allow_population_by_field_name = True
    
  @classmethod
  def from_model(cls, circuit: CircuitModel) -> 'CircuitDto':
    return cls(
      id=circuit.id,
      circuit_id=circuit.circuit_id,
      circuit_short_name=circuit.circuit_short_name,
      name=circuit.name,
      location=circuit.location,
      country=circuit.country,
      country_code=circuit.country_code
    )
  
