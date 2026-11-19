# evaluate_preprocess.py

from preprocess_fpl import (
    build_lexicon_from_neo4j,
    load_embedder,
    preprocess_input,
)


def main():

    # -------------------------
    # 1) Build lexicon
    # -------------------------
    print("Building lexicon...")
    lexicon = build_lexicon_from_neo4j("config.txt")
    print(f"- Players loaded: {len(lexicon.players)}")
    print(f"- Teams loaded: {len(lexicon.teams)}")
    print(f"- Seasons loaded: {len(lexicon.seasons)}")

    # -------------------------
    # 2) Load embedder
    # -------------------------
    print("\nLoading embedder...")
    embedder = load_embedder()
    print("- Embedder loaded.\n")

    # -------------------------
    # 3) Test cases
    # -------------------------
    test_cases = [
        ("Top 5 FWDs in 2022-23 by total points", "TOP_PLAYERS_BY_POSITION"),
        ("Top 3 defenders in 2021-22 with the highest total points", "TOP_PLAYERS_BY_POSITION"),
        ("How many goals did Mohamed Salah score in 2021-22?", "PLAYER_SEASON_STAT"),
        ("How many points did Erling Haaland get in GW 3 of 2022-23?", "PLAYER_GW_STAT"),
        ("Compare Haaland and Kane in 2022-23 total points", "COMPARE_TWO_PLAYERS"),
        ("Compare Mohamed Salah vs Kevin De Bruyne in 2021-22 by assists", "COMPARE_TWO_PLAYERS"),
        ("Which Liverpool players had the most goals in 2021-22?", "TEAM_TOP_PLAYERS"),
        ("Which Manchester City players scored the most total points in 2022-23?", "TEAM_TOP_PLAYERS"),
        ("Who got the most yellow cards in 2022-23?", "DISCIPLINE_STATS"),
        ("Which player received the most red cards in 2021-22?", "DISCIPLINE_STATS"),
        ("Who were the top players in fixture 120 of 2022-23 by total points?", "FIXTURE_TOP_PLAYERS"),
        ("Who scored the most goals in fixture 50 in 2021-22?", "FIXTURE_TOP_PLAYERS"),
        ("How many clean sheets did Alisson keep in 2021-22?", "PLAYER_SEASON_STAT"),
        ("Show me the best midfielders from Arsenal in 2022-23", "TEAM_TOP_PLAYERS"),
        ("Who was the best player in FPL last season?", "GENERIC_STATS_QUESTION"),
        ("Give me some stats about Bukayo Saka", "GENERIC_STATS_QUESTION"),
    ]

    correct = 0

    for q, expected_intent in test_cases:
        print("=" * 80)
        print("Query:", q)
        print("Expected intent:", expected_intent)

        # Now lexicon & embedder exist in this scope ✔
        result = preprocess_input(q, lexicon, embedder)
        predicted_intent = result["intent"]

        print("Predicted intent:", predicted_intent)
        print("Entities:", result["entities"])

        if predicted_intent == expected_intent:
            print("✔ Correct")
            correct += 1
        else:
            print("✘ Incorrect")

    print("\n-----------------------------------------------")
    print(f"Total correct intents: {correct} / {len(test_cases)}")
    print(f"Accuracy: {correct/len(test_cases):.2f}")


if __name__ == "__main__":
    main()
