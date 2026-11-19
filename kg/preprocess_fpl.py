# preprocess_fpl.py

from neo4j import GraphDatabase
from dataclasses import dataclass
from typing import List, Dict, Any
import re
from typing import Optional

from sentence_transformers import SentenceTransformer

# ---------- 1. Load Neo4j config (same style as Create_kg.py) ----------

def load_config(path: str = "config.txt") -> Dict[str, str]:
    config = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config

@dataclass
class FPLLexicon:
    players: List[str]
    teams: List[str]
    positions: List[str]
    seasons: List[str]

    # lowercase versions for matching
    players_lc: List[str]
    teams_lc: List[str]
    positions_lc: List[str]
    seasons_lc: List[str]

def build_lexicon_from_neo4j(config_path: str = "config.txt") -> FPLLexicon:
    config = load_config(config_path)
    uri = config["URI"]
    user = config["USERNAME"]
    password = config["PASSWORD"]

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        # Players
        players = sorted([
            record["name"]
            for record in session.run("MATCH (p:Player) RETURN DISTINCT p.player_name AS name")
        ])

        # Teams
        teams = sorted([
            record["name"]
            for record in session.run("MATCH (t:Team) RETURN DISTINCT t.name AS name")
        ])

        # Positions
        positions = sorted([
            record["name"]
            for record in session.run("MATCH (pos:Position) RETURN DISTINCT pos.name AS name")
        ])

        # Seasons
        seasons = sorted([
            record["name"]
            for record in session.run("MATCH (s:Season) RETURN DISTINCT s.season_name AS name")
        ])

    driver.close()

    return FPLLexicon(
        players=players,
        teams=teams,
        positions=positions,
        seasons=seasons,
        players_lc=[p.lower() for p in players],
        teams_lc=[t.lower() for t in teams],
        positions_lc=[p.lower() for p in positions],
        seasons_lc=[s.lower() for s in seasons],
    )

STAT_KEYWORDS = {
    "goal": "goals_scored",
    "goals": "goals_scored",
    "assist": "assists",
    "assists": "assists",
    "total points": "total_points",
    "points": "total_points",
    "clean sheet": "clean_sheets",
    "clean sheets": "clean_sheets",
    "yellow card": "yellow_cards",
    "yellow cards": "yellow_cards",
    "red card": "red_cards",
    "red cards": "red_cards",
    "saves": "saves",
    # you can add more mappings if needed
}

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def extract_season(text: str, lex: FPLLexicon) -> Optional[str]:
    t = text.lower()

    # --------------------------------------------------
    # Natural language season references
    # --------------------------------------------------
    if "this season" in t or "current season" in t:
        return lex.seasons[-1]  # latest season

    if "last season" in t or "previous season" in t:
        if len(lex.seasons) >= 2:
            return lex.seasons[-2]

    # --------------------------------------------------
    # Direct match from KG seasons (e.g. "2022-23")
    # --------------------------------------------------
    for s, s_lc in zip(lex.seasons, lex.seasons_lc):
        if s_lc in t:
            return s

    # --------------------------------------------------
    # Pattern match: 2022-23 or 2022/23
    # --------------------------------------------------
    m = re.search(r"(20\d{2})\s*[-/]\s*(\d{2})", t)
    if m:
        season_str = f"{m.group(1)}-{m.group(2)}"
        if season_str in lex.seasons:
            return season_str

    # --------------------------------------------------
    # Pattern match: 21/22
    # --------------------------------------------------
    m = re.search(r"\b(\d{2})/(\d{2})\b", t)
    if m:
        start = int(m.group(1))
        end = int(m.group(2))
        season_str = f"20{start}-{end:02d}"
        if season_str in lex.seasons:
            return season_str

    return None
def extract_gameweek(text: str) -> Optional[int]:
    t = text.lower()
    for pattern in [
        r"\bgw\s*(\d+)\b",
        r"\bgameweek\s*(\d+)\b",
        r"\bweek\s*(\d+)\b",
        r"\bround\s*(\d+)\b",
        r"\bmatchweek\s*(\d+)\b"
    ]:
        m = re.search(pattern, t)
        if m:
            return int(m.group(1))
    return None

def extract_fixture_number(text: str) -> Optional[int]:
    t = text.lower()
    m = re.search(r"\bfixture\s*(\d+)\b", t)
    if m:
        return int(m.group(1))
    return None
def extract_position(text: str, lex: FPLLexicon) -> Optional[str]:
    t = text.lower()
    # keywords → canonical roles
    if "goalkeeper" in t or re.search(r"\bgk\b", t):
        return "GK"
    if "defender" in t or "defenders" in t or re.search(r"\bdef\b", t):
        return "DEF"
    if "midfielder" in t or "midfielders" in t or re.search(r"\bmid\b", t):
        return "MID"
    if "forward" in t or "forwards" in t or "striker" in t or re.search(r"\bfwd\b", t):
        return "FWD"

    # maybe the question directly uses "FWD" etc.
    for pos, pos_lc in zip(lex.positions, lex.positions_lc):
        if pos_lc in t:
            return pos

    return None
