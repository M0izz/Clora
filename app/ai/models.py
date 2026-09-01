"""
Model registry and configuration for INDUSAI-X local inference.
Owns: which models are allowed, which is default, safe switching.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ModelConfig:
    name: str          # exact Ollama model tag
    label: str          # human-readable name for UI
    context_window: int # approx max tokens it handles well
    is_default: bool = False
    is_fallback: bool = False


# --- Registry: edit this list after you finish benchmarking (Step 7) ---
REGISTERED_MODELS = [
    ModelConfig(name="llama3.2:3b", label="Llama 3.2 3B", context_window=8192, is_default=True),
    ModelConfig(name="phi3:mini", label="Phi-3 Mini", context_window=4096, is_fallback=True),
    ModelConfig(name="qwen2.5:3b", label="Qwen 2.5 3B", context_window=8192),
    ModelConfig(name="moondream", label="Moondream (Vision)", context_window=2048),
]

_REGISTRY = {m.name: m for m in REGISTERED_MODELS}

DEFAULT_MODEL = os.getenv("INDUSAI_DEFAULT_MODEL") or next(
    (m.name for m in REGISTERED_MODELS if m.is_default), REGISTERED_MODELS[0].name
)
FALLBACK_MODEL = os.getenv("INDUSAI_FALLBACK_MODEL") or next(
    (m.name for m in REGISTERED_MODELS if m.is_fallback), None
)


class UnsupportedModelError(Exception):
    pass


ALIASES = {
    "llama3.2": "llama3.2:3b",
    "llama3": "llama3.2:3b",
    "llama": "llama3.2:3b",
    "phi3": "phi3:mini",
    "phi": "phi3:mini",
    "qwen2.5": "qwen2.5:3b",
    "qwen": "qwen2.5:3b",
    "vision": "moondream",
}


def resolve_model(requested: Optional[str]) -> str:
    """Validate a requested model name, or return the default. Never raises to caller crash —
    callers should catch UnsupportedModelError and return a clean 400, not a 500."""
    if requested is None:
        return DEFAULT_MODEL
    
    canonical = ALIASES.get(requested.lower().strip(), requested)
    if canonical not in _REGISTRY:
        raise UnsupportedModelError(
            f"Model '{requested}' is not registered. Available: {list(_REGISTRY.keys())}"
        )
    return canonical



def list_models() -> list[dict]:
    """For the frontend model-switch dropdown."""
    return [
        {"name": m.name, "label": m.label, "is_default": m.is_default, "is_fallback": m.is_fallback}
        for m in REGISTERED_MODELS
    ]
