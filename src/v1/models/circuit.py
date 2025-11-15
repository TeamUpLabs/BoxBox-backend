from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from typing import List

# Import Base from the base module to avoid circular imports
from src.core.database.base import Base

class Circuit(Base):
    """
    Circuit model representing a Formula 1 racing circuit.
    """
    __tablename__ = 'circuits'

    id = Column(Integer, primary_key=True, index=True)
    circuit_id = Column(Integer, unique=True, index=True, comment="Original circuit ID from the API")
    circuit_short_name = Column(String(100), unique=True, index=True, comment="Short reference name for the circuit")
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    country = Column(String(100), nullable=False, index=True)
    country_code = Column(String(3), nullable=True, comment="ISO 3166-1 alpha-3 country code")
    
    # Use string-based relationship to avoid circular imports
    sessions = relationship("Session", back_populates="circuit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Circuit {self.name} ({self.country})>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'circuit_id': self.circuit_id,
            'circuit_short_name': self.circuit_short_name,
            'name': self.name,
            'location': self.location,
            'country': self.country,
            'country_code': self.country_code,
        }