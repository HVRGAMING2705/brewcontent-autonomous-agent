from __future__ import annotations

from typing import List

import httpx

from app.core.config import settings

_OLLAMA_URL = "http://localhost:11434/api/generate"

_SYSTEM = """You are a helpful product assistant for BrewContent, an AI-powered content creation platform.
Answer the user's question using ONLY the provided knowledge base excerpts.
Be concise, friendly, and practical.
If the excerpts don't contain enough information, say so honestly.
Do not invent features or steps."""

_PROMPT_TEMPLATE = """Knowledge base excerpts:
{context}

User question: {question}

Answer:"""


class Answerer:
    """Generates a natural-language answer from retrieved KB sources using Ollama."""

    async def answer(self, question: str, sources: List[dict]) -> str:
        """
        Build context from *sources* and call Ollama to produce a final answer.
        Falls back to a context-only answer if Ollama is unavailable.
        """
        if not sources:
            return (
                "I couldn't find relevant information in the knowledge base for your question. "
                "Try rephrasing or asking about a specific BrewContent feature."
            )

        # Build context string from top sources
        context_parts = []
        for s in sources[:4]:
            title = s.get("title", "")
            content = s.get("content", "")
            snippet = content[:800] if len(content) > 800 else content
            context_parts.append(f"**{title}**\n{snippet}")
        context = "\n\n---\n\n".join(context_parts)

        prompt = _PROMPT_TEMPLATE.format(context=context, question=question)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    _OLLAMA_URL,
                    json={
                        "model": settings.ollama_model,
                        "system": _SYSTEM,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                answer = data.get("response", "").strip()
                if answer:
                    return answer
        except Exception as exc:
            print(f"[Answerer] Ollama error: {exc}")

        # Fallback: return the top snippet directly
        top = sources[0]
        content = top.get("content", "")
        return (
            f"Based on the knowledge base:\n\n"
            f"{content[:600]}\n\n"
            f"_(AI summarisation unavailable — showing raw excerpt)_"
        )
