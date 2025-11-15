from pydantic import BaseModel
from datetime import datetime
from src.v1.models.result import Result as ResultModel

class ResultDto(BaseModel):
  id: int | None = None
  session_key: int | None = None
  meeting_key: int | None = None
  session_type: str | None = None
  driver_number: int | None = None
  position: int | None = None
  points: float | None = None
  status: str | None = None
  dnf: bool = False
  dns: bool = False
  dsq: bool = False
  laps_completed: int = 0
  time: float | None = None
  gap_to_leader: float | None = None
  created_at: datetime | None = None
  updated_at: datetime | None = None
  
  class Config:
    allow_population_by_field_name = True
    
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
      session_key=cls._parse_int_value(result.session_key),
      meeting_key=cls._parse_int_value(result.meeting_key),
      session_type=result.session_type,
      driver_number=cls._parse_int_value(result.driver_number),
      position=cls._parse_int_value(result.position),
      points=cls._parse_float_value(result.points),
      status=result.status,
      dnf=bool(result.dnf) if result.dnf is not None else False,
      dns=bool(result.dns) if result.dns is not None else False,
      dsq=bool(result.dsq) if result.dsq is not None else False,
      laps_completed=cls._parse_int_value(result.laps_completed) or 0,
      time=cls._parse_time_value(result.time),
      gap_to_leader=cls._parse_time_value(result.gap_to_leader),
      created_at=result.created_at,
      updated_at=result.updated_at
    )