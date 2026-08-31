"""
INDUSAI-X: Sovereign Local Embedding Benchmark Suite (SIH26117 / MRPL)
Evaluates local embedding candidates on CPU latency, memory footprint, and MRPL technical retrieval accuracy.
"""

import sys
import os
import time
import tracemalloc
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table

# Reconfigure stdout/stderr for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(legacy_windows=False)

# 10 Hand-crafted MRPL Technical Test Pairs (Representative synthetic industrial dataset)
MRPL_BENCHMARK_CORPUS = [
    {
        "chunk_id": "c_p101_bearing",
        "text": "Centrifugal Booster Pump P-101: Bearing temperature exceeded maximum operating threshold of 90°C, peaking at 95°C during high throughput mode.",
        "equipment": "P-101"
    },
    {
        "chunk_id": "c_p101_lube",
        "text": "Lube oil reservoir inspection for Pump P-101: Contamination observed with metallic debris and degraded viscosity index.",
        "equipment": "P-101"
    },
    {
        "chunk_id": "c_k201_surge",
        "text": "Wet Gas Compressor K-201: Anti-surge valve MOV-102 failed to modulate during sudden discharge pressure fluctuation.",
        "equipment": "K-201"
    },
    {
        "chunk_id": "c_hex301_fouling",
        "text": "Pre-heat Exchanger HEX-301: Heavy crude tube-side fouling caused 18% reduction in overall heat transfer coefficient.",
        "equipment": "HEX-301"
    },
    {
        "chunk_id": "c_tk502_vent",
        "text": "Naphtha Storage Tank TK-502: Pressure vacuum relief valve inspected and calibrated to 15 mbar overpressure limit.",
        "equipment": "TK-502"
    },
    {
        "chunk_id": "c_sop_startup",
        "text": "Standard Operating Procedure: Pre-commissioning line flush, nitrogen purging, and seal barrier fluid pressurization for centrifugal pumps.",
        "equipment": "General"
    },
    {
        "chunk_id": "c_vibe_sensor",
        "text": "Vibration monitoring protocol: Velocity RMS above 4.5 mm/s requires immediate shift supervisor notification and spectral analysis.",
        "equipment": "General"
    },
    {
        "chunk_id": "c_fcv204_calib",
        "text": "Flow Control Valve FCV-204: Positioner recalibration completed; stroke travel verified from 0% to 100% with zero deadband.",
        "equipment": "FCV-204"
    },
    {
        "chunk_id": "c_seal_flush",
        "text": "API Plan 53A seal flush reservoir: Buffer fluid level dropped below low-level alarm switch due to primary mechanical seal wear.",
        "equipment": "P-101"
    },
    {
        "chunk_id": "c_safety_h2s",
        "text": "Refinery Safety Protocol: H2S exposure limit threshold is 10 ppm TWA; respiratory protection mandatory upon alarm activation.",
        "equipment": "Safety"
    }
]

MRPL_EVAL_QUERIES = [
    {"query": "Why did Pump P-101 experience high bearing temperature?", "target_chunk": "c_p101_bearing"},
    {"query": "Lube oil particulate contamination in pump reservoir", "target_chunk": "c_p101_lube"},
    {"query": "Compressor K-201 anti surge valve failure", "target_chunk": "c_k201_surge"},
    {"query": "Heat transfer loss in pre heat exchanger HEX 301", "target_chunk": "c_hex301_fouling"},
    {"query": "Tank TK-502 pressure vacuum relief valve calibration", "target_chunk": "c_tk502_vent"},
    {"query": "Nitrogen purging and pre-commissioning pump steps", "target_chunk": "c_sop_startup"},
    {"query": "Vibration velocity RMS threshold limits for shift alert", "target_chunk": "c_vibe_sensor"},
    {"query": "FCV-204 valve positioner recalibration deadband", "target_chunk": "c_fcv204_calib"},
    {"query": "Plan 53A barrier fluid seal leakage", "target_chunk": "c_seal_flush"},
    {"query": "H2S gas ppm safety limits and alarm response", "target_chunk": "c_safety_h2s"}
]

