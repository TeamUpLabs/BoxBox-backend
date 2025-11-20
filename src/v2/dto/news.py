from pydantic import BaseModel
from datetime import datetime
from src.v2.models.news import News as NewsModel

class NewsDto(BaseModel):
  id: int | None = None
  display_title: str | None = None
  title: str | None = None
  summary: str | None = None
  content: str | None = None
  thumbnail: str | None = None
  url: str | None = None
  published_at: datetime | None = None
  created_at: datetime | None = None
  updated_at: datetime | None = None
  
  @classmethod
  def from_model(cls, model: NewsModel) -> "NewsDto":
    return cls(
      id=model.id,
      display_title=model.display_title,
      title=model.title,
      summary=model.description,
      content=model.content,
      thumbnail=model.thumbnail,
      url=model.url,
      published_at=model.published_at,
      created_at=model.created_at,
      updated_at=model.updated_at
    )