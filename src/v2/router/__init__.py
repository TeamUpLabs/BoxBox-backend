from .teams import router as teams_router
from .drivers import router as drivers_router
from .circuits import router as circuits_router
from .sessions import router as sessions_router
from .results import router as results_router
from .news import router as news_router

routers = [
  teams_router,
  drivers_router,
  circuits_router,
  sessions_router,
  results_router,
  news_router,
]
