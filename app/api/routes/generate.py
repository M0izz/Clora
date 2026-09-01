"""
Inference API routes for INDUSAI-X.
Endpoints: generate, stream, models, health.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.ai.models import UnsupportedModelError, list_models, resolve_model, DEFAULT_MODEL
from app.ai.prompts import list_tasks
from app.ai.inference import InferenceService, UnsafePromptError

logger = logging.getLogger("indusai.routes")
router = APIRouter(tags=["inference"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The user prompt to process")
    model: Optional[str] = Field(None, description="Ollama model tag (uses default if omitted)")
    task: str = Field("general", description="Task type: general, summarize, classify, reason, extract, translate, tabular")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=8192)
    images: Optional[list[str]] = Field(None, description="Optional list of base64 encoded images for VLM models")
    check_safety: bool = Field(True, description="Whether to check prompt against injection guard")


class GenerateResponse(BaseModel):
    model: str
    response: str
    tokens_generated: int | None = None
    latency_s: float | None = None
    done: bool = True


class GuardScanRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Prompt text to scan for injection or jailbreak patterns")


class GuardSanitizeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Prompt text to sanitize")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_service(request: Request) -> InferenceService:
    if hasattr(request.app.state, "inference") and request.app.state.inference is not None:
        return request.app.state.inference
    return InferenceService()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/health", summary="Health check")
async def health(request: Request):
    service = _get_service(request)
    ollama_ok = await service.client.health()
    return {
        "status": "ok" if ollama_ok else "degraded",
        "ollama": "reachable" if ollama_ok else "unreachable",
        "default_model": DEFAULT_MODEL,
    }


@router.get("/models", summary="List registered models")
async def get_models():
    return {"models": list_models()}


@router.get("/models/status", summary="Model availability in Ollama")
async def models_status(request: Request):
    service = _get_service(request)
    registered = list_models()
    local = await service.client.list_local_models()
    local_names = {m.get("name", "") for m in local}

    for m in registered:
        m["available"] = any(n.startswith(m["name"]) for n in local_names)

    return {"models": registered, "ollama_model_count": len(local)}


@router.get("/tasks", summary="List available task types")
async def get_tasks():
    return {"tasks": list_tasks()}


@router.post("/generate", summary="Full text generation", response_model=GenerateResponse)
async def generate(body: GenerateRequest, request: Request):
    service = _get_service(request)
    try:
        result = await service.run(
            prompt=body.prompt,
            task=body.task,
            model=body.model,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
            images=body.images,
            check_safety=body.check_safety,
        )
    except (UnsupportedModelError, UnsafePromptError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Inference failed")
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}")

    return GenerateResponse(
        model=result.get("model", body.model or DEFAULT_MODEL),
        response=result.get("response", ""),
        tokens_generated=result.get("eval_count"),
        latency_s=result.get("_latency_s"),
    )


@router.post("/generate/stream", summary="Streaming text generation (SSE)")
async def generate_stream(body: GenerateRequest, request: Request):
    service = _get_service(request)

    try:
        resolve_model(body.model)  # validate early
    except UnsupportedModelError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    async def event_generator():
        try:
            async for chunk in service.run_stream(
                prompt=body.prompt,
                task=body.task,
                model=body.model,
                temperature=body.temperature,
                max_tokens=body.max_tokens,
                images=body.images,
                check_safety=body.check_safety,
            ):
                token = chunk.get("response", "")
                done = chunk.get("done", False)
                yield {
                    "event": "token",
                    "data": json.dumps({"token": token, "done": done}),
                }
                if done:
                    yield {
                        "event": "done",
                        "data": json.dumps({
                            "model": chunk.get("model", ""),
                            "tokens_generated": chunk.get("eval_count"),
                        }),
                    }
        except UnsafePromptError as exc:
            yield {"event": "error", "data": json.dumps({"error": str(exc)})}
        except Exception as exc:
            logger.exception("Streaming failed")
            yield {"event": "error", "data": json.dumps({"error": str(exc)})}

    return EventSourceResponse(event_generator())


class SwitchModelRequest(BaseModel):
    model: str = Field(..., description="Model tag to set as active default")


@router.post("/models/switch", summary="Switch the active default model")
async def switch_model(body: SwitchModelRequest, request: Request):
    """
    Validate the requested model is registered and available, then update
    the module-level DEFAULT_MODEL. Note: this is process-local, not persistent.
    """
    try:
        resolve_model(body.model)
    except UnsupportedModelError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Check availability in Ollama
    service = _get_service(request)
    available = await service.client.is_model_available(body.model)
    if not available:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{body.model}' is registered but not pulled in Ollama. Run: ollama pull {body.model}",
        )

    # Update module-level default (process-scoped)
    import app.ai.models as models_mod
    models_mod.DEFAULT_MODEL = body.model
    logger.info("Default model switched to %s", body.model)

    return {"status": "ok", "default_model": body.model}



@router.post("/guard/scan", summary="Scan prompt for injection/jailbreak patterns")
async def guard_scan(body: GuardScanRequest):
    from app.ai.guard import scan_prompt
    result = scan_prompt(body.prompt)
    return {
        "level": result.level.value,
        "is_safe": result.level.value in ["safe", "low"],
        "flags": result.flags,
        "reason": result.reason,
        "sanitized": result.sanitized,
    }


@router.post("/guard/sanitize", summary="Sanitize prompt removing dangerous injection patterns")
async def guard_sanitize(body: GuardSanitizeRequest):
    from app.ai.guard import sanitize
    cleaned = sanitize(body.prompt)
    return {
        "original": body.prompt,
        "sanitized": cleaned,
    }


@router.get("/benchmark/results", summary="Retrieve local offline inference benchmarks")
async def get_benchmark_results():
    from pathlib import Path
    bench_file = Path("benchmark_results.json")
    if bench_file.exists():
        try:
            with open(bench_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"status": "ok", "benchmark_results": data}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Error reading benchmark results: {exc}")
    return {"status": "pending", "message": "Benchmark results not yet generated. Run benchmark suite."}

