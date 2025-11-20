"""
Central import point for all SQLAlchemy models.
This helps avoid circular imports by ensuring all models are loaded before relationships are set up.
"""
# Import all models here to ensure they are loaded before relationships are set up
from .circuit import Circuit
from .session import Session
from .driver import Driver
from .team import Team
from .result import Result
from .news import News

# This ensures that all models are properly imported and their metadata is available
__all__ = ['Circuit', 'Session', 'Driver', 'Team', 'Result', 'News']
