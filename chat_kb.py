import os
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer
import ollama

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

question = input("\nAsk BrewContent AI: ")

query_embedding = embed_model.encode(question).tolist()

results = supabase.rpc(
    "match_kb_embeddings",
    {
        "query_embedding": query_embedding,
        "match_count": 2
    }
).execute()

context = ""

for item in results.data:
    context += f"""
TITLE: {item['title']}
CATEGORY: {item['category']}
CONTENT:
{item['content'][:1200]}
"""

prompt = f"""
You are BrewContent AI Support Assistant.

Answer only from the knowledge base below.
If the answer is not available, say:
"I don't have enough BrewContent knowledge to answer that yet."

Keep the answer short and simple.

KNOWLEDGE BASE:
{context}

USER QUESTION:
{question}

ANSWER:
"""

response = ollama.chat(
    model="llama3.2:1b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    options={
        "num_predict": 180,
        "temperature": 0.2,
        "num_ctx": 2048,
        "num_thread": 2
    }
)

print("\nAI ANSWER:\n")
print(response["message"]["content"])