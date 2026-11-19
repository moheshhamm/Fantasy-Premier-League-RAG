# test_retrieval_extended.py

from preprocess_fpl import (
    build_lexicon_from_neo4j,
    load_embedder,
    preprocess_input,
)
from retrieval_fpl import get_driver, baseline_retrieve


def main():
    # 1) Build lexicon & embedder (Component 1)
    print("Building lexicon...")
    lexicon = build_lexicon_from_neo4j("config.txt")
    print(f"- Players loaded: {len(lexicon.players)}")
    print(f"- Teams loaded: {len(lexicon.teams)}")
    print(f"- Seasons loaded: {len(lexicon.seasons)}")

    print("\nLoading embedder...")
    embedder = load_embedder()
    print("- Embedder loaded.\n")

    # 2) Connect to Neo4j
    driver = get_driver("config.txt")

    # 3) Extended set of queries (12+)
    queries = [
        # TOP_PLAYERS_BY_POSITION
        "Top 5 FWDs in 2022-23 by total points",
        "Top 3 defenders in 2021-22 with the highest total points",

        # PLAYER_SEASON_STAT
        "How many goals did Mohamed Salah score in 2021-22?",
        "How many assists did Kevin De Bruyne get in 2022-23?",

        # PLAYER_GW_STAT
        "How many points did Erling Haaland get in GW 3 of 2022-23?",
        "How many goals did Harry Kane score in GW 10 of 2021-22?",

        # COMPARE_TWO_PLAYERS
        "Compare Haaland and Kane in 2022-23 total points",
        "Compare Mohamed Salah vs Kevin De Bruyne in 2021-22 by assists",

        # TEAM_TOP_PLAYERS
        "Which Liverpool players had the most goals in 2021-22?",
        "Which Man City players scored the most total points in 2022-23?",

        # TEAM_SEASON_STAT (NEW)
        "How many goals did Liverpool score in 2021-22?",
        "What was the total points scored by Arsenal in 2022-23?",

        # FIXTURE_TOP_PLAYERS
        "Who were the top players in fixture 120 of 2022-23 by total points",
        "Who scored the most goals in fixture 50 in 2021-22?",

        # GAMEWEEK_TOP_PLAYERS (NEW)
        "Who were the top players in GW 5 of 2022-23 by total points?",
        "Show me the best players in GW 1 of 2021-22 by total points",

        # DISCIPLINE_STATS
        "Who got the most yellow cards in 2022-23?",
        "Which player received the most red cards in 2021-22?",
    ]

    print("\n==================== EXTENDED BASELINE RETRIEVAL TEST ====================\n")

    for q in queries:
        print("=" * 80)
        print("USER QUERY:", q)

        pre = preprocess_input(q, lexicon, embedder)
        print("Intent:", pre["intent"])
        print("Entities:", pre["entities"])

        rows = baseline_retrieve(driver, pre)
        print("\nBaseline results:")
        if not rows:
            print("(No results)")
        else:
            for row in rows[:10]:  # top 10 rows max
                print(row)

        print("\n" + "=" * 80 + "\n")

    driver.close()


if __name__ == "__main__":
    main()
