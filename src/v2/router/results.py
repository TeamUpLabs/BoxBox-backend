from fastapi import APIRouter, Depends
from src.v2.repositories.results import ResultRepository
from sqlalchemy.orm import Session
from src.core.database.database import get_db

router = APIRouter(prefix="/v2/results", tags=["results"])

@router.get("")
def get_results(
  driver_number: Optional[int] = None, 
  db: Session = Depends(get_db)
):
  result_repository = ResultRepository(db)
  if driver_number:
    return result_repository.get_results_by_driver_number(driver_number)
  return result_repository.get_results()

@router.get("/podiums")
def get_podiums(
  driver_number: int, 
  db: Session = Depends(get_db)
):
  result_repository = ResultRepository(db)
  return result_repository.get_podiums(driver_number)

