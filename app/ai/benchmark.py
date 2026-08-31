"""
Benchmark local Ollama models — latency, throughput, availability.
Run:  python -m app.ai.benchmark
"""
from __future__ import annotations

import asyncio
import json
import sys
import time

import httpx

from app.ai.models import REGISTERED_MODELS
from app.config import settings

# --- Test prompts (short, medium, long) -----------------------------------

PROMPTS = {
    "short": "What is the capital of India?",
    "medium": (
        "Summarize the key provisions of the Digital Personal Data Protection "
        "Act 2023 of India in 5 bullet points."
    ),
    "long": (
        "You are a policy analyst. Compare and contrast the Indian IT Act 2000 "
        "with the Digital Personal Data Protection Act 2023. Cover: scope, "
        "penalties, consent framework, cross-border data transfer rules, and "
        "the role of the Data Protection Board. Provide a structured analysis."
    ),
}


async def _check_available(client: httpx.AsyncClient) -> list[str]:
    """Return model names that are actually pulled in Ollama."""
    try:
        r = await client.get("/api/tags")
        r.raise_for_status()
        local = {m["name"] for m in r.json().get("models", [])}
    except Exception:
        print("[!] Could not reach Ollama. Is it running?")
        sys.exit(1)

    available = []
    for m in REGISTERED_MODELS:
        # Ollama tags may include :latest suffix
        if m.name in local or any(n.startswith(m.name) for n in local):
            available.append(m.name)
        else:
            print(f"  [skip] {m.name} - not pulled locally")
    return available


async def _bench_one(
    client: httpx.AsyncClient,
    model: str,
    prompt_label: str,
    prompt: str,
) -> dict:
    """Run a single benchmark call and collect metrics."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 512},
    }

    t0 = time.perf_counter()
    try:
        r = await client.post("/api/generate", json=payload, timeout=180.0)
        r.raise_for_status()
    except Exception as exc:
        return {
            "model": model,
            "prompt": prompt_label,
            "error": str(exc),
        }
    elapsed = time.perf_counter() - t0

    body = r.json()
    eval_count = body.get("eval_count", 0)
    eval_duration_ns = body.get("eval_duration", 1)  # nanoseconds
    prompt_eval_ns = body.get("prompt_eval_duration", 0)

    tokens_per_sec = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns else 0
    ttft = prompt_eval_ns / 1e9  # time-to-first-token (prompt eval phase)

    return {
        "model": model,
        "prompt": prompt_label,
        "total_latency_s": round(elapsed, 3),
        "ttft_s": round(ttft, 3),
        "tokens_generated": eval_count,
        "tokens_per_sec": round(tokens_per_sec, 1),
    }


async def run_benchmark() -> list[dict]:
    print("=" * 60)
    print("  INDUSAI-X  Model Benchmark")
    print("=" * 60)
    print(f"  Ollama URL: {settings.ollama_base_url}")
    print()

    async with httpx.AsyncClient(base_url=settings.ollama_base_url) as client:
        available = await _check_available(client)
        if not available:
            print("[!] No registered models found in Ollama. Pull at least one.")
            return []

        print(f"\n  Models to benchmark: {available}\n")
        results: list[dict] = []

        for model in available:
            for label, prompt in PROMPTS.items():
                print(f"  > {model}  |  {label:6s}  ... ", end="", flush=True)
                result = await _bench_one(client, model, label, prompt)
                results.append(result)

                if "error" in result:
                    print(f"ERROR: {result['error'][:60]}")
                else:
                    print(
                        f"{result['tokens_per_sec']:6.1f} tok/s  "
                        f"| {result['tokens_generated']:4d} tokens  "
                        f"| {result['total_latency_s']:6.2f}s total  "
                        f"| TTFT {result['ttft_s']:.2f}s"
                    )

    # --- Summary ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Results saved to benchmark_results.json")
    print("=" * 60)

    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    asyncio.run(run_benchmark())
