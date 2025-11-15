from .points import router as points_router
from .drivers import router as drivers_router
from .results import router as results_router
from .teams import router as teams_router
from .circuits import router as circuits_router
from .sessions import router as sessions_router

routers = [
  points_router,
  drivers_router,
  results_router,
  teams_router,
  circuits_router,
  sessions_router
]
