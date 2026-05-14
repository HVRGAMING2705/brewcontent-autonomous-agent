from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

for file in Path("transformed_kb").glob("*.md"):
    content = file.read_text(encoding="utf-8")
    title = file.stem.replace("_", " ").title()

    print(f"Embedding {title}...")

    embedding = model.encode(content).tolist()

    supabase.table("kb_embeddings").insert({
        "title": title,
        "category": title,
        "content": content,
        "source_url": "https://app.brewcontent.ai",
        "embedding": embedding
    }).execute()

    print(f"Stored: {title}")

print("DONE")