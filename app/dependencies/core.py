"""
Core dependencies module.

This module provides common FastAPI dependency types and utilities
used across the application.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db_session

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
