"""
FastAPI Main Application for INDUSAI-X Sovereign Backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.graph.routes import routes as graph_router
from data_intelligence.api_router import router as member6_router
from app.api.routes.generate import router as member4_router

app = FastAPI(
    title="INDUSAI-X Sovereign Agentic AI Workbench",
    description="Backend Intelligence Backbone for MRPL (SIH26117)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph_router, prefix="/api/v1")
app.include_router(member6_router, prefix="/api/v1")
app.include_router(member4_router, prefix="/api/v1/ai", tags=["Member 4: Local LLM Inference"])



@app.get("/health")
async def health():
    return {
        "status": "HEALTHY",
        "app": "INDUSAI-X",
        "sovereign_mode": "AIR_GAPPED_READY",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
