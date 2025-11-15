from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum

class WeatherCondition(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    RAINY_CLEARING = "rainy_clearing"
    WINDY = "windy"
    HUMID = "humid"
    UNKNOWN = "unknown"

class WeatherAnalyzer:
    @staticmethod
    def analyze_weather(weather_data: List[Dict]) -> Dict[str, str]:
        if not weather_data:
            return {}
            
        results = {}
        prev_condition = None
        
        for i, data in enumerate(weather_data):
            timestamp = data.get('date', '')
            if not timestamp:
                continue
                
            # 날짜 형식 변환 (YYYY-MM-DD HH:MM:SS)
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, AttributeError):
                time_str = f"entry_{i}"
            
            # 날씨 상태 분석
            condition = WeatherAnalyzer._determine_condition(data, prev_condition)
            results[time_str] = condition.value
            prev_condition = condition
            
        return results
    
    @staticmethod
    def _determine_condition(data: Dict, prev_condition: Optional[WeatherCondition] = None) -> WeatherCondition:
        rainfall = data.get('rainfall', 0)
        wind_speed = data.get('wind_speed', 0)
        humidity = data.get('humidity', 0)
        
        if rainfall > 0:
            return WeatherCondition.RAINY
            
        # 비가 그친 후 맑아지는 경우
        if prev_condition == WeatherCondition.RAINY and rainfall == 0:
            return WeatherCondition.RAINY_CLEARING
            
        # 바람이 강한 경우
        if wind_speed > 10:  # m/s
            return WeatherCondition.WINDY
            
        # 습도가 높은 경우
        if humidity > 70:
            return WeatherCondition.HUMID
            
        # 구름 상태 (간접적으로 판단)
        track_temp = data.get('track_temperature', 0)
        air_temp = data.get('air_temperature', 0)
        temp_diff = track_temp - air_temp
        
        # 트랙 온도와 공기 온도 차이가 크지 않으면 흐림으로 판단
        if abs(temp_diff) < 2:
            return WeatherCondition.CLOUDY
            
        # 그 외의 경우 맑음으로 판단
        return WeatherCondition.CLEAR
    
    @staticmethod
    def get_weather_summary(weather_data: List[Dict]) -> Dict:
        if not weather_data:
            return {}
            
        conditions = []
        rainfall_total = 0
        max_wind_speed = 0
        temperatures = []
        humidities = []
        
        for data in weather_data:
            condition = WeatherAnalyzer._determine_condition(data)
            conditions.append(condition)
            
            rainfall_total += data.get('rainfall', 0)
            max_wind_speed = max(max_wind_speed, data.get('wind_speed', 0))
            
            if 'air_temperature' in data:
                temperatures.append(data['air_temperature'])
            if 'humidity' in data:
                humidities.append(data['humidity'])
        
        # 가장 흔한 날씨 상태 찾기
        if conditions:
            most_common_condition = max(set(conditions), key=conditions.count)
        else:
            most_common_condition = WeatherCondition.UNKNOWN
            
        # 평균 기온과 습도 계산
        avg_temp = sum(temperatures) / len(temperatures) if temperatures else None
        avg_humidity = sum(humidities) / len(humidities) if humidities else None
        
        return {
            'most_common_condition': most_common_condition.value,
            'rainfall_total': round(rainfall_total, 1),
            'max_wind_speed': round(max_wind_speed, 1),
            'avg_temperature': round(avg_temp, 1) if avg_temp is not None else None,
            'avg_humidity': round(avg_humidity, 1) if avg_humidity is not None else None,
            'condition_distribution': {cond.value: conditions.count(cond) for cond in set(conditions)}
        }
        
    def get_representative_weather(self, weather_data: List[Dict]) -> Dict:
        if not weather_data:
            return {"error": "날씨 데이터가 없습니다."}
            
        # 전체 데이터에서 날씨 상태 카운트
        conditions = [self._determine_condition(data) for data in weather_data]
        condition_counts = {}
        
        # 각 날씨 상태별로 카운트
        for condition in conditions:
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
        
        # 최대 카운트 찾기
        max_count = max(condition_counts.values())
        
        # 가장 심한 날씨 상태를 우선으로 정렬 (RAINY > WINDY > HUMID > CLOUDY > CLEAR > UNKNOWN)
        severity_order = {
            WeatherCondition.RAINY: 5,
            WeatherCondition.RAINY_CLEARING: 4,
            WeatherCondition.WINDY: 3,
            WeatherCondition.HUMID: 2,
            WeatherCondition.CLOUDY: 1,
            WeatherCondition.CLEAR: 0,
            WeatherCondition.UNKNOWN: -1
        }
        
        # 최대 카운트를 가진 조건들 중 가장 심한 날씨 선택
        max_conditions = [cond for cond, count in condition_counts.items() if count == max_count]
        most_common_condition = max(max_conditions, key=lambda x: severity_order[x])
        
        # 비율 계산
        ratio = max_count / len(weather_data) * 100
        
        # 평균 기온과 습도 계산
        avg_temp = sum(data.get('air_temperature', 0) for data in weather_data) / len(weather_data)
        avg_humidity = sum(data.get('humidity', 0) for data in weather_data) / len(weather_data)
        
        return {
            'weather_condition': most_common_condition.value,
            'condition_ratio': f"{ratio:.1f}%",
            'average_temperature': f"{avg_temp:.1f}°C",
            'average_humidity': f"{avg_humidity:.1f}%"
        }

# 사용 예시
if __name__ == "__main__":
    # 예시 데이터
    sample_data = [
        {
            "date": "2025-02-26T10:00:00+00:00",
            "session_key": 9683,
            "wind_direction": 30,
            "meeting_key": 1253,
            "wind_speed": 1.7,
            "rainfall": 0,
            "track_temperature": 17.8,
            "air_temperature": 14.6,
            "humidity": 53,
            "pressure": 1020.8
        },
        {
            "date": "2025-02-26T11:00:00+00:00",
            "session_key": 9683,
            "wind_direction": 35,
            "meeting_key": 1253,
            "wind_speed": 11.2,
            "rainfall": 0,
            "track_temperature": 16.2,
            "air_temperature": 15.1,
            "humidity": 72,
            "pressure": 1019.5
        },
        {
            "date": "2025-02-26T12:00:00+00:00",
            "session_key": 9683,
            "wind_direction": 40,
            "meeting_key": 1253,
            "wind_speed": 8.5,
            "rainfall": 5.2,
            "track_temperature": 15.8,
            "air_temperature": 14.9,
            "humidity": 85,
            "pressure": 1018.3
        }
    ]
    
    # 날씨 분석 실행
    analyzer = WeatherAnalyzer()
    
    # 대표 날씨 정보 조회 및 출력
    weather_info = analyzer.get_representative_weather(sample_data)
    print("\n=== 대표 날씨 정보 ===")
    print(weather_info)
