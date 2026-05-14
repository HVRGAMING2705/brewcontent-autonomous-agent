import os
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))
database_id = os.getenv("NOTION_DATABASE_ID")

CATEGORY_MAP = {
    "home": "Home",
    "projects": "Projects",
    "templates": "Templates",
    "audience": "Audience",
    "brand_kit": "BrandKit",
    "flows": "AI Video",
    "campaign": "Campaign",
    "schedule": "Scheduler",
    "billing": "Billing",
}

SOURCE_MAP = {
    "home": "https://app.brewcontent.ai/home",
    "projects": "https://app.brewcontent.ai/projects",
    "templates": "https://app.brewcontent.ai/templates",
    "audience": "https://app.brewcontent.ai/audience",
    "brand_kit": "https://app.brewcontent.ai/brand-kit",
    "flows": "https://app.brewcontent.ai/flows",
    "campaign": "https://app.brewcontent.ai/campaign",
    "schedule": "https://app.brewcontent.ai/schedule",
    "billing": "https://app.brewcontent.ai/billing",
}

def chunk_text(text, size=1800):
    return [text[i:i + size] for i in range(0, len(text), size)]

for file in Path("transformed_kb").glob("*.md"):
    key = file.stem
    title = key.replace("_", " ").title()
    content = file.read_text(encoding="utf-8")
    category = CATEGORY_MAP.get(key, "Product")
    source_url = SOURCE_MAP.get(key, "https://app.brewcontent.ai")

    children = []

    for chunk in chunk_text(content):
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": chunk}
                    }
                ]
            }
        })

    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "KB Articles": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Category": {
                "select": {
                    "name": category
                }
            },
            "Source URL": {
                "url": source_url
            },
            "Status": {
                "status": {
                    "name": "Not started"
                }
            },
            "Last Crawled": {
                "date": {
                    "start": datetime.now(timezone.utc).isoformat()
                }
            },
            "Embedding Synced": {
                "checkbox": False
            },
            "Product Area": {
                "select": {
                    "name": category
                }
            }
        },
        children=children
    )

    print(f"Pushed to Notion: {title}")

print("Done pushing all KB articles to Notion.")