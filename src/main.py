"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Problem Knowledge Management System",
    description="AI-destekli Problem Bilgi Yönetim Sistemi",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """Health check endpoint — returns 200 if the API process is running."""
    return JSONResponse(
        status_code=200,
        content={"status": "success", "data": {"healthy": True}, "error": None},
    )


@app.get("/ready")
async def ready():
    """Readiness check endpoint — returns 200 when all dependencies are reachable."""
    # In the skeleton phase we return 200 unconditionally.
    # Later tasks will wire up real DB / Qdrant / Redis checks.
    return JSONResponse(
        status_code=200,
        content={"status": "success", "data": {"ready": True}, "error": None},
    )
