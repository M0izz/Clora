"""
Unit tests for Local Embedding Service.
"""

from backend.rag.embeddings import LocalEmbeddingService


def test_local_embedding_dimensions_and_batch():
    embedder = LocalEmbeddingService()
    docs = ["First industrial document.", "Second equipment report."]
    embeddings = embedder.embed_documents(docs)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == embedder.embedding_dimension

    q_vec = embedder.embed_query("Query test")
    assert len(q_vec) == embedder.embedding_dimension
