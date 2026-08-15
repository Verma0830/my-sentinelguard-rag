# Vercel SQLite Compatibility Fix
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
import sys
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure current directory is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_engine import RAGEngine

app = FastAPI(title="SentinelGuard CRAG API", version="1.0.0")

# Enable CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4
    model: Optional[str] = "nvidia/nemotron-3.5-lightning:free"

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "SentinelGuard CRAG API"}

@app.get("/api/stats")
def get_stats():
    return {
        "status": "online",
        "chunks_count": 199,
        "engine": "nvidia/nemotron-3.5-lightning:free",
        "vector_db": "ChromaDB (HNSW Cosine)"
    }

@app.post("/api/query")
def query_rag(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    start_time = time.time()
    try:
        engine = RAGEngine()
        result = engine.query(
            user_query=req.query,
            top_k=req.top_k or 4,
            model_name=req.model or "nvidia/nemotron-3.5-lightning:free"
        )
        elapsed = time.time() - start_time
        
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "telemetry": {
                "latency": round(elapsed, 2),
                "chunks_count": len(result["sources"]),
                "model": req.model or "nvidia/nemotron-3.5-lightning:free"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
