-- ============================================================
-- BrewContent Knowledge Agent — Supabase Setup
-- Run this in your Supabase SQL Editor
-- ============================================================

-- 1. Enable pgvector extension
create extension if not exists vector;

-- 2. Create kb_chunks table
create table if not exists kb_chunks (
  id          bigint generated always as identity primary key,
  title       text,
  url         text unique,
  content     text,
  embedding   vector(384),
  created_at  timestamptz default now()
);

-- 3. Create HNSW index for fast ANN search (recommended over ivfflat for small datasets)
create index if not exists kb_chunks_embedding_idx
  on kb_chunks
  using hnsw (embedding vector_cosine_ops);

-- 4. Create the match_kb_chunks RPC
create or replace function match_kb_chunks(
  query_embedding vector(384),
  match_count     int default 5
)
returns table (
  id      bigint,
  title   text,
  url     text,
  content text,
  score   float
)
language sql stable
as $$
  select
    id,
    title,
    url,
    content,
    1 - (embedding <=> query_embedding) as score
  from kb_chunks
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- 5. Disable RLS for local development
--    (Re-enable with proper policies before going to production)
alter table kb_chunks disable row level security;

-- ============================================================
-- PRODUCTION NOTE:
-- When ready, enable RLS and add policies:
--
-- alter table kb_chunks enable row level security;
--
-- create policy "Allow service role full access"
--   on kb_chunks
--   for all
--   using (true)
--   with check (true);
-- ============================================================
