from src.core.database.base import Base
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Result(Base):
    __tablename__ = "results"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    session = relationship("Session", back_populates="results")
    
    driver_number = Column(Integer, ForeignKey("drivers.permanentNumber"), nullable=False)
    driver = relationship("Driver", back_populates="results")
    
    position = Column(Float, nullable=True)
    points = Column(Float, default=0.0)
    
    status = Column(String(50), nullable=True)
    
    laps_completed = Column(Integer, nullable=True)
    
    Q1 = Column(Float, nullable=True)
    Q2 = Column(Float, nullable=True)
    Q3 = Column(Float, nullable=True)
    time = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "driver_number": self.driver_number,
            "position": self.position,
            "points": self.points,
            "status": self.status,
            "laps_completed": self.laps_completed,
            "Q1": self.Q1,
            "Q2": self.Q2,
            "Q3": self.Q3,
            "time": self.time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Result(id={self.id}, driver_number={self.driver_number}, position={self.position})>"