from pydantic import BaseModel
from src.v2.models.circuit import Circuit as CircuitModel

class CircuitDto(BaseModel):
  id: int
  circuit_id: int
  name: str
  location: str
  country: str
  country_code: str
  circuit_info: dict
  
  @classmethod
  def from_model(cls, circuit: CircuitModel) -> 'CircuitDto':
    return cls(
      id=circuit.id,
      circuit_id=circuit.circuit_id,
      name=circuit.name,
      location=circuit.location,
      country=circuit.country,
      country_code=circuit.country_code,
      circuit_info=circuit.circuit_info
    )