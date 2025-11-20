from typing import List
from sqlalchemy.orm import Session
from src.v2.models.news import News as NewsModel
from src.v2.dto.news import NewsDto

class NewsRepository:
  def __init__(self, db: Session):
    self.db = db
    
  def get_latest_news(self, limit: int = 10) -> List[NewsDto]:
    news = self.db.query(NewsModel)\
                 .order_by(NewsModel.published_at.desc())\
                 .limit(limit)\
                 .all()
    return [NewsDto.from_model(news) for news in news]