from fastapi import APIRouter, Depends
from src.v2.repositories.drivers import DriverRepository
from sqlalchemy.orm import Session
from src.core.database.database import get_db

router = APIRouter(prefix="/v2/drivers", tags=["drivers"])

@router.get("")
def get_drivers(db: Session = Depends(get_db)):
  driver_repository = DriverRepository(db)
  return driver_repository.get_drivers()
