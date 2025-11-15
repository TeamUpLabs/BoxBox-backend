from pydantic import BaseModel
from src.v1.models.session import Session as SessionModel
from src.v1.dto.results import ResultDto
from src.v1.utils.weather_analyzer import WeatherAnalyzer
from datetime import datetime
from typing import List, Dict, Optional

class SessionDto(BaseModel):
  id: int
  year: int
  round: int
  session_key: int
  session_type: str
  session_name: str
  session_date: datetime
  circuit_id: int
  status: str
  weather: Optional[Dict[str, str]] = None
  created_at: datetime
  updated_at: datetime
  
  results: List[ResultDto]
  
  class Config:
    allow_population_by_field_name = True
    
  @classmethod
  def from_model(cls, session: SessionModel) -> 'SessionDto':
    # Get representative weather data if available
    weather = None
    if session.weather and isinstance(session.weather, list):
      analyzer = WeatherAnalyzer()
      weather = analyzer.get_representative_weather(session.weather)
    elif session.weather and isinstance(session.weather, dict):
      # Handle case where weather is a single data point
      analyzer = WeatherAnalyzer()
      weather = analyzer.get_representative_weather([session.weather])
      
    return cls(
      id=session.id,
      year=session.year,
      round=session.round % 1253,  # 2025년은 meeting key 1253가 1라운드
      session_key=session.session_key,
      session_type=session.session_type,
      session_name=session.session_name,
      session_date=session.session_date,
      circuit_id=session.circuit_id,
      status=session.status,
      weather=weather,
      created_at=session.created_at,
      updated_at=session.updated_at,
      results=[ResultDto.from_model(result) for result in (session.results or [])]
    )
  
