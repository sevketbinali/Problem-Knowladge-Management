"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.v1.analysis import router as analysis_router
from src.api.v1.auth import router as auth_router
from src.api.v1.health import router as health_router
from src.api.v1.knowledge import router as knowledge_router
from src.api.v1.records import router as records_router
from src.api.v1.sessions import router as session_router

from src.infrastructure.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup: Initialize DB and Admin
    await init_db()
    yield


app = FastAPI(
    title="Problem Knowledge Management System",
    description="AI-destekli Problem Bilgi Yönetim Sistemi",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware - Allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers (Task 21.6)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "data": None,
            "error": str(exc.detail),
            "message": None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "data": None,
            "error": "Internal Server Error",
            "message": str(exc) if not app.debug else None
        }
    )

# Register routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(session_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(records_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
