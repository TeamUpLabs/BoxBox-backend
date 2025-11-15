# Import all models here to ensure they are registered with SQLAlchemy
from .circuit import Circuit
from .session import Session
from .driver import Driver
from .team import Team
from .result import Result

# This ensures that SQLAlchemy can discover all models
__all__ = ['Circuit', 'Session', 'Driver', 'Team', 'Result']
