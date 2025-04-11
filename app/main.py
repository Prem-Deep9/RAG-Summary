"""FastAPI application entry point for MELO AI patient summaries."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.dependencies.database import sessionmanager
from app.routers import patient_summary


@asynccontextmanager
async def lifespan(_application: FastAPI):
    """
    Function that handles startup and shutdown events.
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(
    lifespan=lifespan, title="MELO AI generated patient summaries", version="0.1.0"
)


@app.get("/")
async def root():
    """Return a welcome message for the API root endpoint."""
    return {"message": "Hello from Melo!"}


# Routers
app.include_router(patient_summary.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
