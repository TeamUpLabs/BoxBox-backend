from fastapi import APIRouter, Depends
from src.v2.repositories.circuits import CircuitRepository
from sqlalchemy.orm import Session
from src.core.database.database import get_db
from typing import Optional

router = APIRouter(prefix="/v2/circuits", tags=["circuits"])

@router.get("")
def get_circuits(circuit_id: Optional[int] = None, db: Session = Depends(get_db)):
  circuit_repository = CircuitRepository(db)
  if circuit_id:
    return circuit_repository.get_circuit_by_circuit_id(circuit_id)
  return circuit_repository.get_circuits()
