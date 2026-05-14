from pathlib import Path

files = sorted(Path(".").glob("kb_*.txt"))

with open("product_knowledge_base.md", "w", encoding="utf-8") as out:
    out.write("# BrewContent Product Knowledge Base\n\n")

    for file in files:
        title = file.stem.replace("kb_", "").replace("_", " ").title()
        content = file.read_text(encoding="utf-8").strip()

        out.write(f"## {title}\n\n")
        out.write(content)
        out.write("\n\n---\n\n")

print("Created product_knowledge_base.md")