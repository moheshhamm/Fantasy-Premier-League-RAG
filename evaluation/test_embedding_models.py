# test_embedding_models.py

from preprocess_fpl import (
    build_lexicon_from_neo4j,
    load_embedder,
    preprocess_input,
)
from retrieval_fpl import (
    get_driver,
    baseline_retrieve,
    embedding_retrieve_players_minilm,
    embedding_retrieve_players_mpnet,
)
from sentence_transformers import SentenceTransformer


def main():
    # 1) Component 1 setup
    print("Building lexicon...")
    lexicon = build_lexicon_from_neo4j("config.txt")

    print("Loading MiniLM (query) embedder for Component 1...")
    embedder_minilm_query = load_embedder()
    print("- MiniLM loaded.\n")

    # 2) Second model for query embedding: MPNet
    print("Loading MPNet (query) embedder...")
    embedder_mpnet_query = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    print("- MPNet loaded.\n")

    # 3) Neo4j driver
    driver = get_driver("config.txt")

    # 4) Some semantic queries
    queries = [
        "Which forwards are good goal scorers?",
        "Best players for clean sheets",
        "Who are the most attacking defenders?",
    ]

    for q in queries:
        print("=" * 80)
        print("User query:", q)

        # Use Component 1 to get intent + entities + MiniLM embedding
        pre = preprocess_input(q, lexicon, embedder_minilm_query)
        print("Intent:", pre["intent"])
        print("Entities:", pre["entities"])

        # Baseline retrieval (may be empty or generic for vague queries)
        print("\nBaseline retrieval:")
        rows_baseline = baseline_retrieve(driver, pre)
        for row in rows_baseline[:5]:
            print(row)
        if not rows_baseline:
            print("(No baseline result)")

        # Embedding-based retrieval with MiniLM
        print("\nEmbedding-based retrieval (MiniLM) – top 5 players:")
        rows_minilm = embedding_retrieve_players_minilm(driver, pre["embedding"], k=5)
        for row in rows_minilm:
            print(row)

        # Embedding-based retrieval with MPNet
        print("\nEmbedding-based retrieval (MPNet) – top 5 players:")
        # Get MPNet embedding of the same query text
        emb_mpnet_query = embedder_mpnet_query.encode([q], convert_to_numpy=True)[0]
        rows_mpnet = embedding_retrieve_players_mpnet(driver, emb_mpnet_query, k=5)
        for row in rows_mpnet:
            print(row)

        print()

    driver.close()


if __name__ == "__main__":
    main()
