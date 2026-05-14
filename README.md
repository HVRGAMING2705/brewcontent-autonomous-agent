# BrewContent Autonomous Knowledge Agent

A ChatGPT-style browser app that automatically searches, scrapes, transforms,
embeds and answers questions about BrewContent using your existing infrastructure.

---

## Architecture

```
User Question
    │
    ▼
[Retriever] ─── Supabase pgvector search
    │
    ├─ score ≥ 0.55 ──► [Answerer] ──► Response
    │
    └─ score < 0.55
          │
          ▼
     [Scraper] ── Playwright + auth.json ──► BrewContent pages
          │
          ▼
    [Transformer] ── Ollama llama3.2:1b ──► KB articles
          │
          ├──► [NotionSync] ── Notion API
          │
          ├──► [Embedder] ── all-MiniLM-L6-v2
          │
          ├──► [Retriever.store] ── Supabase
          │
          └──► [Retriever.search] ──► [Answerer] ──► Response
```

---

## Prerequisites (already done per your setup)

- ✅ Python venv at `C:\Users\VikranthReddyCloudan\Desktop\crawl4ai-project\venv`
- ✅ Supabase project with pgvector + kb_chunks + match_kb_chunks RPC
- ✅ Notion database with "KB Article" and "Source URL" properties
- ✅ Ollama running with `llama3.2:1b`
- ✅ Playwright + Chromium installed
- ✅ `auth.json` with BrewContent session
- ✅ `.env` file at project root

---

## Folder Structure

```
C:\Users\VikranthReddyCloudan\Desktop\crawl4ai-project\
├── .env                          ← existing (reused)
├── auth.json                     ← existing (reused by scraper)
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   └── config.py
│   │   └── tools/
│   │       ├── retriever.py
│   │       ├── scraper.py
│   │       ├── transformer.py
│   │       ├── notion_sync.py
│   │       ├── embedder.py
│   │       ├── answerer.py
│   │       └── orchestrator.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── package.json
│   ├── next.config.js
│   └── tsconfig.json
└── supabase_setup.sql
```

---

## Step 1 — Supabase (if not already done)

Open your Supabase SQL Editor and run `supabase_setup.sql`.
Skip if `kb_chunks` table and `match_kb_chunks` RPC already exist.

---

## Step 2 — Backend setup

Open PowerShell:

```powershell
# Navigate to project root (venv is here)
cd C:\Users\VikranthReddyCloudan\Desktop\crawl4ai-project

# Activate existing venv
.\venv\Scripts\Activate.ps1

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install Playwright Chromium (if not already done for this venv)
python -m playwright install chromium

# Start backend (from inside backend/ folder so .env resolves correctly)
uvicorn app.main:app --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Test it:
```powershell
curl http://127.0.0.1:8000/health
```

---

## Step 3 — Frontend setup

Open a second PowerShell window:

```powershell
cd C:\Users\VikranthReddyCloudan\Desktop\crawl4ai-project\frontend
npm install
npm run dev
```

Open browser at: **http://localhost:3000**

---

## Step 4 — .env must contain

Your existing `.env` at the project root needs these keys:

```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-service-role-key
NOTION_TOKEN=secret_xxx
NOTION_DATABASE_ID=your-database-id
OLLAMA_MODEL=llama3.2:1b
BREW_BASE_URL=https://app.brewcontent.ai
```

The backend reads `.env` from the working directory. Always run uvicorn
from inside the `backend/` folder.

---

## How it works

1. You type a question in the chat UI
2. Frontend POSTs to `http://127.0.0.1:8000/chat`
3. Backend embeds your question with all-MiniLM-L6-v2
4. Supabase RPC searches pgvector for matching chunks
5. **If top score ≥ 0.55** → answer immediately from KB
6. **If score < 0.55** → determines relevant BrewContent pages from question keywords
7. Playwright opens those pages using your `auth.json` session
8. Ollama transforms raw HTML text into clean KB articles
9. Articles are saved to Notion (errors are caught, won't crash the app)
10. Articles are embedded and stored in Supabase
11. KB is searched again with the new knowledge
12. Ollama generates a final answer
13. Response returns: `answer` + `sources` + `activity` log

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Liveness check |
| GET | /kb/status | KB chunk count |
| POST | /chat | Main agent endpoint |

### POST /chat

Request:
```json
{ "message": "How do I create an Instagram campaign?" }
```

Response:
```json
{
  "answer": "To create an Instagram campaign in BrewContent...",
  "sources": [
    { "title": "Campaign Builder", "url": "https://...", "score": 0.82 }
  ],
  "activity": [
    "🔍 Searching knowledge base…",
    "⚠️ KB score too low (0.12). Scraping: /campaign",
    "🕷️ Scraping BrewContent pages…",
    "✍️ Transforming: Campaign Builder",
    "📓 Saved to Notion: Campaign Builder",
    "💾 Stored in Supabase: Campaign Builder",
    "💬 Generating answer…",
    "✅ Done."
  ]
}
```

---

## Troubleshooting

**Ollama not responding**
- Make sure Ollama is running: `ollama serve`
- Check model is pulled: `ollama pull llama3.2:1b`

**Playwright fails to scrape**
- BrewContent session may have expired → re-run your `save_login.py`
- Check `auth.json` is at the project root

**Supabase embedding errors**
- Confirm the vector(384) column exists
- The `url` column has a UNIQUE constraint for upserts to work

**Notion sync fails**
- This is non-fatal — the agent will log the error and continue
- Check `NOTION_TOKEN` and `NOTION_DATABASE_ID` in `.env`

**Frontend shows "Cannot reach backend"**
- Make sure backend is running on port 8000
- CORS is open (`allow_origins=["*"]`) so no browser blocks

---

## Notes

- The scraper uses `auth.json` at the **project root** automatically
- Notion errors are caught and logged to `activity` — they never crash the app
- The score threshold is `0.55` (in `orchestrator.py`) — tune as needed
- Embedding model downloads once on first run (~90MB)
