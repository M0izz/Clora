"""
LangChain / LangGraph adapter for INDUSAI-X.
Owns: supplying pre-configured ChatOllama instances to Member 5 (Agents/RAG).

Usage by Member 5:
    from app.ai.langchain_adapter import get_chat_model, get_reasoning_model

    llm = get_chat_model()                       # default model
    llm = get_reasoning_model()                   # best reasoning model
    llm = get_chat_model("qwen2.5:3b")           # specific model
    llm_with_tools = bind_tools(llm, [my_tool])   # tool-calling ready
"""
from __future__ import annotations

import logging
from typing import Any, Sequence

from langchain_ollama import ChatOllama
from langchain_core.tools import BaseTool

from app.ai.models import DEFAULT_MODEL, FALLBACK_MODEL, resolve_model, _REGISTRY
from app.config import settings

logger = logging.getLogger("indusai.langchain")


# ---------------------------------------------------------------------------
# Model factories
# ---------------------------------------------------------------------------

def get_chat_model(
    model: str | None = None,
    temperature: float = 0.3,
    num_predict: int | None = None,
    format: str | None = None,
    **kwargs: Any,
) -> ChatOllama:
    """
    Return a ready-to-use ChatOllama instance for LangGraph agents.

    Args:
        model:       Ollama model tag. Uses DEFAULT_MODEL if None.
        temperature: Sampling temperature (lower = more deterministic).
        num_predict: Max tokens to generate. Uses settings default if None.
        format:      Set to "json" to force JSON-only output.
        **kwargs:    Passed through to ChatOllama (e.g., top_p, repeat_penalty).
    """
    model = resolve_model(model)
    config = _REGISTRY.get(model)

    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=model,
        temperature=temperature,
        num_predict=num_predict or settings.max_tokens,
        format=format or "",
        **kwargs,
    )


def get_reasoning_model(**kwargs: Any) -> ChatOllama:
    """Return the best available reasoning model (qwen2.5:3b > llama3.2:3b > fallback)."""
    # Prefer qwen2.5 for reasoning/tool-calling, fall back through registry
    for candidate in ["qwen2.5:3b", DEFAULT_MODEL, FALLBACK_MODEL]:
        if candidate and candidate in _REGISTRY:
            logger.info("Reasoning model selected: %s", candidate)
            return get_chat_model(model=candidate, temperature=0.1, **kwargs)

    # Absolute fallback
    return get_chat_model(temperature=0.1, **kwargs)


def get_json_model(model: str | None = None, **kwargs: Any) -> ChatOllama:
    """Return a model configured to output ONLY valid JSON."""
    return get_chat_model(model=model, temperature=0.0, format="json", **kwargs)


# ---------------------------------------------------------------------------
# Tool binding helper
# ---------------------------------------------------------------------------

def bind_tools(
    llm: ChatOllama,
    tools: Sequence[BaseTool | dict] | None = None,
) -> ChatOllama:
    """
    Bind tool-calling schemas to a ChatOllama instance.
    Member 5 passes their LangGraph tools here; we handle the binding.

    Args:
        llm:   A ChatOllama instance from get_chat_model().
        tools: List of LangChain BaseTool instances or raw OpenAI-style tool dicts (defaults to TOOL_SCHEMAS).

    Returns:
        A new ChatOllama with tools bound (use .invoke() as normal).
    """
    if tools is None:
        tools = list(TOOL_SCHEMAS.values())
    return llm.bind_tools(tools)



# ---------------------------------------------------------------------------
# Pre-built tool schemas (for common INDUSAI-X operations)
# ---------------------------------------------------------------------------

# These are OpenAI-compatible function schemas that Member 5 can use directly
# in LangGraph tool nodes. Add more as the agent workflows are defined.

TOOL_SCHEMAS: dict[str, dict] = {
    "classify_document": {
        "type": "function",
        "function": {
            "name": "classify_document",
            "description": "Classify a government document into a category",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "complaint", "inquiry", "application", "report",
                            "notification", "circular", "order", "other",
                        ],
                        "description": "The document category",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score between 0.0 and 1.0",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief reason for the classification",
                    },
                },
                "required": ["category", "confidence", "reason"],
            },
        },
    },
    "extract_entities": {
        "type": "function",
        "function": {
            "name": "extract_entities",
            "description": "Extract structured entities from a government document",
            "parameters": {
                "type": "object",
                "properties": {
                    "names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Person or organization names mentioned",
                    },
                    "dates": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Dates mentioned (ISO format preferred)",
                    },
                    "reference_numbers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File numbers, order numbers, section references",
                    },
                    "amounts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Monetary amounts or quantities mentioned",
                    },
                },
                "required": ["names", "dates", "reference_numbers"],
            },
        },
    },
    "route_query": {
        "type": "function",
        "function": {
            "name": "route_query",
            "description": "Decide which department or workflow should handle a citizen query",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": "Target department name",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Priority level for the query",
                    },
                    "action": {
                        "type": "string",
                        "description": "Recommended next action",
                    },
                },
                "required": ["department", "priority", "action"],
            },
        },
    },
}


def get_tool_schema(name: str) -> dict | None:
    """Retrieve a pre-built tool schema by name."""
    return TOOL_SCHEMAS.get(name)


def list_tool_schemas() -> list[str]:
    """List all available pre-built tool schema names."""
    return list(TOOL_SCHEMAS.keys())


TOOL_DEFINITIONS = TOOL_SCHEMAS

