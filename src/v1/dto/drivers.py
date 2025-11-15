from pydantic import BaseModel, Field
from datetime import date
from src.v1.models.driver import Driver

class DriverStats(BaseModel):
    points: int = 0
    podiums: int = 0
    wins: int = 0

class DriverDto(BaseModel):
    id: int
    driver_number: int
    family_name: str
    given_name: str
    name_acronym: str
    date_of_birth: date
    nationality: str
    headshot_url: str
    country_flag_url: str
    team: str
    stats: DriverStats
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            date: lambda d: d.strftime('%Y-%m-%d')
        }
    
    @classmethod
    def from_model(
        cls,
        driver: Driver,
        points: int = 0,
        podiums: int = 0,
        wins: int = 0
    ) -> 'DriverDto':
        return cls(
            id=driver.id,
            driver_number=driver.permanentNumber,
            family_name=driver.familyName,
            given_name=driver.givenName,
            name_acronym=driver.nameAcronym,
            date_of_birth=driver.dateOfBirth,
            nationality=driver.nationality,
            headshot_url=driver.headshotURL,
            country_flag_url=driver.countryFlagURL,
            team=driver.currentTeam,
            stats=DriverStats(points=points, podiums=podiums, wins=wins)
        )