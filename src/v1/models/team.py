from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, backref

from src.core.database.base import Base

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    constructorId = Column(String, nullable=False, index=True, unique=True)
    name = Column(String, nullable=False)
    nationality = Column(String, nullable=False)
    teamColor = Column(String, nullable=False)
    logoURL = Column(String, nullable=False)
    carURL = Column(String, nullable=False)
    countryFlagURL = Column(String, nullable=False)
    
    drivers = relationship("Driver", back_populates="team", foreign_keys="Driver.currentTeam")
    
    def to_dict(self):
        return {
            "constructorId": self.constructorId,
            "name": self.name,
            "nationality": self.nationality,
            "teamColor": self.teamColor,
            "logoURL": self.logoURL,
            "carURL": self.carURL,
            "countryFlagURL": self.countryFlagURL
        }
    
    def __repr__(self):
        return f"<Team(constructorId={self.constructorId}, name={self.name}, nationality={self.nationality}, teamColor={self.teamColor}, logoURL={self.logoURL}, carURL={self.carURL}, countryFlagURL={self.countryFlagURL})>"
        
    
