from __future__ import annotations

from typing import List, Dict, Any

from app.tools.retriever import Retriever
from app.tools.scraper import Scraper
from app.tools.transformer import Transformer
from app.tools.notion_sync import NotionSync
from app.tools.embedder import Embedder
from app.tools.answerer import Answerer

_SCORE_THRESHOLD = 0.55

# Keyword → path list mapping for URL planning
_URL_PLANS: List[tuple[list[str], list[str]]] = [
    (["instagram", "campaign", "post", "publish", "create content"], ["/home", "/campaign", "/templates", "/schedule"]),
    (["billing", "plan", "subscription", "payment", "invoice", "upgrade"], ["/billing"]),
    (["audience", "target", "segment", "follower"], ["/audience"]),
    (["brand", "logo", "color", "font", "kit", "style"], ["/brand-kit"]),
    (["video", "flow", "workflow", "automation", "sequence"], ["/flows"]),
    (["project", "workspace", "folder"], ["/projects"]),
    (["schedule", "calendar", "timing", "queue"], ["/schedule"]),
    (["template", "preset"], ["/templates"]),
]

_DEFAULT_PATHS = ["/home", "/campaign", "/templates"]


def _plan_urls(question: str) -> List[str]:
    """Return a list of BrewContent paths relevant to the question."""
    q = question.lower()
    for keywords, paths in _URL_PLANS:
        if any(kw in q for kw in keywords):
            return paths
    return _DEFAULT_PATHS


class Orchestrator:
    """
    Autonomous pipeline that:
      1. Searches Supabase for existing knowledge
      2. Falls back to scraping BrewContent if knowledge is missing/weak
      3. Transforms → Notion → embeds → stores → retrieves → answers
    """

    def __init__(self) -> None:
        self._retriever = Retriever()
        self._scraper = Scraper()
        self._transformer = Transformer()
        self._notion = NotionSync()
        self._embedder = Embedder()
        self._answerer = Answerer()

    async def chat(self, question: str) -> Dict[str, Any]:
        activity: List[str] = []
        sources: List[dict] = []

        # ── Step 1: Search existing KB ────────────────────────────────────
        activity.append("🔍 Searching knowledge base…")
        results = await self._retriever.search(question)

        # ── Step 2: Decide if knowledge is sufficient ─────────────────────
        top_score = results[0].get("score", 0.0) if results else 0.0
        if results and top_score >= _SCORE_THRESHOLD:
            activity.append(
                f"✅ Found {len(results)} relevant chunk(s) (top score {top_score:.2f}). Answering from KB."
            )
            sources = results
        else:
            # ── Step 3: Plan URLs ─────────────────────────────────────────
            paths = _plan_urls(question)
            activity.append(
                f"⚠️ KB score too low ({top_score:.2f}). Scraping: {', '.join(paths)}"
            )

            # ── Step 4: Scrape ────────────────────────────────────────────
            activity.append("🕷️ Scraping BrewContent pages…")
            pages = await self._scraper.scrape_pages(paths)
            activity.append(f"📄 Scraped {len(pages)} page(s).")

            for page in pages:
                title = page["title"]
                url = page["url"]

                # ── Step 5: Transform ─────────────────────────────────────
                activity.append(f"✍️ Transforming: {title}")
                article_text = await self._transformer.transform(page)

                # ── Step 6: Save to Notion (non-fatal) ────────────────────
                try:
                    ok = await self._notion.save_article(title, article_text, url)
                    if ok:
                        activity.append(f"📓 Saved to Notion: {title}")
                    else:
                        activity.append(f"⚠️ Notion save failed for: {title} (continuing)")
                except Exception as notion_err:
                    activity.append(f"⚠️ Notion error for '{title}': {notion_err} (continuing)")

                # ── Step 7: Embed ─────────────────────────────────────────
                activity.append(f"🔢 Embedding: {title}")
                embedding = self._embedder.embed_text(article_text)

                # ── Step 8: Store in Supabase ─────────────────────────────
                stored = await self._retriever.store(title, article_text, url, embedding)
                if stored:
                    activity.append(f"💾 Stored in Supabase: {title}")
                else:
                    activity.append(f"⚠️ Supabase store failed for: {title}")

            # ── Step 9: Re-retrieve ───────────────────────────────────────
            activity.append("🔍 Re-searching knowledge base after update…")
            results = await self._retriever.search(question)
            sources = results
            activity.append(
                f"✅ Final retrieval: {len(sources)} chunk(s)."
            )

        # ── Step 10: Answer ───────────────────────────────────────────────
        activity.append("💬 Generating answer…")
        answer = await self._answerer.answer(question, sources)
        activity.append("✅ Done.")

        return {
            "answer": answer,
            "sources": [
                {
                    "title": s.get("title", ""),
                    "url": s.get("url", ""),
                    "score": round(float(s.get("score", 0.0)), 3),
                }
                for s in sources
            ],
            "activity": activity,
        }
