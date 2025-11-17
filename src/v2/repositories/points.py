from sqlalchemy.orm import Session, joinedload
from src.v2.models.result import Result as ResultModel
from src.v2.models.session import Session as SessionModel
from src.v2.models.driver import Driver as DriverModel
from sqlalchemy import func
from src.core.database import SessionLocal

class PointRepository:
    def __init__(self, db: Session):
        self.db = db
      
    def get_points(self):        
        results = (self.db.query(
                    ResultModel.driver_number,
                    DriverModel.permanentNumber.label('driver_number'),
                    func.sum(ResultModel.points).label('total_points')
                )
                .join(DriverModel, ResultModel.driver_number == DriverModel.permanentNumber)
                .join(SessionModel, ResultModel.session_id == SessionModel.id)
                .filter(SessionModel.session_type == "Race")
                .group_by(ResultModel.driver_number, DriverModel.permanentNumber)
                .order_by(func.sum(ResultModel.points).desc())
                .all())
                
        # Convert SQLAlchemy Row objects to dictionaries
        return [
            {
                'driver_number': row.driver_number,
                'total_points': float(row.total_points) if row.total_points else 0.0
            }
            for row in results
        ]

    def get_point_by_driver_number(self, driver_number: int):
        result = (self.db.query(
                    ResultModel.driver_number,
                    DriverModel.permanentNumber.label('driver_number'),
                    func.sum(ResultModel.points).label('total_points')
                )
                .join(DriverModel, ResultModel.driver_number == DriverModel.permanentNumber)
                .join(SessionModel, ResultModel.session_id == SessionModel.id)
                .filter(SessionModel.session_type == "Race")
                .filter(ResultModel.driver_number == driver_number)
                .group_by(ResultModel.driver_number, DriverModel.permanentNumber)
                .first())
        
        # Return default response if no results found
        if result is None:
            return {
                'driver_number': driver_number,
                'total_points': 0.0
            }
            
        # Convert SQLAlchemy Row to dictionary
        return {
            'driver_number': result.driver_number,
            'total_points': float(result.total_points) if result.total_points is not None else 0.0
        }

if __name__ == "__main__":
    db = SessionLocal()
    point_repository = PointRepository(db)
    points = point_repository.get_points()
    print(points)
        
