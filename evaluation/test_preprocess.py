# test_preprocess.py

from preprocess_fpl import (
    build_lexicon_from_neo4j,
    load_embedder,
    preprocess_input,
)

def main():
    # 1) Build the lexicon (reads from your Neo4j KG)
    print("Building lexicon from Neo4j...")
    lexicon = build_lexicon_from_neo4j("config.txt")
    print(f"- Loaded {len(lexicon.players)} players")
    print(f"- Loaded {len(lexicon.teams)} teams")
    print(f"- Loaded {len(lexicon.positions)} positions")
    print(f"- Loaded {len(lexicon.seasons)} seasons")

    # 2) Load the MiniLM embedder
    print("\nLoading MiniLM embedder...")
    embedder = load_embedder()
    print("- Embedder loaded.")

    # 3) Test some example queries
    queries = [
        "Top 5 FWDs in 2022-23 by total points",
        "How many goals did Mohamed Salah score in 2021-22?",
        "Compare Haaland and Kane in 2022-23 total points",
        "Who got the most yellow cards in 2022-23?",
        "Which Liverpool players had the most goals in 2021-22?",
    ]

    for q in queries:
        print("\n" + "=" * 80)
        print("Query:", q)
        result = preprocess_input(q, lexicon, embedder)

        print("Intent:", result["intent"])
        print("Entities:", result["entities"])
        print("Embedding shape:", result["embedding"].shape)

if __name__ == "__main__":
    main()
