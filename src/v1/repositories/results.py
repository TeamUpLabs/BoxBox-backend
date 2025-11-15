from src.v1.models.result import Result as ResultModel
from sqlalchemy.orm import Session
from src.v1.dto.results import ResultDto

class ResultRepository:
  def __init__(self, db: Session):
    self.db = db
    
  def get_results(self):
    results = self.db.query(ResultModel).all()
    return [ResultDto.from_model(result) for result in results]
      
  def get_results_by_driver_number(self, driver_number):
    results = self.db.query(ResultModel).filter_by(driver_number=driver_number).all()
    return [ResultDto.from_model(result) for result in results]
  
  def get_results_by_session_key(self, session_key):
    results = self.db.query(ResultModel).filter_by(session_key=session_key).all()
    return [ResultDto.from_model(result) for result in results]
  
  def get_podiums(self, driver_number):
    results = (self.db.query(ResultModel)
               .filter_by(driver_number=driver_number)
               .filter(ResultModel.session_type == "Race")
               .filter(ResultModel.position.in_([1, 2, 3]))
               .all())
    return [ResultDto.from_model(result) for result in results]
    
  def get_wins(self, driver_number):
    results = (self.db.query(ResultModel)
               .filter_by(driver_number=driver_number)
               .filter(ResultModel.session_type == "Race")
               .filter(ResultModel.position == 1)
               .all())
    return [ResultDto.from_model(result) for result in results]
