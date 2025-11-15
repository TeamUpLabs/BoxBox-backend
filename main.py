from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.v1.repositories.points import PointRepository
import uvicorn

app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인으로 제한하는 것이 좋습니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.v1.router import routers as v1_routers

for router in v1_routers:
    app.include_router(router)

if __name__ == "__main__":
    # 0.0.0.0으로 설정하면 모든 네트워크 인터페이스에서 접근 가능합니다.
    # 포트는 8000을 사용하지만 필요시 변경 가능합니다.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)