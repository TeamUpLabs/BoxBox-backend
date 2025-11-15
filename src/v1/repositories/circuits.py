from typing import List
from sqlalchemy.orm import Session
from src.v1.models.circuit import Circuit as CircuitModel
from src.v1.dto.circuits import CircuitDto

class CircuitRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_circuits(self) -> List[CircuitDto]:
        circuits = self.db.query(CircuitModel).all()
        return [CircuitDto.from_model(circuit) for circuit in circuits]
        