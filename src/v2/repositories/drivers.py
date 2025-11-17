from typing import List
from sqlalchemy.orm import Session
from src.v2.models.driver import Driver as DriverModel
from src.v2.repositories.points import PointRepository
from src.v2.repositories.results import ResultRepository
from src.v2.dto.drivers import DriverDto

class DriverRepository:
    def __init__(self, db: Session):
        self.db = db
        self.point_repository = PointRepository(db)
        self.result_repository = ResultRepository(db)
        
    def get_drivers(self) -> List[DriverDto]:
        drivers = self.db.query(DriverModel).all()
        results = []
        
        for driver in drivers:
            points = self.point_repository.get_point_by_driver_number(driver.permanentNumber)["total_points"]
            podiums = len(self.result_repository.get_podiums(driver.permanentNumber))
            wins = len(self.result_repository.get_wins(driver.permanentNumber))
            
            driver_dto = DriverDto.from_model(
                driver=driver,
                points=points,
                podiums=podiums,
                wins=wins
            )
            results.append(driver_dto)
        
        return results
