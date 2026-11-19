from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from kg.preprocess_fpl import build_lexicon_from_neo4j, load_embedder, preprocess_input
from retrieval.retrieval_fpl import get_driver, baseline_retrieve, embedding_retrieve_players_minilm
from llm.answer_generator import generate_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load once
lexicon = build_lexicon_from_neo4j("config.txt")
embedder = load_embedder()
driver = get_driver("config.txt")

class Query(BaseModel):
    question: str
    models: list[str] = ["llama"]


# ---- Smart small-talk detection ----
SMALL_TALK = {
    "hi", "hello", "hey", "yo",
    "who are you", "what are you",
    "what can you do", "help"
}


@app.post("/query")
def run_query(q: Query):

    question = q.question.strip()
    lowered = question.lower()

    # 🧠 Chat mode (no KG, no Neo4j)
    if lowered in SMALL_TALK:
        return {
            "final_answer": "👋 Hi! I’m an AI assistant built to analyze Fantasy Premier League data using knowledge graphs and multiple large language models. Ask me anything about players, teams, seasons, or FPL strategy!",
            "model_responses": {},
            "merged_count": 0,
        }

    # ---- Normal Graph-RAG pipeline ----
    pre = preprocess_input(question, lexicon, embedder)

    baseline = baseline_retrieve(driver, pre)
    embeddings = embedding_retrieve_players_minilm(driver, pre["embedding"], k=5)

    retrieval = {
        "baseline": baseline,
        "embeddings": embeddings
    }

    config = {
        "models": [
            m for m in [
                {"name": "llama", "model": "llama-3.3-70b-versatile"},
                {"name": "qwen", "model": "qwen/qwen3-32b"},
                {"name": "gpt-oss", "model": "openai/gpt-oss-120b"},
            ]
            if m["name"] in q.models
        ]
    }

    return generate_answer(pre, retrieval, config)