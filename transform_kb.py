from pathlib import Path

PAGE_MAP = {
    "kb_home.txt": {
        "title": "Home Dashboard",
        "category": "Home",
        "source_url": "https://app.brewcontent.ai/home",
    },
    "kb_projects.txt": {
        "title": "Projects",
        "category": "Projects",
        "source_url": "https://app.brewcontent.ai/projects",
    },
    "kb_templates.txt": {
        "title": "Templates",
        "category": "Templates",
        "source_url": "https://app.brewcontent.ai/templates",
    },
    "kb_audience.txt": {
        "title": "Audience Configuration",
        "category": "Audience",
        "source_url": "https://app.brewcontent.ai/audience",
    },
    "kb_brand_kit.txt": {
        "title": "Brand Kit",
        "category": "BrandKit",
        "source_url": "https://app.brewcontent.ai/brand-kit",
    },
    "kb_flows.txt": {
        "title": "AI Video Flows",
        "category": "AI Video",
        "source_url": "https://app.brewcontent.ai/flows",
    },
    "kb_campaign.txt": {
        "title": "Campaign Generator",
        "category": "Campaign",
        "source_url": "https://app.brewcontent.ai/campaign",
    },
    "kb_schedule.txt": {
        "title": "Scheduler",
        "category": "Scheduler",
        "source_url": "https://app.brewcontent.ai/schedule",
    },
    "kb_billing.txt": {
        "title": "Billing and Usage",
        "category": "Billing",
        "source_url": "https://app.brewcontent.ai/billing",
    },
}

def make_article(title, category, source_url, raw):
    return f"""# {title}

Category: {category}
Source URL: {source_url}

## What this page is for

This page is part of the BrewContent product. It helps users work with the {category} area of the platform.

## User intent

Users may come here to understand how to use {title}, what actions are available, and what options they can configure.

## Available UI elements and product information

{raw}

## Help article draft

### How do I use {title} in BrewContent?

1. Open BrewContent.
2. Go to the {title} section from the sidebar.
3. Review the available options on the page.
4. Use the visible buttons, forms, or actions to complete your task.
5. If the page shows an empty state, create the required item first.

## Possible user questions

- What is {title} used for?
- How do I use {title}?
- Why is this page empty?
- What should I click next?
- What plan or credits are needed for this feature?

## LLM retrieval notes

Only answer questions about this feature using the information above. If the answer is not present, say that the information is not available in the BrewContent knowledge base.
"""

Path("transformed_kb").mkdir(exist_ok=True)

for filename, meta in PAGE_MAP.items():
    path = Path(filename)

    if not path.exists():
        print(f"Missing {filename}")
        continue

    raw = path.read_text(encoding="utf-8").strip()

    article = make_article(
        meta["title"],
        meta["category"],
        meta["source_url"],
        raw
    )

    output = Path("transformed_kb") / filename.replace("kb_", "").replace(".txt", ".md")
    output.write_text(article, encoding="utf-8")

    print(f"Created {output}")