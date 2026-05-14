from __future__ import annotations

from notion_client import AsyncClient

from app.core.config import settings


class NotionSync:
    """Saves KB articles to the configured Notion database."""

    def _get_client(self) -> AsyncClient:
        return AsyncClient(auth=settings.notion_token)

    async def save_article(self, title: str, content: str, url: str) -> bool:
        """
        Create a new page in the Notion database with the given article.

        Uses the property names exactly as defined:
          - 'KB Articles'  (title property)
          - 'Source URL'  (url property)

        Returns True on success, False on failure.
        Does NOT raise — the orchestrator catches errors independently.
        """
        try:
            client = self._get_client()

            # Notion page content blocks (paragraphs)
            blocks = []
            for paragraph in content.split("\n"):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                blocks.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": paragraph[:2000]}}
                            ]
                        },
                    }
                )

            await client.pages.create(
                parent={"database_id": settings.notion_database_id},
                properties={
                    "KB Articles": {
                        "title": [{"type": "text", "text": {"content": title[:255]}}]
                    },
                    "Source URL": {
                        "url": url
                    },
                },
                children=blocks[:100],  # Notion API limit
            )
            return True
        except Exception as exc:
            print(f"[NotionSync] error saving '{title}': {exc}")
            return False
