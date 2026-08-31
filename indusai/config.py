"""
INDUSAI-X: Sovereign On-Premise Agentic AI Workbench (SIH26117 / MRPL)
Core Configuration Module
"""

import os
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Settings(BaseModel):
    # System identification
    APP_NAME: str = "INDUSAI-X"
    ORGANIZATION: str = "MRPL"
    PROJECT_ID: str = "SIH26117"
    VERSION: str = "1.0.0"

    # Local Inference & Embedding Settings (No external cloud calls)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL: str = os.getenv("OLLAMA_LLM_MODEL", "qwen2.5:7b-instruct")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    LOCAL_EMBEDDING_MODEL: str = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Vector Database (ChromaDB)
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db_indusai")
    COLLECTION_NAME: str = "mrpl_industrial_knowledge"

    # Role Hierarchy & RBAC
    VALID_ROLES: List[str] = [
        "plant_manager",
        "shift_supervisor",
        "supervisor",
        "maintenance_engineer",
        "safety_officer",
        "reliability_engineer",
        "operator",
        "technician",
        "auditor",
        "guest"
    ]

    # Verification & Hallucination Firewall Thresholds
    SUPPORTED_THRESHOLD: float = 0.85
    PARTIALLY_SUPPORTED_THRESHOLD: float = 0.60
    MAX_RETRIEVAL_TOP_K: int = 5
    RERANK_TOP_K: int = 3

    # Causal leap guard keywords
    CAUSAL_CONNECTIVES: List[str] = [
        "caused", "causing", "because of", "due to", "led to", "leading to",
        "resulted in", "resulting in", "triggered", "triggering", "brought about",
        "consequently", "as a direct result of"
    ]

settings = Settings()
