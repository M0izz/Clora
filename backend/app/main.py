from contextlib import asynccontextmanager

from app.api.router import api_router
from app.core.config import settings
from app.db import database
from app.services.agent_service import recover_zombie_queries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager:
    1. Provisions physical storage directories.
    2. Initializes database schemas.
    3. Executes startup zombie query recovery sweep.
    """
    # 1. Ensure storage root exists
    ws_dir = settings.STORAGE_DIR / "workspaces"
    ws_dir.mkdir(parents=True, exist_ok=True)

    # 2. Initialize DB tables
    database.Base.metadata.create_all(bind=database.engine)

    # 3. Startup Sweep: Transition stuck queries from previous restarts into 'failed'
    db = database.SessionLocal()
    try:
        recover_zombie_queries(db)
    finally:
        db.close()

    yield

    # Teardown logic if needed


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title="INDUSAI-X Backend API",
        description="Industrial Intelligence Platform - Multi-Agent Orchestration & Persistence Spine",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount health checks
    app.include_router(health.router)

    # Mount core API endpoints under /api
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()
