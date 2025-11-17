from typing import List
from sqlalchemy.orm import Session
from src.v2.models.circuit import Circuit as CircuitModel
from src.v2.dto.circuits import CircuitDto

class CircuitRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_circuits(self) -> List[CircuitDto]:
        circuits = self.db.query(CircuitModel).all()
        return [CircuitDto.from_model(circuit) for circuit in circuits]
      
    def get_circuit_by_circuit_id(self, circuit_id: int) -> CircuitDto:
        circuit = self.db.query(CircuitModel).filter(CircuitModel.circuit_id == circuit_id).first()
        return CircuitDto.from_model(circuit)
        