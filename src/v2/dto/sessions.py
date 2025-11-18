from pydantic import BaseModel
from typing import Optional, Dict, List, Union
from datetime import datetime
import numpy as np
from src.v2.models.session import Session as SessionModel
from src.v2.dto.results import ResultDto
from src.v2.utils.analyze_weather import analyze_weather_conditions

class WeatherData(BaseModel):
    weather_condition: str
    condition_ratio: str
    average_temperature: str
    average_humidity: str
    wind_speed: str

class SessionDto(BaseModel):
    id: int
    year: int
    round: int
    session_type: str
    session_name: str
    session_date: datetime
    circuit_id: int
    status: str
    weather: Optional[WeatherData] = None
    created_at: datetime
    updated_at: datetime
    results: List[ResultDto]
    
    class Config:
        orm_mode = True
        json_encoders = {
            np.float64: float  # Ensure numpy types are properly serialized
        }
        
    @classmethod
    def from_model(cls, session: SessionModel) -> 'SessionDto':
        # Get representative weather data if available
        weather = None
        if session.weather and isinstance(session.weather, list):
            weather_data = analyze_weather_conditions(session.weather)
            weather = WeatherData(**weather_data)
        elif session.weather and isinstance(session.weather, dict):
            # Handle case where weather is a single data point
            weather_data = analyze_weather_conditions([session.weather])
            weather = WeatherData(**weather_data)
            
        return cls(
            id=session.id,
            year=session.year,
            round=session.round,
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
