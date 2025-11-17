from pydantic import BaseModel
from datetime import datetime
from src.v2.models.result import Result as ResultModel

class ResultDto(BaseModel):
  id: int | None = None
  session_id: int | None = None
  driver_number: int | None = None
  position: int | None = None
  points: float | None = None
  status: str | None = None
  laps_completed: int | None = None
  Q1: float | None = None
  Q2: float | None = None
  Q3: float | None = None
  time: float | None = None
  created_at: datetime | None = None
  updated_at: datetime | None = None
  
  @classmethod
  def _parse_int_value(cls, value):
    if value is None:
      return None
    try:
      return int(value)
    except (TypeError, ValueError):
      return None
      
  @classmethod
  def _parse_float_value(cls, value):
    if value is None:
      return None
    try:
      return float(value)
    except (TypeError, ValueError):
      return None
      
  @classmethod
  def _parse_time_value(cls, value):
    if value is None:
      return None
    try:
      if isinstance(value, list):
        if value:  # Non-empty list
          return float(value[0])
        return None
      return float(value)
    except (TypeError, ValueError):
      return None
    
  @classmethod
  def from_model(cls, result: ResultModel) -> 'ResultDto':
    return cls(
      id=cls._parse_int_value(result.id),
      session_id=cls._parse_int_value(result.session_id),
      driver_number=cls._parse_int_value(result.driver_number),
      position=cls._parse_int_value(result.position),
      points=cls._parse_float_value(result.points),
      status=result.status,
      laps_completed=cls._parse_int_value(result.laps_completed) or 0,
      Q1=cls._parse_time_value(result.Q1),
      Q2=cls._parse_time_value(result.Q2),
      Q3=cls._parse_time_value(result.Q3),
      time=cls._parse_time_value(result.time),
      created_at=result.created_at,
      updated_at=result.updated_at
    )