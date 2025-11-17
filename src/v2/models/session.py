from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
import json

from src.core.database.base import Base

class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    round = Column(Integer, nullable=False, comment="Race round number in the season")
    session_type = Column(String(50), nullable=False, comment="e.g., Practice, Qualifying, Race")
    session_name = Column(String(100), nullable=False, comment="e.g., FP1, FP2, FP3, Qualifying, Race")
    session_date = Column(DateTime, nullable=False)
    circuit_id = Column(Integer, ForeignKey('circuits.circuit_id', ondelete='CASCADE'), nullable=False, index=True)
    
    status = Column(String(50), default='Scheduled', comment="e.g., Scheduled, In Progress, Completed, Cancelled")
    
    # Weather data (can be stored as JSON for flexibility)
    weather = Column(JSON, nullable=True, comment="Weather conditions during the session")
    
    # Relationships
    circuit = relationship("Circuit", back_populates="sessions")
    # Relationship to results
    results = relationship("Result", back_populates="session", lazy="dynamic")
    
    # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Session {self.year} {self.round} {self.session_name}>"
      
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        return {
            "id": self.id,
            "year": self.year,
            "round": self.round,
            "session_type": self.session_type,
            "session_name": self.session_name,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "circuit_id": self.circuit_id,
            "status": self.status,
            "weather": json.loads(self.weather) if isinstance(self.weather, str) else self.weather,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }