from __future__ import annotations
import asyncio
from pathlib import Path
from typing import List
from playwright.async_api import async_playwright, BrowserContext, Page
from app.core.config import settings

_ROOT = Path(__file__).resolve().parents[3]
_AUTH_JSON = _ROOT / "auth.json"

async def _scrape_one(context, url):
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        try:
            await page.wait_for_selector("h1, h2, main", timeout=10000)
        except Exception:
            pass
        await asyncio.sleep(6)
        title = await page.title()
        js = "['nav','script','style','noscript','svg'].forEach(t=>document.querySelectorAll(t).forEach(e=>e.remove()));return document.body?document.body.innerText.trim():''"
        content = await page.evaluate("() => {" + js + "}")
        content = content[:8000]
        print(f"[Scraper] {url} -> {len(content)} chars")
        return {"title": title or url, "url": url, "content": content}
    except Exception as exc:
        print(f"[Scraper] failed {url}: {exc}")
        return {"title": url, "url": url, "content": ""}
    finally:
        await page.close()

class Scraper:
    async def scrape_pages(self, urls):
        results = []
        full_urls = [u if u.startswith("http") else settings.brew_base_url + u for u in urls]
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            kw = {"storage_state": str(_AUTH_JSON)} if _AUTH_JSON.exists() else {}
            context = await browser.new_context(**kw)
            try:
                for url in full_urls:
                    d = await _scrape_one(context, url)
                    if d["content"].strip():
                        results.append(d)
            finally:
                await context.close()
                await browser.close()
        return results