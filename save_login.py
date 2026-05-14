import asyncio
from playwright.async_api import async_playwright

async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        context = await browser.new_context()

        page = await context.new_page()

        await page.goto("https://app.brewcontent.ai")

        print("\nLOGIN MANUALLY.")
        print("After FULL login + dashboard loads press ENTER.\n")

        input()

        await context.storage_state(
            path="auth.json"
        )

        print("Saved login session to auth.json")

        await browser.close()

asyncio.run(main())