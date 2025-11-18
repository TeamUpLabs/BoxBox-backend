import pandas as pd
import numpy as np
import json
from typing import Dict, Any, List, Optional, Union
from enum import Enum

class WeatherCondition(str, Enum):
    DRY = "dry"
    DRIZZLE = "drizzle"
    RAINY = "rainy"
    RAINY_CLEARING = "rainy_clearing"
    WINDY = "windy"
    HUMID = "humid"
    UNKNOWN = "unknown"

def analyze_weather_conditions(weather_data: Union[Dict, List[Dict], pd.DataFrame]) -> Dict[str, Any]:
    """
    Analyze weather data and determine detailed weather conditions.
    
    Args:
        weather_data: Weather data as a dictionary, list of dictionaries, or pandas DataFrame
                     Expected keys/columns: Time, AirTemp, Humidity, Pressure, Rainfall, TrackTemp, WindDirection, WindSpeed
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - weather_condition (str): One of 'dry', 'drizzle', 'rainy', 'rainy_clearing', 'windy', 'humid', 'unknown'
            - condition_ratio (float): Ratio of wet samples to total samples
            - average_temperature (float): Average air temperature in Celsius
            - average_humidity (float): Average humidity in percentage
            - wind_speed (float): Average wind speed in km/h
    """
    # Convert input to DataFrame if it's not already
    if not isinstance(weather_data, pd.DataFrame):
        if isinstance(weather_data, str):
            try:
                weather_data = json.loads(weather_data)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string provided")
        df = pd.DataFrame(weather_data)
    else:
        df = weather_data.copy()
    
    # Convert Time to datetime if it's a string
    if 'Time' in df.columns and df['Time'].dtype == 'object':
        # Handle different time string formats
        try:
            df['Time'] = pd.to_timedelta(df['Time'].str.extract(r'(\d+:\d+:\d+(?:\.\d+)?)')[0])
        except:
            try:
                df['Time'] = pd.to_datetime(df['Time'])
            except:
                pass
    
    # Calculate basic statistics
    total_samples = len(df)
    if total_samples == 0:
        return {
            'weather_condition': WeatherCondition.UNKNOWN.value,
            'condition_ratio': 0.0,
            'average_temperature': 0.0,
            'average_humidity': 0.0,
            'wind_speed': 0.0
        }
    
    # Calculate condition ratio and rain statistics
    has_rainfall = 'Rainfall' in df.columns
    if has_rainfall:
        if df['Rainfall'].dtype == 'bool':
            wet_samples = df['Rainfall'].sum()
        else:
            # Handle case where Rainfall might be 0/1 or 'True'/'False' strings
            wet_samples = df['Rainfall'].astype(str).str.lower().map({'true': True, 'false': False, '1': True, '0': False}).fillna(False).sum()
    else:
        wet_samples = 0
    
    condition_ratio = wet_samples / total_samples if has_rainfall else 0.0
    
    # Calculate averages with error handling
    try:
        avg_temp = df['AirTemp'].mean()
        avg_humidity = df['Humidity'].mean()
        avg_wind_speed = df['WindSpeed'].mean() if 'WindSpeed' in df.columns else 0.0
    except Exception as e:
        print(f"Error calculating averages: {e}")
        avg_temp = 0.0
        avg_humidity = 0.0
        avg_wind_speed = 0.0
    
    # Determine weather condition
    weather_condition = _determine_detailed_condition(
        condition_ratio=condition_ratio,
        avg_humidity=avg_humidity,
        avg_wind_speed=avg_wind_speed,
        weather_data=df
    )
    
    return {
        'weather_condition': weather_condition.value,
        'condition_ratio': f"{round(condition_ratio, 2) * 100}%",
        'average_temperature': f"{round(float(avg_temp), 1)}°C",
        'average_humidity': f"{round(float(avg_humidity), 1)}%",
        'wind_speed': f"{round(float(avg_wind_speed), 1)}km/h"
    }

def _determine_detailed_condition(condition_ratio: float, avg_humidity: float, 
                                avg_wind_speed: float, weather_data: pd.DataFrame) -> WeatherCondition:
    """Determine the detailed weather condition based on various factors."""
    # Check for windy conditions first (takes precedence over other conditions)
    if avg_wind_speed > 30:  # km/h
        return WeatherCondition.WINDY
        
    # Check humidity conditions
    if avg_humidity > 80:
        return WeatherCondition.HUMID
    
    # Check rain-related conditions
    if condition_ratio > 0.5:  # More than 50% of the time it was raining
        # Check if rain is clearing (decreasing trend in rainfall)
        if 'Rainfall' in weather_data.columns and len(weather_data) > 1:
            try:
                rain_changes = weather_data['Rainfall'].astype(str).str.lower().map(
                    {'true': 1, 'false': 0, '1': 1, '0': 0, 1: 1, 0: 0, True: 1, False: 0}
                ).diff().dropna()
                if len(rain_changes) > 0 and rain_changes.iloc[-1] < 0:
                    return WeatherCondition.RAINY_CLEARING
            except:
                pass
        return WeatherCondition.RAINY
    elif condition_ratio > 0.1:  # Light rain/drizzle
        return WeatherCondition.DRIZZLE
    
    # Default to dry if no other conditions are met
    return WeatherCondition.DRY

# Example usage with provided data
if __name__ == "__main__":
    from src.core.database.database import SessionLocal
    from src.v2.models.session import Session as SessionModel
    
    db = SessionLocal()
    
    example_data = db.query(SessionModel).filter(SessionModel.year == 2025, SessionModel.round == 1, SessionModel.session_type == "Practice").first().weather
    
    print("Analyzing weather data...")
    analysis = analyze_weather_conditions(example_data)
    
    print("\nWeather Analysis:")
    for key, value in analysis.items():
        print(f"{key}: {value}")
