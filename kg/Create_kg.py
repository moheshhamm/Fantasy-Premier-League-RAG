import pandas as pd
from neo4j import GraphDatabase

# ---------- 1. Read config.txt ----------

def load_config(path="config.txt"):
    config = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


# ---------- 2. Load the single CSV ----------

def load_data():
    # Make sure this filename matches your CSV name in the folder
    df = pd.read_csv("fpl_two_seasons.csv")


    # Keep only the two seasons we care about (optional, but matches milestone)
    df = df[df["season"].isin(["2021-22", "2022-23"])].copy()

    return df


# ---------- 3. Build Knowledge Graph in Neo4j ----------

def build_kg(tx, df):
    # 3.0 Clear DB
    tx.run("MATCH (n) DETACH DELETE n")

    # ========== NODES ==========

    # --- Season nodes ---
    seasons_df = df[["season"]].drop_duplicates()
    seasons = [
        {"season_name": row["season"]}
        for _, row in seasons_df.iterrows()
    ]

    tx.run("""
        UNWIND $seasons AS s
        MERGE (:Season {season_name: s.season_name})
    """, seasons=seasons)

    # --- Gameweek nodes ---
    # GW column = gameweek number
    gws_df = df[["season", "GW"]].drop_duplicates()
    gws = [
        {
            "season": row["season"],
            "GW_number": int(row["GW"])
        }
        for _, row in gws_df.iterrows()
    ]

    tx.run("""
        UNWIND $gws AS gw
        MERGE (:Gameweek {
            season: gw.season,
            GW_number: gw.GW_number
        })
    """, gws=gws)

    # --- Fixture nodes ---
    fixtures_df = df[["season", "fixture", "kickoff_time", "GW", "home_team", "away_team"]].drop_duplicates()
    fixtures = [
        {
            "season": row["season"],
            "fixture_number": int(row["fixture"]),
            "kickoff_time": row["kickoff_time"],
            "GW_number": int(row["GW"]),
            "home_team": row["home_team"],
            "away_team": row["away_team"],
        }
        for _, row in fixtures_df.iterrows()
    ]

    tx.run("""
        UNWIND $fixtures AS f
        MERGE (:Fixture {
            season: f.season,
            fixture_number: f.fixture_number,
            kickoff_time: f.kickoff_time
        })
    """, fixtures=fixtures)

    # --- Team nodes ---
    home_teams = df[["home_team"]].rename(columns={"home_team": "name"})
    away_teams = df[["away_team"]].rename(columns={"away_team": "name"})
    teams_df = pd.concat([home_teams, away_teams]).drop_duplicates()
    teams = teams_df.to_dict("records")

    tx.run("""
        UNWIND $teams AS t
        MERGE (:Team {name: t.name})
    """, teams=teams)

    # --- Position nodes ---
    # position column has values like GK/DEF/MID/FWD
    positions_df = df[["position"]].drop_duplicates()
    positions = [
        {"name": row["position"]}
        for _, row in positions_df.iterrows()
    ]

    tx.run("""
        UNWIND $positions AS p
        MERGE (:Position {name: p.name})
    """, positions=positions)

    # --- Player nodes ---
    # name = player_name, element = player_element
    players_df = df[["name", "element"]].drop_duplicates()
    players = [
        {
            "player_name": row["name"],
            "player_element": int(row["element"])
        }
        for _, row in players_df.iterrows()
    ]

    tx.run("""
        UNWIND $players AS p
        MERGE (:Player {
            player_name: p.player_name,
            player_element: p.player_element
        })
    """, players=players)

    # ========== RELATIONSHIPS ==========

    # (Season)-[:HAS_GW]->(Gameweek)
    tx.run("""
        UNWIND $gws AS gw
        MATCH (s:Season {season_name: gw.season})
        MATCH (g:Gameweek {season: gw.season, GW_number: gw.GW_number})
        MERGE (s)-[:HAS_GW]->(g)
    """, gws=gws)

    # (Gameweek)-[:HAS_FIXTURE]->(Fixture)
    tx.run("""
        UNWIND $fixtures AS f
        MATCH (g:Gameweek {season: f.season, GW_number: f.GW_number})
        MATCH (fi:Fixture {season: f.season, fixture_number: f.fixture_number})
        MERGE (g)-[:HAS_FIXTURE]->(fi)
    """, fixtures=fixtures)

    # (Fixture)-[:HAS_HOME_TEAM]->(Team) and (Fixture)-[:HAS_AWAY_TEAM]->(Team)
    tx.run("""
        UNWIND $fixtures AS f
        MATCH (fi:Fixture {season: f.season, fixture_number: f.fixture_number})
        MATCH (home:Team {name: f.home_team})
        MATCH (away:Team {name: f.away_team})
        MERGE (fi)-[:HAS_HOME_TEAM]->(home)
        MERGE (fi)-[:HAS_AWAY_TEAM]->(away)
    """, fixtures=fixtures)

    # (Player)-[:PLAYS_AS]->(Position)
    # Based on the main CSV: name + element + position
    player_pos_df = df[["name", "element", "position"]].drop_duplicates()
    player_pos = [
        {
            "player_name": row["name"],
            "player_element": int(row["element"]),
            "position_name": row["position"]
        }
        for _, row in player_pos_df.iterrows()
    ]

    tx.run("""
        UNWIND $player_pos AS pp
        MATCH (p:Player {player_name: pp.player_name, player_element: pp.player_element})
        MATCH (pos:Position {name: pp.position_name})
        MERGE (p)-[:PLAYS_AS]->(pos)
    """, player_pos=player_pos)

    # (Player)-[:PLAYED_IN]->(Fixture) with stats
    perf_cols = [
        "season", "GW", "fixture", "name", "element",
        "minutes", "goals_scored", "assists", "total_points", "bonus",
        "clean_sheets", "goals_conceded", "own_goals", "penalties_saved",
        "penalties_missed", "yellow_cards", "red_cards", "saves",
        "bps", "influence", "creativity", "threat", "ict_index", "form"
    ]

    existing_perf_cols = [c for c in perf_cols if c in df.columns]
    perf_df = df[existing_perf_cols].copy()

    performances = []
    for _, row in perf_df.iterrows():
        rec = {
            "season": row["season"],
            "fixture_number": int(row["fixture"]),
            "player_name": row["name"],
            "player_element": int(row["element"])
        }
        # add all stat fields except keys
        for c in existing_perf_cols:
            if c in ["season", "fixture", "name", "element", "GW"]:
                continue
            rec[c] = row[c]
        performances.append(rec)

    set_clauses = []
    for c in existing_perf_cols:
        if c in ["season", "fixture", "name", "element", "GW"]:
            continue
        set_clauses.append(f"r.{c} = perf.{c}")
    set_clause = ", ".join(set_clauses)

    tx.run(f"""
        UNWIND $performances AS perf
        MATCH (p:Player {{
            player_name: perf.player_name,
            player_element: perf.player_element
        }})
        MATCH (fi:Fixture {{
            season: perf.season,
            fixture_number: perf.fixture_number
        }})
        MERGE (p)-[r:PLAYED_IN]->(fi)
        SET {set_clause}
    """, performances=performances)


# ---------- 4. Main entry point ----------

def main():
    config = load_config()
    uri = config["URI"]
    user = config["USERNAME"]
    password = config["PASSWORD"]

    driver = GraphDatabase.driver(uri, auth=(user, password))

    df = load_data()

    with driver.session() as session:
        session.execute_write(build_kg, df)

    driver.close()
    print("Knowledge graph created successfully.")

if __name__ == "__main__":
    main()
