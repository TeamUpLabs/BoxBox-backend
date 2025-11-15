from fastapi import APIRouter, Depends
from src.v1.repositories.circuits import CircuitRepository
from sqlalchemy.orm import Session
from src.core.database.database import get_db

router = APIRouter(prefix="/v1/circuits", tags=["circuits"])

@router.get("")
def get_circuits(db: Session = Depends(get_db)):
  circuit_repository = CircuitRepository(db)
  return circuit_repository.get_circuits()
