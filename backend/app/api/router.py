from fastapi import APIRouter

from app.api.routes import audit, file, query, workspace

api_router = APIRouter()

api_router.include_router(workspace.router)
api_router.include_router(file.router)
api_router.include_router(query.router)
api_router.include_router(audit.router)
