"""
RAG Agent Node for INDUSAI-X.
Retrieves authorized industrial documents with strict permission filtering and reranking.
"""

import re
from typing import Dict, Any, List
from indusai.agents.state import AgentState
from indusai.storage.vector_store import ChromaVectorStore
from indusai.retrieval.reranker import IndustrialReranker
from indusai.retrieval.evidence_pack import EvidencePackBuilder

EQUIPMENT_ID_REGEX = re.compile(r'\b(?:P|K|E|T|TK|V|C|R|HEX|MOV|FCV|PT|TT|LT|FT|D)-\d{2,4}[A-Z]?\b', re.IGNORECASE)

class RAGAgent:
    def __init__(self, vector_store: ChromaVectorStore, reranker: IndustrialReranker):
        self.vector_store = vector_store
        self.reranker = reranker

    def run(self, state: AgentState) -> Dict[str, Any]:
        query = state.get("user_query", "")
        user_role = state.get("user_role", "guest")
        
        eq_matches = EQUIPMENT_ID_REGEX.findall(query)
        equipment_id = eq_matches[0].upper() if eq_matches else None

        # 1. First retrieval attempt
        raw_chunks = self.vector_store.query(
            query_text=query,
            user_role=user_role,
            equipment_id=equipment_id,
            top_k=5
        )

        re_retrieval_performed = False
        expanded_query_used = ""
        expansions_list = []

        # 2. Self-healing Re-retrieval Loop (Hard capped at exactly 1 retry)
        if not raw_chunks:
            re_retrieval_performed = True
            from indusai.retrieval.query_expander import IndustrialQueryExpander
            expanded_query_used, expansions_list = IndustrialQueryExpander.expand_query(query)
            
            # Retry retrieval with expanded query and relaxed equipment constraint
            raw_chunks = self.vector_store.query(
                query_text=expanded_query_used,
                user_role=user_role,
                top_k=5
            )

        # 3. Domain-aware reranking
        active_query = expanded_query_used if re_retrieval_performed and expanded_query_used else query
        reranked_chunks = self.reranker.rerank(active_query, raw_chunks)

        # 4. Build Evidence Pack
        evidence_pack = EvidencePackBuilder.build(reranked_chunks)
        evidence_list = [item.to_dict() for item in evidence_pack.evidence]

        audit_entry = {
            "event": "rag_retrieval_completed",
            "user_role": user_role,
            "equipment_id": equipment_id,
            "re_retrieval_attempted": re_retrieval_performed,
            "query_expansions": expansions_list,
            "retrieved_count": len(reranked_chunks),
            "retrieved_sources": [f"{item['source']}:p.{item['page']}" for item in evidence_list]
        }

        audit_log = list(state.get("audit_log", []))
        audit_log.append(audit_entry)

        agent_outputs = dict(state.get("agent_outputs", {}))
        agent_outputs["rag_agent"] = {
            "chunks_retrieved": len(reranked_chunks),
            "re_retrieval_performed": re_retrieval_performed,
            "sources": list(set(item["source"] for item in evidence_list))
        }

        return {
            "retrieved_docs": reranked_chunks,
            "evidence": evidence_list,
            "agent_outputs": agent_outputs,
            "audit_log": audit_log
        }
