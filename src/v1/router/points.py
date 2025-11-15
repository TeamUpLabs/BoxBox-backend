from fastapi import APIRouter, Depends, HTTPException
from src.v1.repositories.points import PointRepository
from sqlalchemy.orm import Session
from typing import Optional
from src.core.database.database import get_db

router = APIRouter(prefix="/v1/points", tags=["points"])

@router.get("")
def get_points(
    driver_number: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        point_repository = PointRepository(db)
        
        if driver_number:
            return point_repository.get_point_by_driver_number(driver_number)
        return point_repository.get_points()
    except Exception as e:
        print(f"Error in get_points: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
