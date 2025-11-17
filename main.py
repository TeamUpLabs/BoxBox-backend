from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import Settings
import uvicorn

settings = Settings()
app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인으로 제한하는 것이 좋습니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# from src.v1.router import routers as v1_routers
from src.v2.router import routers as v2_routers

# for router in v1_routers:
#     app.include_router(router)
    
for router in v2_routers:
    app.include_router(router)

@app.get("/")
async def root():
  return {
    "name": settings.TITLE,
    "version": settings.VERSION,
    "status": settings.STATUS,
    "api_title": settings.API_TITLE,
    "api_version": settings.API_VERSION,
    "now": settings.now
  }

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # 0.0.0.0으로 설정하면 모든 네트워크 인터페이스에서 접근 가능합니다.
    # 포트는 8000을 사용하지만 필요시 변경 가능합니다.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
