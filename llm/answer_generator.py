"""
Component 3 — LLM Answer Generator (Groq-based, Graph-RAG)

This component:
- Consumes retrieval results from Component 2
- Merges baseline + embedding retrieval
- Builds a structured prompt (persona, context, task)
- Compares ≥ 3 LLMs using Groq
- Returns quantitative + qualitative-ready outputs
"""

from dotenv import load_dotenv
load_dotenv()

import os
import time
from typing import Dict, Any, List
from groq import Groq

# ------------------------------------------------------------------
# Groq client
# ------------------------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

NON_ANSWER = "I don't know based on the provided KG data."

# ------------------------------------------------------------------
# Helper: merge baseline + embedding retrieval
# ------------------------------------------------------------------
def merge_retrievals(
    baseline_rows: List[Dict[str, Any]],
    embedding_rows: List[Dict[str, Any]],
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Merge baseline (Cypher) and embedding retrieval results.
    Baseline results have priority.
    Remove duplicates.
    """

    merged = {}

    for r in baseline_rows or []:
        merged[str(r)] = {"source": "baseline", "data": r}

    for r in embedding_rows or []:
        key = str(r)
        if key not in merged:
            merged[key] = {"source": "embedding", "data": r}

    return list(merged.values())[:top_k]

# ------------------------------------------------------------------
# Helper: convert KG rows to readable context
# ------------------------------------------------------------------
def build_context_text(merged_results: List[Dict[str, Any]]) -> str:
    if not merged_results:
        return "No Knowledge Graph information was retrieved."

    lines = []
    for item in merged_results:
        src = item["source"].upper()
        data = item["data"]
        parts = [f"[{src}]"]
        for k, v in data.items():
            parts.append(f"{k}: {v}")
        lines.append(" | ".join(parts))

    return "\n".join(lines)

# ------------------------------------------------------------------
# Helper: build structured prompt
# ------------------------------------------------------------------
def build_prompt(
    preprocessed: Dict[str, Any],
    merged_results: List[Dict[str, Any]]
) -> str:
    persona = (
        "You are an expert Fantasy Premier League (FPL) analyst. "
        "You must answer strictly using the provided Knowledge Graph context. "
        "Do NOT use external knowledge. Do NOT hallucinate."
    )

    task = (
        "Answer the user's question using ONLY the information in the context.\n\n"
        "You ARE allowed to:\n"
        "- Rank results\n"
        "- Compare players or teams\n"
        "- Select top-k results\n"
        "- Summarize structured data\n"
        "- Rephrase numeric values into natural language\n\n"
        "You are NOT allowed to:\n"
        "- Use external football knowledge\n"
        "- Invent players, teams, or statistics\n"
        "- Go beyond the provided context\n\n"
        "If the context does not contain enough information to answer, "
        "reply EXACTLY with:\n"
        "\"I don't know based on the provided KG data.\""
    )

    context = build_context_text(merged_results)
    question = preprocessed.get("text", "")
    intent = preprocessed.get("intent", "UNKNOWN")
    entities = preprocessed.get("entities", {})

    return f"""
PERSONA:
{persona}

INTENT:
{intent}

ENTITIES:
{entities}

CONTEXT:
{context}

TASK:
{task}

USER QUESTION:
{question}
""".strip()

# ------------------------------------------------------------------
# Helper: call Groq model
# ------------------------------------------------------------------
def call_groq_model(prompt: str, model_name: str) -> Dict[str, Any]:
    start = time.time()

    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    latency = time.time() - start
    answer = completion.choices[0].message.content.strip()

    return {
        "answer": answer,
        "latency": latency,
        "metrics": {
            "answer_len": len(answer)
        }
    }

# ------------------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------------------
def generate_answer(
    preprocessed: Dict[str, Any],
    retrieval_context: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:

    baseline = retrieval_context.get("baseline", [])
    embeddings = retrieval_context.get("embeddings", [])

    merged_results = merge_retrievals(baseline, embeddings)
    prompt = build_prompt(preprocessed, merged_results)

    model_responses = {}

    for m in config["models"]:
        try:
            model_responses[m["name"]] = call_groq_model(prompt, m["model"])
        except Exception as e:
            model_responses[m["name"]] = {
                "answer": f"[ERROR] {e}",
                "latency": None,
                "metrics": {"answer_len": 0}
            }

    # ------------------------------
    # FINAL ANSWER SELECTION (FIXED)
    # ------------------------------
    valid = [
        r for r in model_responses.values()
        if r["latency"] is not None
    ]

    informative = [
        r for r in valid
        if r["answer"].strip() != NON_ANSWER
    ]

    if informative:
        # Choose shortest informative answer
        final_answer = min(
            informative, key=lambda x: x["metrics"]["answer_len"]
        )["answer"]
    else:
        final_answer = NON_ANSWER

    return {
        "merged_count": len(merged_results),
        "model_responses": model_responses,
        "final_answer": final_answer,
        "diagnostics": {
            "used_models": list(model_responses.keys())
        }
    }