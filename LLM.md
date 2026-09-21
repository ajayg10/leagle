# LLM.md — AI Compliance Management System
> **Project:** Code Wizards 2.0 — PS4 | **Team:** 3 members | **Org:** SRMIST | **Owner:** Pradeepto Pal
> **TL;DR:** A microservices RAG platform that monitors regulatory changes, maps them to internal company policies using vector similarity (Qdrant), scores risk, and generates LLM remediation recommendations. Qdrant is the core intelligence engine — not an add-on.

---

## 1. WHAT THIS SYSTEM DOES

| Problem (Before) | Solution (After) |
|---|---|
| Manual regulation tracking (days/weeks) | Automated crawler + NLP parser (minutes) |
| No semantic policy impact detection | Qdrant ANN search finds affected policies instantly |
| Reactive alerting after breaches | Proactive risk scoring before deadlines |
| Legal team bottleneck for summaries | LLM-generated plain-English summaries + actions |
| No cross-regulation linking | Vector embeddings reveal hidden thematic overlaps |

---

## 2. SYSTEM ARCHITECTURE (4 Layers)

```
LAYER 1 — UI:         Next.js 16 + React 19 + Tailwind CSS v4 | Alert Panel | Risk Heatmap | Doc Uploader
LAYER 2 — Gateway:    FastAPI (HTTP + WebSocket) | Auth | Rate Limiting | Routing
LAYER 3 — Services:   Ingestion | RAG Pipeline | Risk Scorer | Alert Engine
LAYER 4 — Data:       Qdrant (vectors) | Neon DB / PostgreSQL (structured) | Redis (cache/queue) | S3 (raw docs)
```

**Key architectural decisions:**
- `FastAPI` — async Python, auto OpenAPI docs, handles LLM I/O latency well
- `Microservices` — Ingestion, RAG, Risk Scorer, Alert Engine are independent; enables parallel development
- `Qdrant` — semantic search over all regulatory text; finds impacted policies even when zero keywords match
- `Neon DB` (serverless PostgreSQL) — source of truth for users, policies, alerts, audit logs, regulation metadata. SQLAlchemy 2.0 ORM works seamlessly.
- `Redis` — Celery job queue for async embedding + pub/sub for real-time WebSocket alerts

---

## 3. TECH STACK

### Backend (Python)
| Tool | Role |
|---|---|
| `FastAPI` | REST API + WebSockets |
| `qdrant-client` | Vector DB operations (official SDK) |
| `sentence-transformers` (`all-MiniLM-L6-v2`) | Text → 384-dim embedding vectors |
| `LangChain` | RAG orchestration, chunking, retrieval chains |
| `Google Gemini API` / `OpenAI` | LLM text generation (summaries, recommendations) |
| `SQLAlchemy` + `Alembic` | ORM + DB migrations |
| `Celery` + `Redis` | Background async embedding jobs |
| `APScheduler` | Cron-like regulation scraper scheduler |
| `BeautifulSoup4` / `httpx` | Web scraping from gov regulation sources |
| `Pydantic v2` | Type-safe API contracts |

### Frontend (JavaScript/TypeScript)
| Tool | Role |
|---|---|
| `Next.js 16` + `React 19` | Full-stack framework with server/client components |
| `Tailwind CSS v4` | Utility-first CSS framework |
| `Recharts` | Risk heatmaps, trend charts |
| `TanStack React Query` | Server state, auto-refetch |
| `Zustand` | Lightweight global state |
| `socket.io-client` | Real-time WebSocket alert notifications |
| `React-PDF` | In-browser document viewer |

---

## 4. QDRANT — CORE INTEGRATION

### Concept
Qdrant is a vector database. Text is converted to embedding vectors (lists of numbers). Qdrant stores millions of these vectors and finds top-K most similar ones to a query vector in milliseconds via Approximate Nearest Neighbour (ANN) search — enabling **semantic** (meaning-based) search rather than keyword matching.

