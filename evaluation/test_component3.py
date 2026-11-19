# test_component3.py

from preprocess_fpl import (
    build_lexicon_from_neo4j,
    load_embedder,
    preprocess_input,
)
from retrieval_fpl import (
    get_driver,
    baseline_retrieve,
    embedding_retrieve_players_minilm,
)
from answer_generator import generate_answer


# -------------------------
# Groq models (Component 3)
# -------------------------
CONFIG = {
    "models": [
        {"name": "llama", "model": "llama-3.3-70b-versatile"},
        {"name": "qwen", "model": "qwen/qwen3-32b"},
        {"name": "gpt-oss", "model": "openai/gpt-oss-120b"},
    ]
}


def main():
    # ---------- Component 1 ----------
    print("Building lexicon...")
    lexicon = build_lexicon_from_neo4j("config.txt")

    print("Loading embedder...")
    embedder = load_embedder()

    # ---------- Component 2 ----------
    print("Connecting to Neo4j...")
    driver = get_driver("config.txt")

    # SAME queries from test_retrieval_extended.py
    queries = [
    # ---------- PLAYER SEASON STATS ----------

    "How many points did trippier Get in season 2022-23?",
]

    print("\n==================== COMPONENT 3 TEST ====================\n")

    for q in queries:
        print("=" * 80)
        print("USER QUESTION:", q)

        # ---------- Component 1 ----------
        pre = preprocess_input(q, lexicon, embedder)
        print("Intent:", pre["intent"])
        print("Entities:", pre["entities"])

        # ---------- Component 2 ----------
        baseline = baseline_retrieve(driver, pre)
        embeddings = embedding_retrieve_players_minilm(
            driver, pre["embedding"], k=5
        )

        print("\nBaseline results:")
        for row in baseline[:5]:
            print(row)

        print("\nEmbedding results:")
        for row in embeddings[:5]:
            print(row)

        # ---------- Component 3 ----------
        retrieval_context = {
            "baseline": baseline,
            "embeddings": embeddings
        }

        out = generate_answer(pre, retrieval_context, CONFIG)

        print("\nFINAL ANSWER (Component 3):")
        print(out["final_answer"])

        print("\nModel comparison:")
        for m, r in out["model_responses"].items():
            print(f"- {m}: latency={r['latency']:.2f}s, len={len(r['answer'])}")

        print("\n" + "=" * 80 + "\n")

    driver.close()


if __name__ == "__main__":
    main()