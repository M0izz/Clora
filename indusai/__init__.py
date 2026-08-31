"""
INDUSAI-X: Sovereign On-Premise Agentic AI Workbench for MRPL (SIH26117)
Intelligence Backbone Package.
"""

from indusai.config import settings
from indusai.agents.graph import IndusAIGraph
from indusai.storage.vector_store import ChromaVectorStore
from indusai.ingestion.schema import ChunkMetadata, Chunk, IngestedDocument
from indusai.ingestion.chunker import IntelligentChunker
from indusai.ingestion.document_parser import DocumentParser
from indusai.verification.verifier import EvidenceVerifier
from indusai.evaluation.metrics import Evaluator

__version__ = "1.0.0"
__all__ = [
    "settings",
    "IndusAIGraph",
    "ChromaVectorStore",
    "ChunkMetadata",
    "Chunk",
    "IngestedDocument",
    "IntelligentChunker",
    "DocumentParser",
    "EvidenceVerifier",
    "Evaluator"
]
