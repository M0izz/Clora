"""
FastAPI application for INDUSAI-X inference backend.
Run:  uvicorn app.api.main:app --reload --port 8000
"""
from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.inference import InferenceService, OllamaClient
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-22s  %(levelname)-5s  %(message)s",
)
logger = logging.getLogger("indusai.api")


# ---------------------------------------------------------------------------
# Lifespan — initialise / tear down shared resources
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start up: create the inference service, health-check Ollama."""
    client = OllamaClient()
    service = InferenceService(client)

    healthy = await client.health()
    if healthy:
        logger.info("✓ Ollama is reachable at %s", settings.ollama_base_url)
    else:
        logger.warning(
            "✗ Ollama NOT reachable at %s — inference calls will fail until it starts",
            settings.ollama_base_url,
        )

    # Store on app.state so routes can access via request.app.state
    app.state.inference = service

    yield

    await service.close()
    logger.info("Inference service shut down.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="INDUSAI-X Inference API",
    description="Sovereign, on-premise AI inference powered by Ollama — no cloud APIs.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register routes -------------------------------------------------------
from app.api.routes.generate import router as generate_router  # noqa: E402

app.include_router(generate_router, prefix=settings.api_prefix)
