from fastapi import APIRouter

from backend.app.api.routes import agents, audit, file, health, ingestion, models, query, sovereignty, workspace
from app.api.routes.generate import router as ai_router

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(workspace.router)
api_router.include_router(file.router)
api_router.include_router(ingestion.router)
api_router.include_router(query.router)
api_router.include_router(models.router)
api_router.include_router(agents.router)
api_router.include_router(audit.router)
api_router.include_router(sovereignty.router)
api_router.include_router(ai_router, prefix="/ai", tags=["Member 4: Local LLM Inference"])


