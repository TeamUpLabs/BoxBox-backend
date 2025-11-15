from sqlalchemy.orm import Session
from src.v1.models.result import Result as ResultModel
from sqlalchemy import func

class PointRepository:
    def __init__(self, db: Session):
        self.db = db
      
    def get_points(self):        
        results = (self.db.query(
                    ResultModel.driver_number,
                    func.sum(ResultModel.points).label('total_points')
                )
                .filter(ResultModel.session_type == "Race")
                .group_by(ResultModel.driver_number)
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
                    func.sum(ResultModel.points).label('total_points')
                )
                .filter(ResultModel.session_type == "Race")
                .filter(ResultModel.driver_number == driver_number)
                .group_by(ResultModel.driver_number)
                .first())
        
        # Convert SQLAlchemy Row objects to dictionaries
        return {
                'driver_number': result.driver_number,
                'total_points': float(result.total_points) if result.total_points else 0.0
              }
            
        
