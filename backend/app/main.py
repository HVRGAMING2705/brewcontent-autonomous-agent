from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.tools.orchestrator import Orchestrator
from app.tools.retriever import Retriever

app = FastAPI(title="BrewContent Knowledge Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_orchestrator = Orchestrator()
_retriever = Retriever()


# ── Request / Response models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list
    activity: list


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "BrewContent Knowledge Agent"}


@app.get("/kb/status")
async def kb_status():
    """Return how many chunks are in the knowledge base."""
    try:
        # A broad search to count results; use a generic term
        results = await _retriever.search("brewcontent features campaign")
        return {
            "status": "ok",
            "chunks_found": len(results),
            "message": f"KB is reachable. Found {len(results)} sample chunks.",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main autonomous chat endpoint."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        result = await _orchestrator.chat(request.message.strip())
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