### Data Flow

**Indexing Pipeline (offline/background):**
```
Regulation PDF → Chunker (512 tokens) → Embedder (all-MiniLM-L6-v2) → Qdrant Collection: regulations_v1
```

**Query Pipeline (real-time, <100ms):**
```
User query → Embed (same model) → Qdrant cosine similarity search → top-K chunks → LLM (Gemini/GPT) → response
```

### Setup Commands
```bash
# Run Qdrant via Docker
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# Install dependencies
pip install qdrant-client sentence-transformers langchain-community
```

### Collection Creation
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(host="localhost", port=6333)
client.create_collection(
    collection_name="regulations_v1",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
```

### Ingestion (Embed + Upsert)
```python
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct
import uuid

model = SentenceTransformer('all-MiniLM-L6-v2')

def ingest_regulation(text: str, metadata: dict):
    chunks = chunk_text(text, max_tokens=512)
    points = []
    for i, chunk in enumerate(chunks):
        vector = model.encode(chunk).tolist()
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={**metadata, "chunk_index": i, "text": chunk}
        ))
    client.upsert(collection_name="regulations_v1", points=points)
```

### Semantic Search
```python
def find_similar_regulations(query_text: str, top_k: int = 5):
    query_vector = model.encode(query_text).tolist()
    results = client.search(
        collection_name="regulations_v1",
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
    return [{"score": hit.score, "text": hit.payload["text"],
             "regulation_id": hit.payload["regulation_id"],
             "title": hit.payload["title"]} for hit in results]
```

### Filtered Search (by category)
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="regulations_v1",
    query_vector=query_vector,
    query_filter=Filter(must=[FieldCondition(key="category", match=MatchValue(value="data_privacy"))]),
    limit=5
)
```

---

## 5. DATABASE SCHEMA (Neon DB / PostgreSQL)

```sql
-- External regulatory documents
CREATE TABLE regulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source TEXT,          -- e.g. "eu.gdpr", "india.sebi"
    category TEXT,        -- "data_privacy" | "finance" | "labor"
    jurisdiction TEXT,
    effective_date DATE,
    raw_text TEXT,
    qdrant_ids TEXT[],    -- chunk IDs stored in Qdrant
    risk_level SMALLINT DEFAULT 0,  -- 0-100
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Internal company policies
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT,
    department TEXT,
    owner TEXT,
    last_review DATE,
    qdrant_ids TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Regulation → Policy impact mappings (populated by Qdrant search)
CREATE TABLE impact_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regulation_id UUID REFERENCES regulations(id),
    policy_id UUID REFERENCES policies(id),
    similarity FLOAT,           -- cosine similarity score from Qdrant (0–1)
    impact_level TEXT,          -- "HIGH" | "MEDIUM" | "LOW"
    llm_summary TEXT,           -- AI-generated explanation of impact
    status TEXT DEFAULT 'OPEN', -- "OPEN" | "RESOLVED" | "IGNORED"
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alert log
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regulation_id UUID REFERENCES regulations(id),
    severity TEXT,
    message TEXT,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT FALSE
);
```

---

## 6. BACKEND — PROJECT STRUCTURE

```
backend/
├── main.py                    # FastAPI app entry point
├── core/
│   ├── config.py              # Env vars (Qdrant URL, DB URL, LLM key)
│   └── database.py            # SQLAlchemy setup
├── services/
│   ├── ingestion.py           # Parse + chunk + embed + upsert to Qdrant
│   ├── rag_pipeline.py        # Retrieve from Qdrant + LLM generation
│   ├── risk_scorer.py         # ML classifier for risk level
│   └── alert_engine.py        # Detect new impacts, send alerts
├── routers/
│   ├── regulations.py         # CRUD + ingest endpoints
│   ├── policies.py            # Company policy management
│   ├── impact.py              # Impact analysis endpoints
│   └── alerts.py              # Alert management
├── models/
│   ├── regulation.py          # SQLAlchemy + Pydantic models
│   └── policy.py
└── tasks/
    └── celery_tasks.py        # Background embedding jobs
```

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/regulations/ingest` | Upload regulation text → embed → store in Qdrant + Neon DB |
| `POST` | `/api/impact/analyze` | Given `regulation_id`, find all impacted policies via Qdrant |
| `GET` | `/api/regulations/` | List all regulations with risk scores |
| `GET` | `/api/alerts/` | Fetch recent alerts (supports WebSocket too) |
| `POST` | `/api/policies/upload` | Upload company policy PDF → parse → embed → store |
| `GET` | `/api/impact/heatmap` | Returns risk matrix data for frontend chart |
| `POST` | `/api/rag/explain` | Natural language question → RAG answer from regulations |
| `GET` | `/api/regulations/{id}/similar` | Top-K similar regulations from Qdrant |

### RAG Pipeline Core
```python
# services/rag_pipeline.py
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Qdrant as LCQdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai

embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
qdrant_store = LCQdrant(client=qdrant_client, collection_name="regulations_v1", embeddings=embeddings)

def analyze_regulation_impact(regulation_text: str, company_policy: str) -> dict:
    relevant_chunks = qdrant_store.similarity_search_with_score(regulation_text, k=5)
    context = "\n\n".join([doc.page_content for doc, _ in relevant_chunks])

    prompt = f"""You are a compliance expert. Analyze whether this new regulation
impacts the given company policy.

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{context}

NEW REGULATION:
{regulation_text}

COMPANY POLICY:
{company_policy}

Provide:
1. Impact level (HIGH/MEDIUM/LOW)
2. Specific gaps in the policy
3. Recommended actions (numbered list)
4. Compliance deadline if mentioned"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return {
        "analysis": response.text,
        "source_chunks": [doc.page_content[:200] for doc, _ in relevant_chunks],
        "similarity_scores": [score for _, score in relevant_chunks]
    }
```

---

## 7. FRONTEND — KEY SCREENS

| Screen | Description |
|---|---|
| **Overview Dashboard** | Risk summary cards (HIGH/MEDIUM/LOW counts), recent alerts feed, 7-day ingestion trend (Recharts LineChart) |
| **Regulation Ingestion** | Drag-and-drop PDF or paste text; live progress: Parsing → Chunking → Embedding → Storing → Analyzing (EventSource streaming) |
| **Risk Heatmap** | 2D grid: Departments (rows) × Risk Categories (columns); color intensity = risk score; click cell → affected policies |
| **Semantic Search** | Qdrant-powered search bar; returns semantically relevant results with similarity scores as progress bars |
| **Impact Analysis** | Per-regulation: ranked list of affected policies by Qdrant similarity score + LLM explanation + "Mark Resolved" button |
| **Alerts Panel** | Real-time WebSocket feed; color-coded by severity; filter by dept/type; acknowledge button updates Neon DB |

### Frontend Bootstrap
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install tailwindcss @tailwindcss/vite recharts @tanstack/react-query zustand socket.io-client axios lucide-react react-dropzone
```

---

## 8. DATASETS FOR DEMO

| Dataset | Source | Used For |
|---|---|---|
| GDPR Full Text | eur-lex.europa.eu / Kaggle | Privacy regulations — embed as Qdrant points |
| US Code of Federal Regulations (CFR) | Kaggle: "us cfr dataset" | 1000+ rules corpus |
| Financial Regulations (FINRA, SEC) | Kaggle: "financial regulations nlp" | Finance category |
| Legal Contracts NLP | Kaggle: "legal contracts dataset" | Company policy examples |
| CUAD | HuggingFace: cuad | Policy clause extraction |
| IndiaCode / data.gov.in | data.gov.in | Indian regulations |

**Demo seeding target:** ≥50 regulation chunks across 3 categories (`data_privacy`, `finance`, `labor`) for meaningful semantic search results and a non-trivial risk heatmap.

---

## 9. TEAM & SPRINT PLAN

| Person | Role | Owns |
|---|---|---|
| Person 1 (Pradeepto) | Backend + AI Lead | FastAPI, Qdrant integration, RAG pipeline, risk scorer, seed script |
| Person 2 | Backend + DB | Neon DB setup, SQLAlchemy models, ingestion service, Celery, scrapers |
| Person 3 | Frontend Lead | React dashboard, Tailwind UI, Recharts heatmap, WebSocket alerts, demo flow |

| Phase | Hours | Tasks |
|---|---|---|
| Foundation | 0–4 | Repo, Docker Compose (Qdrant + Redis), Neon DB setup, FastAPI skeleton, Vite setup, DB migrations |
| Core AI | 4–10 | Ingestion + Qdrant upsert, RAG with Gemini, risk scorer, seed script |
| Features | 10–17 | Impact analysis endpoint, alert engine, React screens, WebSocket alerts |
| Polish | 17–22 | Risk heatmap, LLM recommendation UI, mobile responsiveness, error handling |
| Demo Prep | 22–24 | Rehearse demo, 3 live scenarios, README + architecture diagram, 30-sec backup video |

---

## 10. DEMO SCRIPT (5 min)

| Time | Step | Action |
|---|---|---|
| 0:00–0:30 | Hook | Stat: "GDPR fines in 2024 totalled €1.3B. Show the problem." |
| 0:30–1:30 | Ingest | Paste real GDPR article → watch chunk/embed/Qdrant store in real time |
| 1:30–2:30 | Semantic Search | Type "data breach notification deadline" → show results without exact keyword matches; highlight similarity scores |
| 2:30–3:30 | Impact Analysis | Select regulation → "Analyze Impact" → ranked policy list + LLM explanation of WHY each is affected |
| 3:30–4:30 | Risk Heatmap | Navigate heatmap → click HIGH risk cell → drill-down + auto-generated alert |
| 4:30–5:00 | Qdrant Pitch | "This wouldn't be possible with a traditional database. Qdrant finds regulatory relationships based on *meaning*, not keywords." |

---

## 11. JUDGING CRITERIA MAP

| Criterion | How It's Addressed |
|---|---|
| AI Implementation Depth | Qdrant ANN + sentence-transformers + LLM RAG + ML risk classifier = 4 distinct AI components |
| Originality | Semantic vector search for regulatory impact; not another chatbot |
| Real-World Usability | Every company needs compliance tooling; polished React dashboard |
| Scalability | Qdrant scales to millions of vectors; async FastAPI; Celery background jobs |
| Documentation | This file + README with architecture diagram |
| Qdrant Special Prize | Qdrant IS the core feature — entire semantic search and impact analysis depends on it |

---

## 12. CRITICAL IMPLEMENTATION NOTES FOR LLMs

- **Embedding model is fixed:** Always use `all-MiniLM-L6-v2` (384 dimensions) consistently across ingestion and query pipelines. Switching models invalidates all stored vectors.
- **Chunk size:** 512 tokens per chunk. Store `chunk_index` and original `text` in Qdrant payload for retrieval.
- **IDs:** Use `uuid4` strings for Qdrant point IDs; store them back in PostgreSQL `qdrant_ids[]` column for cross-referencing.
- **LLM:** Default to `gemini-1.5-flash` (free tier) for hackathon. Swap to `gpt-4o-mini` via env var.
- **Similarity threshold:** Cosine similarity > 0.75 → HIGH impact; 0.5–0.75 → MEDIUM; < 0.5 → LOW.
- **Qdrant ports:** REST API on `6333`, gRPC on `6334`. Python client defaults to REST.
- **Database hosting:** Use Neon free tier (https://console.neon.tech) for serverless PostgreSQL or Supabase for PostgreSQL hosting during hackathon.
- **README must mention "Qdrant" in the first paragraph** and include a section titled "Qdrant Integration" for judges scanning for the special prize.