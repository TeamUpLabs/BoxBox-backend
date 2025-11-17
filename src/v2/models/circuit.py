from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from typing import List, Dict, Any, Optional
import json

from src.core.database.base import Base

class Circuit(Base):
    """
    Circuit model representing a Formula 1 racing circuit.
    """
    __tablename__ = 'circuits'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    circuit_id = Column(Integer, unique=True, index=True, comment="Original circuit ID from the API")
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    country = Column(String(100), nullable=False, index=True)
    country_code = Column(String(3), nullable=True, comment="ISO 3166-1 alpha-3 country code")
    circuit_info = Column(JSON, nullable=True, comment="Circuit information")
    
    # Use string-based relationship to avoid circular imports
    sessions = relationship("Session", back_populates="circuit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Circuit {self.name} ({self.country})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'circuit_id': self.circuit_id,
            'name': self.name,
            'location': self.location,
            'country': self.country,
            'country_code': self.country_code,
            'circuit_info': json.loads(self.circuit_info) if isinstance(self.circuit_info, str) else self.circuit_info
        }