def extract_players(text: str, lex: FPLLexicon) -> List[str]:
    players_found = set()
    t = text.lower()
    tokens = t.split()

    # --- 1) Full-name matching (same as before) ---
    for n in [3, 2, 1]:
        for i in range(len(tokens) - n + 1):
            span = " ".join(tokens[i:i+n])
            if span in lex.players_lc:
                idx = lex.players_lc.index(span)
                players_found.add(lex.players[idx])

    # --- 2) Last-name / single-token matching (e.g. "Haaland", "Kane") ---
    # Only if we haven't already matched them via full name
    for token in tokens:
        if len(token) <= 2:
            continue  # skip very short tokens like "in", "to", etc.

        # find all players whose name contains this token as a full word
        candidates = []
        for p_lc, p in zip(lex.players_lc, lex.players):
            # match token as separate word inside the player name
            if re.search(rf"\b{re.escape(token)}\b", p_lc):
                candidates.append(p)

        # if exactly ONE player has this last name, we can safely choose it
        if len(candidates) == 1:
            players_found.add(candidates[0])

    return list(players_found)

def extract_teams(text: str, lex: FPLLexicon) -> List[str]:
    teams_found = set()
    t = text.lower()
    for team, team_lc in zip(lex.teams, lex.teams_lc):
        if team_lc in t:
            teams_found.add(team)
    return list(teams_found)
def extract_stat(text: str) -> Optional[str]:
    t = text.lower()

    # handle multi-word keys first (like "total points", "clean sheet")
    for phrase in ["total points", "clean sheet", "clean sheets", "yellow cards",
                   "yellow card", "red card", "red cards"]:
        if phrase in t:
            return STAT_KEYWORDS[phrase]

    # single-word matches
    for word in ["goals", "goal", "assists", "assist", "points", "saves", "bonus"]:
        if re.search(rf"\b{word}\b", t):
            return STAT_KEYWORDS.get(word)

    return None
def extract_limit(text: str, default: int = 5) -> Optional[int]:
    t = text.lower()
    m = re.search(r"\btop\s+(\d+)\b", t)
    if m:
        return int(m.group(1))
    if "top" in t or "best" in t or "most" in t:
        return default
    return None
def extract_entities(user_text: str, lex: FPLLexicon) -> Dict[str, Any]:
    return {
        "players": extract_players(user_text, lex),
        "teams": extract_teams(user_text, lex),
        "position": extract_position(user_text, lex),
        "season": extract_season(user_text, lex),
        "gw": extract_gameweek(user_text),
        "fixture_number": extract_fixture_number(user_text),
        "stat": extract_stat(user_text),
        "limit": extract_limit(user_text),
    }
def classify_intent(user_text: str, entities: Dict[str, Any]) -> str:
    t = user_text.lower()
    players = entities.get("players", [])
    teams = entities.get("teams", [])
    has_stat = entities.get("stat") is not None
    has_season = entities.get("season") is not None
    has_gw = entities.get("gw") is not None
    has_fixture = entities.get("fixture_number") is not None
    has_position = entities.get("position") is not None

    # --------------------------------------------------
    # 1) Compare two players (MOST specific)
    # --------------------------------------------------
    if len(players) >= 2 or " vs " in t or " versus " in t or "compare" in t:
        return "COMPARE_TWO_PLAYERS"

    # --------------------------------------------------
    # 2) Player stat in a specific gameweek
    # --------------------------------------------------
    if players and has_season and has_gw and has_stat:
        return "PLAYER_GW_STAT"

    # --------------------------------------------------
    # 3) Top players in a specific gameweek
    # --------------------------------------------------
    if has_season and has_gw and ("top" in t or "best" in t or "most" in t) and not players:
        return "GAMEWEEK_TOP_PLAYERS"

    # --------------------------------------------------
    # 4) Player season stat
    # --------------------------------------------------
    if players and has_season and has_stat:
        return "PLAYER_SEASON_STAT"

    # --------------------------------------------------
    # 5) Team aggregate season stat (not per-player)
    # --------------------------------------------------
    if teams and has_season and has_stat and ("how many" in t or "total" in t or "sum" in t):
        if "player" not in t and "players" not in t:
            return "TEAM_SEASON_STAT"

    # --------------------------------------------------
    # 6) Top players by position
    # --------------------------------------------------
    if ("top" in t or "best" in t or "most" in t) and has_position:
        return "TOP_PLAYERS_BY_POSITION"

    # --------------------------------------------------
    # 7) Team top players
    # --------------------------------------------------
    if teams and has_season and ("top" in t or "best" in t or "most" in t):
        return "TEAM_TOP_PLAYERS"

    # --------------------------------------------------
    # 8) Fixture-focused stats
    # --------------------------------------------------
    if has_fixture or ("fixture" in t and has_season):
        return "FIXTURE_TOP_PLAYERS"

    # --------------------------------------------------
    # 9) Discipline stats
    # --------------------------------------------------
    if "yellow card" in t or "yellow cards" in t or "red card" in t or "red cards" in t:
        return "DISCIPLINE_STATS"

    # --------------------------------------------------
    # 10) Safety fallback: player + season should never be generic
    # --------------------------------------------------
    if players and has_season:
        return "PLAYER_SEASON_STAT"

    # --------------------------------------------------
    # Final fallback
    # --------------------------------------------------
    return "GENERIC_STATS_QUESTION"
def load_embedder(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    return SentenceTransformer(model_name)

def embed_query(text: str, embedder: SentenceTransformer):
    # returns a 384-dim numpy array
    return embedder.encode([text], convert_to_numpy=True)[0]
def preprocess_input(
    user_text: str,
    lexicon: FPLLexicon,
    embedder: SentenceTransformer
) -> Dict[str, Any]:
    """
    Main function of Component 1:
    - Extract entities
    - Classify intent
    - Embed input
    """
    entities = extract_entities(user_text, lexicon)
    intent = classify_intent(user_text, entities)
    embedding = embed_query(user_text, embedder)

    return {
        "text": user_text,
        "intent": intent,
        "entities": entities,
        "embedding": embedding,
    }
