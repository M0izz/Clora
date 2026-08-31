"""
app.ai — INDUSAI-X local inference engine.
"""
from app.ai.models import (
    ModelConfig,
    REGISTERED_MODELS,
    DEFAULT_MODEL,
    FALLBACK_MODEL,
    UnsupportedModelError,
    resolve_model,
    list_models,
)
from app.ai.inference import OllamaClient, InferenceService, UnsafePromptError
from app.ai.prompts import build_system_prompt, list_tasks
from app.ai.guard import scan_prompt, sanitize, is_safe, PromptThreatLevel
from app.ai.langchain_adapter import get_chat_model, get_reasoning_model, get_json_model, bind_tools

__all__ = [
    "ModelConfig",
    "REGISTERED_MODELS",
    "DEFAULT_MODEL",
    "FALLBACK_MODEL",
    "UnsupportedModelError",
    "resolve_model",
    "list_models",
    "OllamaClient",
    "InferenceService",
    "UnsafePromptError",
    "build_system_prompt",
    "list_tasks",
    "scan_prompt",
    "sanitize",
    "is_safe",
    "PromptThreatLevel",
    "get_chat_model",
    "get_reasoning_model",
    "get_json_model",
    "bind_tools",
]
