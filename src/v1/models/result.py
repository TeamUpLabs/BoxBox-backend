from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, backref

from src.core.database.base import Base

class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Session and race information
    session_key = Column(Integer, ForeignKey('sessions.session_key'), nullable=False, index=True)
    meeting_key = Column(Integer, nullable=False, index=True)
    session_type = Column(String(50), nullable=False)
    
    # Driver information
    driver_number = Column(Integer, ForeignKey("drivers.permanentNumber"), nullable=False)
    
    # Position and timing
    position = Column(Integer, nullable=True)  # Finishing position
    points = Column(Float, default=0.0)
    
    # Race status
    status = Column(String(50), nullable=True)  # e.g., 'Finished', 'Accident', 'Engine', etc.
    dnf = Column(Boolean, default=False)
    dns = Column(Boolean, default=False)
    dsq = Column(Boolean, default=False)
    
    # Lap information
    laps_completed = Column(Integer, default=0)
    
    # Timing data - both can be float or list of floats
    time = Column(JSON, nullable=True, comment="Can be float (seconds) or list of sector times")
    gap_to_leader = Column(JSON, nullable=True, comment="Can be float (seconds) or list of gaps")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (using string-based references to avoid circular imports)
    driver = relationship("Driver", back_populates="results")
    session = relationship("Session", back_populates="results")
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "session_key": self.session_key,
            "meeting_key": self.meeting_key,
            "driver_number": self.driver_number,
            "position": self.position,
            "points": float(self.points) if self.points is not None else None,
            "status": self.status,
            "dnf": self.dnf,
            "laps_completed": self.laps_completed,
            "time": self.time if not isinstance(self.time, (list, dict)) else list(self.time),
            "gap_to_leader": self.gap_to_leader,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Result(driver={self.driver_number}, position={self.position}, points={self.points})>"