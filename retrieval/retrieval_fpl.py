# retrieval_fpl.py

from typing import Any, Dict, List
from neo4j import GraphDatabase
from kg.preprocess_fpl import load_config
import numpy as np


# -----------------------------
# 1) Neo4j driver helper
# -----------------------------

def get_driver(config_path: str = "config.txt"):
    """
    Create and return a Neo4j driver based on config.txt
    """
    config = load_config(config_path)
    uri = config["URI"]
    user = config["USERNAME"]
    password = config["PASSWORD"]
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def _run_and_collect(tx, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Helper: run a Cypher query and return a list of dict rows.
    """
    result = tx.run(cypher, **params)
    return [record.data() for record in result]


# -----------------------------
# 2) Query functions (per intent)
# -----------------------------

def _query_top_players_by_position(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    season = entities.get("season")
    position = entities.get("position")
    stat = entities.get("stat") or "total_points"
    limit = entities.get("limit") or 5

    # stat is controlled (from STAT_KEYWORDS), so safe to inject in f-string
    cypher = f"""
    MATCH (s:Season {{season_name: $season}})
          -[:HAS_GW]->(:Gameweek)
          -[:HAS_FIXTURE]->(fi:Fixture)<-[r:PLAYED_IN]-(p:Player)
          -[:PLAYS_AS]->(pos:Position {{name: $position}})
    RETURN
        p.player_name AS player,
        SUM(r.{stat}) AS value
    ORDER BY value DESC
    LIMIT $limit
    """

    params = {
        "season": season,
        "position": position,
        "limit": limit,
    }
    return _run_and_collect(tx, cypher, params)


def _query_player_season_stat(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    players = entities.get("players") or []
    if not players:
        return []
    player = players[0]  # take the first one
    season = entities.get("season")
    stat = entities.get("stat") or "total_points"

    cypher = f"""
    MATCH (p:Player {{player_name: $player}})
    MATCH (s:Season {{season_name: $season}})
          -[:HAS_GW]->(:Gameweek)
          -[:HAS_FIXTURE]->(fi:Fixture)<-[r:PLAYED_IN]-(p)
    RETURN
        p.player_name AS player,
        SUM(r.{stat}) AS value
    """

    params = {
        "player": player,
        "season": season,
    }
    return _run_and_collect(tx, cypher, params)


def _query_player_gw_stat(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    players = entities.get("players") or []
    if not players:
        return []
    player = players[0]
    season = entities.get("season")
    gw = entities.get("gw")
    stat = entities.get("stat") or "total_points"

    cypher = f"""
    MATCH (p:Player {{player_name: $player}})
    MATCH (s:Season {{season_name: $season}})
          -[:HAS_GW]->(gw:Gameweek {{GW_number: $gw}})
          -[:HAS_FIXTURE]->(fi:Fixture)<-[r:PLAYED_IN]-(p)
    RETURN
        p.player_name AS player,
        gw.GW_number AS gameweek,
        SUM(r.{stat}) AS value
    """

    params = {
        "player": player,
        "season": season,
        "gw": gw,
    }
    return _run_and_collect(tx, cypher, params)


def _query_compare_two_players(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    players = entities.get("players") or []
    if len(players) < 2:
        # we can still compare 1 player, but usually we expect 2+
        pass
    season = entities.get("season")
    stat = entities.get("stat") or "total_points"

    cypher = f"""
    MATCH (p:Player)
    WHERE p.player_name IN $players
    MATCH (s:Season {{season_name: $season}})
          -[:HAS_GW]->(:Gameweek)
          -[:HAS_FIXTURE]->(fi:Fixture)<-[r:PLAYED_IN]-(p)
    RETURN
        p.player_name AS player,
        SUM(r.{stat}) AS value
    ORDER BY value DESC
    """

    params = {
        "players": players,
        "season": season,
    }
    return _run_and_collect(tx, cypher, params)


def _query_team_top_players(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    teams = entities.get("teams") or []
    if not teams:
        return []
    team = teams[0]
    season = entities.get("season")
    stat = entities.get("stat") or "total_points"
    limit = entities.get("limit") or 5
    position = entities.get("position")  # optional filter

    # base Cypher
    base_cypher = f"""
    MATCH (t:Team {{name: $team}})
    MATCH (s:Season {{season_name: $season}})
          -[:HAS_GW]->(:Gameweek)
          -[:HAS_FIXTURE]->(fi:Fixture)
    MATCH (fi)-[:HAS_HOME_TEAM|HAS_AWAY_TEAM]->(t)
    MATCH (p:Player)-[r:PLAYED_IN]->(fi)
    OPTIONAL MATCH (p)-[:PLAYS_AS]->(pos:Position)
    """


    where_clause = ""
    if position:
        where_clause = "WHERE pos.name = $position"

    cypher = f"""
    {base_cypher}
    {where_clause}
    RETURN
        p.player_name AS player,
        SUM(r.{stat}) AS value
    ORDER BY value DESC
    LIMIT $limit
    """

    params = {
        "team": team,
        "season": season,
        "limit": limit,
        "position": position,
    }
    return _run_and_collect(tx, cypher, params)


def _query_fixture_top_players(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    season = entities.get("season")
    fixture_number = entities.get("fixture_number")
    stat = entities.get("stat") or "total_points"
    limit = entities.get("limit") 
    cypher = f"""
    MATCH (fi:Fixture {{
        season: $season,
        fixture_number: $fixture_number
    }})
    MATCH (p:Player)-[r:PLAYED_IN]->(fi)
    RETURN
        p.player_name AS player,
        r.{stat} AS value
    ORDER BY value DESC
    LIMIT coalesce($limit, 1000)
    """

    params = {
        "season": season,
        "fixture_number": fixture_number,
        "limit": limit,
    }
    return _run_and_collect(tx, cypher, params)


def _query_discipline_stats(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    season = entities.get("season")
    stat = entities.get("stat") or "yellow_cards"  # either yellow_cards or red_cards

    # We'll compute both yellow and red, but order by the requested one
    order_field = "yellow_cards" if stat == "yellow_cards" else "red_cards"

    cypher = f"""
    MATCH (s:Season {{season_name: $season}})
          -[:HAS_GW]->(:Gameweek)
          -[:HAS_FIXTURE]->(fi:Fixture)<-[r:PLAYED_IN]-(p:Player)
    RETURN
        p.player_name AS player,
        SUM(coalesce(r.yellow_cards, 0)) AS yellow_cards,
        SUM(coalesce(r.red_cards, 0)) AS red_cards
    ORDER BY {order_field} DESC
    LIMIT coalesce($limit, 1000)
    """

    params = {
    "season": season,
    "limit": entities.get("limit")
}
    return _run_and_collect(tx, cypher, params)


def _query_team_season_stat(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    New template:
    TEAM_SEASON_STAT – aggregate a stat (e.g. goals_scored, total_points) for a team in a season.

    Example question:
    - "How many goals did Liverpool score in 2021-22?"
    """
    teams = entities.get("teams", [])
    season = entities.get("season")
    stat = entities.get("stat") or "total_points"

    if not teams or not season:
        return []

    team = teams[0]

    cypher = f"""
    MATCH (t:Team {{name: $team}})
    MATCH (s:Season {{season_name: $season}})
          -[:HAS_GW]->(:Gameweek)
          -[:HAS_FIXTURE]->(fi:Fixture)
    MATCH (fi)-[:HAS_HOME_TEAM|HAS_AWAY_TEAM]->(t)
    MATCH (p:Player)-[r:PLAYED_IN]->(fi)
    RETURN
        t.name AS team,
        SUM(r.{stat}) AS value
    """

    result = tx.run(cypher, team=team, season=season)
    return [record.data() for record in result]


def _query_gameweek_top_players(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    New template:
    GAMEWEEK_TOP_PLAYERS – top players in a single gameweek (by some stat, usually total_points).

    Example question:
    - "Who were the top players in GW 5 of 2022-23 by total points?"
    """
    season = entities.get("season")
    gw = entities.get("gw")
    stat = entities.get("stat") or "total_points"
    limit = entities.get("limit") or 5

    if season is None or gw is None:
        return []

    cypher = f"""
    MATCH (s:Season {{season_name: $season}})
          -[:HAS_GW]->(gw:Gameweek {{GW_number: $gw}})
          -[:HAS_FIXTURE]->(fi:Fixture)
    MATCH (p:Player)-[r:PLAYED_IN]->(fi)
    OPTIONAL MATCH (p)-[:PLAYS_AS]->(pos:Position)
    RETURN
        p.player_name AS player,
        pos.name AS position,
        SUM(r.{stat}) AS value
    ORDER BY value DESC
    LIMIT $limit
    """

    result = tx.run(cypher, season=season, gw=gw, limit=limit)
    return [record.data() for record in result]



def _query_generic_stats(tx, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fallback: if we don't recognize a specific intent,
    just return top players by total_points in a season (if given),
    or across all seasons otherwise.
    """
    season = entities.get("season")
    stat = entities.get("stat") or "total_points"

    if season:
        cypher = f"""
        MATCH (s:Season {{season_name: $season}})
              -[:HAS_GW]->(:Gameweek)
              -[:HAS_FIXTURE]->(fi:Fixture)<-[r:PLAYED_IN]-(p:Player)
        RETURN
            p.player_name AS player,
            SUM(r.{stat}) AS value
        ORDER BY value DESC
        """
        params = {"season": season}
    else:
        cypher = f"""
        MATCH (p:Player)-[r:PLAYED_IN]->(:Fixture)
        RETURN
            p.player_name AS player,
            SUM(r.{stat}) AS value
        ORDER BY value DESC
        """
        params = {}

    return _run_and_collect(tx, cypher, params)


# -----------------------------
# 3) Dispatcher (baseline_retrieve)
# -----------------------------

# -----------------------------
# 3) Dispatcher (baseline_retrieve)
# -----------------------------

def baseline_retrieve(driver, preprocessed: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Main baseline retrieval function.

    - Reads intent + entities from Component 1
    - Chooses a Cypher template
    - Executes it on Neo4j
    - Returns list of dict rows
    """
    intent = preprocessed["intent"]
    entities = preprocessed["entities"]

    with driver.session() as session:
        if intent == "TOP_PLAYERS_BY_POSITION":
            return session.execute_read(_query_top_players_by_position, entities)
        elif intent == "PLAYER_SEASON_STAT":
            return session.execute_read(_query_player_season_stat, entities)
        elif intent == "PLAYER_GW_STAT":
            return session.execute_read(_query_player_gw_stat, entities)
        elif intent == "COMPARE_TWO_PLAYERS":
            return session.execute_read(_query_compare_two_players, entities)
        elif intent == "TEAM_TOP_PLAYERS":
            return session.execute_read(_query_team_top_players, entities)
        elif intent == "FIXTURE_TOP_PLAYERS":
            return session.execute_read(_query_fixture_top_players, entities)
        elif intent == "DISCIPLINE_STATS":
            return session.execute_read(_query_discipline_stats, entities)
        elif intent == "TEAM_SEASON_STAT":                  # NEW
            return session.execute_read(_query_team_season_stat, entities)
        elif intent == "GAMEWEEK_TOP_PLAYERS":              # NEW
            return session.execute_read(_query_gameweek_top_players, entities)
        else:
            return session.execute_read(_query_generic_stats, entities)

def embedding_retrieve_players_minilm(driver, query_embedding: Any, k: int = 10) -> List[Dict[str, Any]]:
    """
    Semantic similarity search using MiniLM embeddings stored in p.embedding_minilm.
    """
    # Ensure we pass a plain Python list to Neo4j
    if isinstance(query_embedding, np.ndarray):
        query_vec = query_embedding.tolist()
    else:
        query_vec = list(query_embedding)

    cypher = """
    CALL db.index.vector.queryNodes(
        'player_embedding_minilm_index',
        $k,
        $query_vec
    )
    YIELD node, score
    RETURN node.player_name AS player, score
    ORDER BY score DESC
    """

    with driver.session() as session:
        result = session.run(cypher, k=k, query_vec=query_vec)
        return [record.data() for record in result]


def embedding_retrieve_players_mpnet(driver, query_embedding: Any, k: int = 10) -> List[Dict[str, Any]]:
    """
    Semantic similarity search using MPNet embeddings stored in p.embedding_mpnet.
    """
    if isinstance(query_embedding, np.ndarray):
        query_vec = query_embedding.tolist()
    else:
        query_vec = list(query_embedding)

    cypher = """
    CALL db.index.vector.queryNodes(
        'player_embedding_mpnet_index',
        $k,
        $query_vec
    )
    YIELD node, score
    RETURN node.player_name AS player, score
    ORDER BY score DESC
    """

    with driver.session() as session:
        result = session.run(cypher, k=k, query_vec=query_vec)
        return [record.data() for record in result]


