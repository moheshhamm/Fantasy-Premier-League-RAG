# embed_players.py

from typing import Dict, Any, List
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np

from preprocess_fpl import load_config  # reuse your existing config loader


def get_driver(config_path: str = "config.txt"):
    config = load_config(config_path)
    uri = config["URI"]
    user = config["USERNAME"]
    password = config["PASSWORD"]
    return GraphDatabase.driver(uri, auth=(user, password))


def fetch_players_with_positions(tx) -> List[Dict[str, Any]]:
    """
    Return list of dicts: {player_name, position}
    """
    cypher = """
    MATCH (p:Player)-[:PLAYS_AS]->(pos:Position)
    RETURN p.player_name AS player_name, pos.name AS position
    ORDER BY player_name
    """
    result = tx.run(cypher)
    return [record.data() for record in result]


def write_player_embeddings(
    tx,
    player_name: str,
    emb_minilm: List[float],
    emb_mpnet: List[float],
):
    """
    Store both embeddings on the Player node.
    """
    cypher = """
    MATCH (p:Player {player_name: $player_name})
    SET p.embedding_minilm = $embedding_minilm,
        p.embedding_mpnet = $embedding_mpnet
    """
    tx.run(
        cypher,
        player_name=player_name,
        embedding_minilm=emb_minilm,
        embedding_mpnet=emb_mpnet,
    )


def main():
    # 1) Connect to Neo4j
    driver = get_driver("config.txt")

    # 2) Load both embedding models
    print("Loading MiniLM embedder...")
    embedder_minilm = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("MiniLM loaded.")

    print("Loading MPNet embedder...")
    embedder_mpnet = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    print("MPNet loaded.\n")

    with driver.session() as session:
        # 3) Fetch all players and their positions
        print("Fetching players and positions from Neo4j...")
        players = session.execute_read(fetch_players_with_positions)
        print(f"- Found {len(players)} players with positions.\n")

        # 4) For each player, build a text description and embed it with BOTH models
        for idx, row in enumerate(players, start=1):
            name = row["player_name"]
            position = row["position"]  # e.g., "FWD", "MID", "DEF", "GK"

            # Simple text description (you can expand this later with stats if you like)
            text = f"{name}, {position}, FPL player in the Premier League."

            # MiniLM embedding (384-dim)
            vec_minilm = embedder_minilm.encode([text], convert_to_numpy=True)[0]
            emb_minilm = vec_minilm.tolist()

            # MPNet embedding (768-dim)
            vec_mpnet = embedder_mpnet.encode([text], convert_to_numpy=True)[0]
            emb_mpnet = vec_mpnet.tolist()

            # Store in Neo4j
            session.execute_write(write_player_embeddings, name, emb_minilm, emb_mpnet)

            if idx % 100 == 0:
                print(f"- Processed {idx} players...")

        print("\nDone. Player embeddings (MiniLM + MPNet) have been stored in Neo4j.")

    driver.close()


if __name__ == "__main__":
    main()
