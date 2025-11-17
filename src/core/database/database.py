from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from .base import Base  # Import Base from base.py

load_dotenv()

# 데이터베이스 URL
DATABASE_URL = os.getenv("SUPABASE_DB_URL", "sqlite:///./test.db")

# 데이터베이스 타입 확인
is_postgresql = DATABASE_URL.startswith("postgresql")

# 연결 인자 설정 (PostgreSQL과 SQLite에서 다르게 설정)
if is_postgresql:
    connect_args = {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5,
    }
else:
    connect_args = {"check_same_thread": False}

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Increased from 5
    max_overflow=20,  # Increased from 10
    pool_timeout=60,  # Increased from 30
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=300,  # Recycle connections after 5 minutes (reduced from 30)
    pool_use_lifo=True,  # Use last-in-first-out for better connection reuse
    connect_args=connect_args,
    echo=False  # Set to True for debugging SQL queries
)

try:
  engine.connect()
  print("✅ Database connection successful!")
except Exception as e:
  print(f"❌ Database connection failed: {str(e)}")
  raise

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    데이터베이스 세션을 생성하고 관리하는 의존성 함수
    FastAPI의 Depends와 함께 사용
    """
    # Import all models to ensure they are loaded
    from src.v2.models import Circuit, Session, Driver, Team, Result
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()