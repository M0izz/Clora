"""
Unit tests for RAGAgent.
"""

import shutil
import tempfile

from backend.agents.rag_agent import RAGAgent
from backend.rag.chroma_store import ChromaEvidenceStore
from backend.rag.embeddings import LocalEmbeddingService


def test_rag_agent_retrieval_and_role_filtering():
    temp_dir = tempfile.mkdtemp()
    try:
        store = ChromaEvidenceStore(collection_name="test_rag_agent", persist_path=temp_dir)
        embedder = LocalEmbeddingService()
        agent = RAGAgent(store=store, embedder=embedder)

        # Ingest docs
        doc1 = "Pump P-101 bearing temperature exceeded 95C during high throughput."
        meta1 = {
            "chunk_id": "c1",
            "document_name": "Pump_P101_Report.pdf",
            "page": 14,
            "equipment_id": "P-101",
            "allowed_roles": "maintenance_engineer,supervisor",
        }
        emb1 = embedder.embed_documents([doc1])
        store.add(ids=["c1"], documents=[doc1], embeddings=emb1, metadatas=[meta1])

        # 1. Query as maintenance_engineer
        res_eng = agent.retrieve("Why did Pump P-101 fail?", user_role="maintenance_engineer")
        assert len(res_eng) > 0
        assert res_eng[0].source_document == "Pump_P101_Report.pdf"

        # 2. Query as guest (blocked)
        res_guest = agent.retrieve("Why did Pump P-101 fail?", user_role="guest")
        assert len(res_guest) == 0

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
