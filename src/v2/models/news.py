from src.core.database.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone

class News(Base):
    __tablename__ = "news"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False)
    display_title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    thumbnail = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "display_title": self.display_title,
            "description": self.description,
            "content": self.content,
            "thumbnail": self.thumbnail,
            "url": self.url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<News(id={self.id}, title={self.title}, display_title={self.display_title})>"