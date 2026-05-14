import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://app.brewcontent.ai"

PAGES = [
    "/home",
    "/projects",
    "/templates",
    "/audience",
    "/brand-kit",
    "/flows",
    "/campaign",
    "/schedule",
    "/billing",
]

async def scrape_page(page, url, filename):

    print(f"\nScraping {url}")

    try:

        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=15000
        )

        await page.wait_for_timeout(5000)

        text = await page.locator("body").inner_text()

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(text)

        print(f"Saved {filename}")

    except Exception as e:

        print(f"Failed {url}: {e}")

async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        context = await browser.new_context(
            storage_state="auth.json"
        )

        page = await context.new_page()

        for path in PAGES:

            filename = (
                "kb_" +
                path.replace("/", "")
                .replace("-", "_")
                + ".txt"
            )

            await scrape_page(
                page,
                BASE_URL + path,
                filename
            )

        print("\nALL DONE")

        await browser.close()

asyncio.run(main())