from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.models import ModelStatusResponse, SelectModelRequest
from backend.app.services.llm_service import llm_service

router = APIRouter(tags=["Models & Inference Runtime"])


@router.get(
    "/models",
    response_model=ModelStatusResponse,
    summary="Get Local Model Runtime & Available 1B-4B Models",
)
async def get_models():
    """
    Returns Ollama local runtime health, active 1B-4B quantized model,
    and detected available open-weight models without any cloud AI dependency.
    """
    status_data = await llm_service.get_status()
    return status_data


@router.get(
    "/models/active",
    summary="Get Current Active Model Name",
)
def get_active_model():
    """Returns the current model selected for industrial investigation queries."""
    return {
        "active_model": llm_service.active_model,
        "runtime": "ollama",
        "endpoint": llm_service.base_url,
    }


@router.post(
    "/models/select",
    summary="Switch Active Local Model",
)
def select_active_model(req: SelectModelRequest):
    """
    Dynamically select an active 1B-4B model (e.g. qwen2.5:3b, llama3.2:3b, phi3.5).
    """
    if not req.model_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model name must not be empty",
        )
    active = llm_service.set_active_model(req.model_name)
    return {
        "message": f"Active model set to '{active}'",
        "active_model": active,
    }
