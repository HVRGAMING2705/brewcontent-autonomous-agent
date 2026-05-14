import os
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

question = input("\nAsk BrewContent Question: ")

query_embedding = model.encode(
    question
).tolist()

response = supabase.rpc(
    "match_kb_embeddings",
    {
        "query_embedding": query_embedding,
        "match_count": 3
    }
).execute()

print("\nTOP MATCHES:\n")

for match in response.data:

    print("=" * 80)

    print(f"\nTITLE: {match['title']}")

    print(f"\nCATEGORY: {match['category']}")

    print(f"\nSIMILARITY: {match['similarity']}")

    print("\nCONTENT:\n")

    print(match["content"][:1000])

    print("\n")