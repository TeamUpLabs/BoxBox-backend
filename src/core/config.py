from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import cached_property
from zoneinfo import ZoneInfo
from datetime import datetime

class Settings(BaseSettings):
  model_config = ConfigDict(
    ignored_types=(cached_property,),
    env_file=".env",
    extra="allow"  # This will allow extra fields from .env without validation errors
  )
  
  # Supabase configuration
  SUPABASE_URL: str = ""
  SUPABASE_KEY: str = ""
  SUPABASE_DB_URL: str = ""
  
  TITLE: str = "F1 App"
  VERSION: str = "1.0.0"
  DESCRIPTION: str = "F1 App API"
  STATUS: str = "active"
  DEBUG: bool = True
  
  TIMEZONE: str = "Asia/Seoul"
  
  @property
  def API_VERSION(self) -> str:
    return f"v{self.VERSION}"
  
  @property
  def API_TITLE(self) -> str:
    return f"{self.TITLE} {self.API_VERSION}"

  @cached_property
  def timezone(self) -> ZoneInfo:
    return ZoneInfo(self.TIMEZONE)

  @property
  def now(self) -> datetime:
    return datetime.now(tz=self.timezone)
  