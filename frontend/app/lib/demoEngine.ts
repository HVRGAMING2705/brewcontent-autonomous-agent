// ── BrewContent demo engine ─────────────────────────────────────────────────
// Client-side replacement for the FastAPI backend (which is not deployed).
// Loads the bundled knowledge-base text files and answers with simple
// keyword retrieval. Same response shapes the UI already expects.

export interface DemoSource {
  title: string;
  url: string;
  score: number;
}

export interface DemoAnswer {
  answer: string;
  sources: DemoSource[];
  activity: string[];
}

export interface DemoStatus {
  status: string;
  chunks_found: number;
  message: string;
}

const KB_FILES = [
  "kb_home.txt",
  "kb_projects.txt",
  "kb_templates.txt",
  "kb_audience.txt",
  "kb_brand_kit.txt",
  "kb_campaign.txt",
  "kb_schedule.txt",
  "kb_billing.txt",
  "kb_flows.txt",
];

interface Chunk {
  file: string;
  title: string;
  text: string;
}

let chunkCache: Chunk[] | null = null;

const STOP = new Set(
  "the,a,an,and,or,of,to,in,on,for,with,is,are,was,were,it,its,this,that,these,those,by,from,as,at,be,have,has,had,you,your,we,our,they,their,he,she,his,her,not,but,what,when,where,which,who,whom,how,why,can,could,should,would,do,does,did,will,i,me,my,please,tell,give,show,about,into,over,under,more,most,than,then,so,such,no,yes,if,all,any,each,other,some,there,here".split(",")
);

function prettyTitle(file: string): string {
  return file
    .replace(/^kb_/, "")
    .replace(/\.txt$/, "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function tokenize(s: string): string[] {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2 && !STOP.has(w));
}

async function loadChunks(): Promise<Chunk[]> {
  if (chunkCache) return chunkCache;
  const chunks: Chunk[] = [];
  for (const file of KB_FILES) {
    try {
      const res = await fetch(`/kb/${file}`);
      if (!res.ok) continue;
      const text = await res.text();
      const title = prettyTitle(file);
      // Split into chunks on blank lines; drop stubs.
      const parts = text.split(/\n\s*\n/).map((p) => p.trim()).filter((p) => p.length > 24);
      for (const part of parts) chunks.push({ file, title, text: part });
    } catch {
      /* file missing — skip */
    }
  }
  chunkCache = chunks;
  return chunks;
}

export async function getDemoStatus(): Promise<DemoStatus> {
  const chunks = await loadChunks();
  if (chunks.length === 0) {
    return {
      status: "error",
      chunks_found: 0,
      message: "Knowledge base files could not be loaded.",
    };
  }
  return {
    status: "ready",
    chunks_found: chunks.length,
    message: `Demo mode: ${chunks.length} knowledge chunks loaded locally — no backend required.`,
  };
}

export async function demoChat(message: string): Promise<DemoAnswer> {
  const chunks = await loadChunks();
  const activity: string[] = [];
  activity.push(`Parsed query (${tokenize(message).length} keywords)`);
  activity.push(`Searching ${chunks.length} local knowledge chunks`);

  const keywords = tokenize(message);
  const scored = chunks
    .map((c) => {
      const hay = c.text.toLowerCase();
      let score = 0;
      for (const k of keywords) {
        const hits = hay.split(k).length - 1;
        // Title matches weigh more.
        const titleHits = c.title.toLowerCase().split(k).length - 1;
        score += hits + titleHits * 3;
      }
      return { c, score };
    })
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);

  activity.push(
    scored.length > 0
      ? `Ranked ${scored.length} relevant chunks by keyword overlap`
      : "No strong keyword match — listing available topics"
  );

  if (scored.length === 0) {
    const topics = [...new Set(chunks.map((c) => c.title))].join(", ");
    return {
      answer:
        `I couldn't find a direct match for that in the BrewContent knowledge base. ` +
        `Try asking about one of these topics: ${topics}.`,
      sources: [],
      activity: [...activity, "Composed guidance answer"],
    };
  }

  const best = scored[0];
  const lines = scored.map((s) => s.c.text);
  const answer =
    `Based on the BrewContent knowledge base (${best.c.title}):\n\n` +
    lines.join("\n\n— — —\n\n");

  const sources: DemoSource[] = scored.map((s) => ({
    title: s.c.title,
    url: `/kb/${s.c.file}`,
    score: Math.round((s.score / (best.score || 1)) * 100) / 100,
  }));

  activity.push("Composed answer from top chunks");
  return { answer, sources, activity };
}
