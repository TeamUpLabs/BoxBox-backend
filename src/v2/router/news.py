from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.database.database import get_db
from src.v2.repositories.news import NewsRepository

router = APIRouter(prefix="/v2/news", tags=["news"])

@router.get("")
def get_news(
  limit: int = 10,
  db: Session = Depends(get_db)
):
  news_repository = NewsRepository(db)
  return news_repository.get_latest_news(limit)

  
