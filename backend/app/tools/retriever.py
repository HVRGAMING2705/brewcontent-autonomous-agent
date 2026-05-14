from __future__ import annotations

import json
from typing import List

from supabase import create_client, Client

from app.core.config import settings
from app.tools.embedder import Embedder

_embedder = Embedder()
_TABLE = "kb_chunks"
_RPC = "match_kb_chunks"


def _get_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_key)


class Retriever:
    """Semantic search and storage backed by Supabase pgvector."""

    async def search(self, question: str) -> List[dict]:
        """
        Embed *question* and run the match_kb_chunks RPC.
        Returns a list of dicts with keys: id, title, url, content, score.
        Returns an empty list on any error so the orchestrator can fall back.
        """
        try:
            embedding = _embedder.embed_text(question)
            client = _get_client()
            response = client.rpc(
                _RPC,
                {"query_embedding": embedding, "match_count": 5},
            ).execute()
            if response.data:
                return response.data
            return []
        except Exception as exc:
            print(f"[Retriever.search] error: {exc}")
            return []

    async def store(
        self,
        title: str,
        content: str,
        url: str,
        embedding: List[float],
    ) -> bool:
        """
        Upsert a chunk into kb_chunks.
        Returns True on success, False on failure.
        """
        try:
            client = _get_client()
            client.table(_TABLE).upsert(
                {
                    "title": title,
                    "url": url,
                    "content": content,
                    "embedding": json.dumps(embedding),
                },
                on_conflict="url",
            ).execute()
            return True
        except Exception as exc:
            print(f"[Retriever.store] error: {exc}")
            return False
