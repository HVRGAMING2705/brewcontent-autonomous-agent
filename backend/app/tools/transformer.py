from __future__ import annotations

import httpx

from app.core.config import settings

_OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

_PROMPT_TEMPLATE = """You are a technical knowledge base writer.

Convert the raw BrewContent page content into a clean KB article.

Rules:
- Use plain English
- Use practical steps
- Include feature purpose
- Include pricing/limits exactly if shown
- Remove repeated sidebar/navigation noise
- Maximum 400 words

Page URL: {url}
Page Title: {title}

Raw Content:
{content}

Write the KB article now:
"""


def _get_model_name() -> str:
    return (
        getattr(settings, "ollama_model", None)
        or getattr(settings, "OLLAMA_MODEL", None)
        or "llama3.2:1b"
    )


class Transformer:
    async def transform(self, page: dict) -> str:
        title = page.get("title", "BrewContent Page")
        url = page.get("url", "")
        content = page.get("content", "")

        if not content.strip():
            return f"# {title}\n\nNo content was available.\n\nSource: {url}"

        prompt = _PROMPT_TEMPLATE.format(
            url=url,
            title=title,
            content=content[:5000],
        )

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    _OLLAMA_URL,
                    json={
                        "model": _get_model_name(),
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": 500,
                            "temperature": 0.2,
                            "num_ctx": 4096
                        }
                    },
                )
                response.raise_for_status()
                data = response.json()
                article = data.get("response", "").strip()

                if article:
                    return f"{article}\n\nSource: {url}"

        except Exception as exc:
            print(f"[Transformer] Ollama error: {repr(exc)}")

        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
        summary = "\n".join(lines[:80])
        return f"# {title}\n\n{summary}\n\nSource: {url}"