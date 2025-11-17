from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from src.core.database.base import Base

class Driver(Base):
    __tablename__ = "drivers"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, unique=True)
    driverId = Column(String, nullable=False, unique=True)
    permanentNumber = Column(Integer, nullable=False, unique=True)
    givenName = Column(String, nullable=False)
    familyName = Column(String, nullable=False)
    nameAcronym = Column(String, nullable=False)
    dateOfBirth = Column(DateTime, nullable=False)
    nationality = Column(String, nullable=False)
    headshotURL = Column(String, nullable=False)
    countryFlagURL = Column(String, nullable=False)
    currentTeam = Column(String, ForeignKey("teams.constructorId"), nullable=False)
    
    results = relationship("Result", back_populates="driver")
    team = relationship("Team", back_populates="drivers", foreign_keys=[currentTeam])
    
    def to_dict(self):
        return {
            "driverId": self.driverId,
            "permanentNumber": self.permanentNumber,
            "givenName": self.givenName,
            "familyName": self.familyName,
            "nameAcronym": self.nameAcronym,
            "dateOfBirth": self.dateOfBirth,
            "nationality": self.nationality,
            "headshotURL": self.headshotURL,
            "countryFlagURL": self.countryFlagURL,
            "currentTeam": self.currentTeam
        }
    
    def __repr__(self):
        return f"<Driver(driverId={self.driverId}, permanentNumber={self.permanentNumber}, givenName={self.givenName}, familyName={self.familyName}, nameAcronym={self.nameAcronym}, dateOfBirth={self.dateOfBirth}, nationality={self.nationality}, headshotURL={self.headshotURL}, countryFlagURL={self.countryFlagURL}, currentTeam={self.currentTeam})>"
    