def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(b * b for b in v2) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def benchmark_candidate(candidate_name: str, embedder) -> Dict[str, Any]:
    console.print(f"[cyan]Evaluating candidate: [bold]{candidate_name}[/bold]...[/cyan]")
    
    texts = [item["text"] for item in MRPL_BENCHMARK_CORPUS]
    chunk_ids = [item["chunk_id"] for item in MRPL_BENCHMARK_CORPUS]

    # 1. Batch Embedding Throughput & Memory
    tracemalloc.start()
    t0 = time.perf_counter()
    doc_embeddings = embedder.embed_documents(texts)
    doc_time = time.perf_counter() - t0
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    throughput = len(texts) / max(0.0001, doc_time)
    mem_mb = peak_mem / (1024 * 1024)

    # 2. Query Latency and Retrieval Accuracy (Recall@1 and Recall@3)
    query_latencies = []
    hits_at_1 = 0
    hits_at_3 = 0

    for q_item in MRPL_EVAL_QUERIES:
        q_text = q_item["query"]
        target = q_item["target_chunk"]

        t_q = time.perf_counter()
        q_vec = embedder.embed_query(q_text)
        query_latencies.append((time.perf_counter() - t_q) * 1000.0)

        # Score all docs
        scores = []
        for cid, d_vec in zip(chunk_ids, doc_embeddings):
            sim = cosine_similarity(q_vec, d_vec)
            scores.append((sim, cid))

        scores.sort(key=lambda x: x[0], reverse=True)
        top_1 = scores[0][1] if scores else None
        top_3 = [s[1] for s in scores[:3]]

        if top_1 == target:
            hits_at_1 += 1
        if target in top_3:
            hits_at_3 += 1

    avg_query_latency = sum(query_latencies) / len(query_latencies)
    dim = embedder.embedding_dimension

    return {
        "candidate": candidate_name,
        "dimension": dim,
        "avg_query_latency_ms": round(avg_query_latency, 2),
        "batch_throughput_chunks_sec": round(throughput, 1),
        "recall_at_1": round(hits_at_1 / len(MRPL_EVAL_QUERIES), 2),
        "recall_at_3": round(hits_at_3 / len(MRPL_EVAL_QUERIES), 2),
        "memory_overhead_mb": round(mem_mb, 2)
    }

def run_benchmark():
    console.print("\n[bold white]========================================================================[/bold white]")
    console.print("[bold cyan] INDUSAI-X Sovereign Local Embedding Model Benchmark (MRPL SIH26117) [/bold cyan]")
    console.print("[bold white]========================================================================[/bold white]\n")

    from indusai.embeddings.local_embedding import LocalSentenceTransformerEmbedding, EmbeddingService
    from indusai.embeddings.ollama_embedding import OllamaEmbeddingService

    candidates = [
        ("all-MiniLM-L6-v2 (Local PyTorch / ST)", LocalSentenceTransformerEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")),
        ("bge-small-en-v1.5 (Local PyTorch / ST)", LocalSentenceTransformerEmbedding(model_name="BAAI/bge-small-en-v1.5")),
        ("nomic-embed-text (Ollama / Local)", OllamaEmbeddingService(model_name="nomic-embed-text"))
    ]

    results = []
    for name, embedder in candidates:
        res = benchmark_candidate(name, embedder)
        results.append(res)

    # Render results table
    table = Table(title="Local Embedding Model Benchmark Results (10-pair MRPL Technical Eval Set)")
    table.add_column("Candidate Model", style="cyan")
    table.add_column("Dimensions", justify="center")
    table.add_column("Query Latency", justify="right", style="yellow")
    table.add_column("Throughput", justify="right")
    table.add_column("Recall@1", justify="center", style="green")
    table.add_column("Recall@3", justify="center", style="bold green")
    table.add_column("Memory Incr", justify="right")

    for r in results:
        table.add_row(
            r["candidate"],
            str(r["dimension"]),
            f"{r['avg_query_latency_ms']} ms",
            f"{r['batch_throughput_chunks_sec']} chunks/s",
            f"{int(r['recall_at_1'] * 100)}%",
            f"{int(r['recall_at_3'] * 100)}%",
            f"{r['memory_overhead_mb']} MB"
        )

    console.print()
    console.print(table)
    console.print("\n[bold green][OK] Embedding Benchmark complete! Data ready for Phase 5 technical defense.[/bold green]\n")

if __name__ == "__main__":
    run_benchmark()
