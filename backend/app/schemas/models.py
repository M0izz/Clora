from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    name: str
    size_category: str = "1B-4B"
    parameter_size: Optional[str] = None
    quantization: Optional[str] = None
    modified_at: Optional[str] = None
    status: str = "available"  # available, loaded, offline_fallback


class ModelStatusResponse(BaseModel):
    runtime: str = "ollama"
    endpoint: str
    active_model: str
    is_online: bool
    hardware_mode: str = "LOCAL_AIR_GAPPED"
    available_models: List[ModelInfo] = Field(default_factory=list)
    fallback_active: bool = False


class SelectModelRequest(BaseModel):
    model_name: str
