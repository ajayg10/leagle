# Leagle

**AI compliance intelligence system**

Leagle combines semantic search, document ingestion, and LLM-powered regulatory impact analysis to help organizations stay audit-ready, reduce manual review overhead, and accelerate policy alignment across regulations and internal controls.

---

## The Problem

New regulations appear constantly across privacy, security, finance, and industry-specific frameworks. Manual review is slow, fragmented, and prone to missing cross-policy dependencies.

Many tools still rely on keyword matching, which fails to connect legal intent across phrasing like "data retention" and "record keeping timelines." Leagle solves this by understanding compliance meaning through embeddings and contextual analysis.

---

## What Leagle Does

### 1. Semantic Search for Regulations and Policies

Regulations, policies, and legal documents are converted into vector embeddings and stored in **Qdrant**. Natural language queries return the most relevant content by meaning, not just keyword overlap.

### 2. Automated Policy and Regulation Ingestion

Leagle ingests content from PDFs, manual uploads, and external feeds. It can process policy PDFs directly and sync official legislative sources across multiple jurisdictions.

### 3. Retrieval-Augmented Impact Analysis

Leagle uses a RAG pipeline to analyze regulation-policy relationships with structured findings, compliance gaps, risk labels, and remediation guidance. This includes full regulation impact analysis and policy compliance checks.

### 4. Advanced Risk Visualization

A new dual-mode heatmap experience combines an interactive departmental risk matrix with a global 2D/3D hotspot map. Users can drill into categories, view jurisdiction-specific risk clusters, and explore live risk signals across countries.

### 5. Real-Time Alerts and Monitoring

The system emits alerts for new high-risk findings and provides a WebSocket stream for live updates, enabling compliance teams to stay informed without polling the backend.

---

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Next.js    │────▶│   FastAPI     │────▶│     Qdrant       │
│   Frontend   │◀────│   Backend     │◀────│   Vector DB      │
│  (React 19)  │     │  + Socket.IO  │     │  (Embeddings)    │
└──────────────┘     └──────┬───────┘     └──────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
              ┌─────▼─────┐  ┌─────▼─────┐
              │ PostgreSQL │  │   Redis   │
              │  (Models)  │  │  (Cache)  │
              └───────────┘  └────────────┘
```

**Backend** — FastAPI with async SQLAlchemy, Socket.IO for real-time alerts, and LangChain for RAG.

**Vector DB** — Qdrant stores chunked embedding vectors for regulations and policies.

**LLM Layer** — Flexible provider configuration supports Gemini, Groq, and OpenAI.

**Risk Scoring** — Hybrid local scoring augmented by optional ML models.

**Frontend** — Next.js 16, React 19, Tailwind CSS, Zustand, React Query, and Socket.IO.

---

## Features

- Semantic search across regulations, policies, and legal documents
- Retrieval-augmented compliance Q&A with source citations
- Full RAG impact analysis between regulations and policies
- Automated policy compliance checks and impact mapping
- PDF ingestion pipeline with text extraction, chunking, embedding, and indexing
- Dual-mode risk visualization: departmental matrix + global 2D/3D hotspot map
- Real-time alerts via WebSockets and alert acknowledgment
- Multi-jurisdiction sync across 17+ country-specific legislative feeds
- Hybrid risk scoring with dynamic risk intensity and heatmap mapping
- Secure public API support with institutional neural retrieval endpoints
- Continuous dataset seeding and regulatory feed automation
- Support for Gemini, Groq, and OpenAI LLM providers

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, Tailwind CSS v4, Zustand, React Query, Socket.IO Client |
| Backend | FastAPI, SQLAlchemy (async), Socket.IO, LangChain, Pydantic |
| Vector DB | Qdrant |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| AI/ML | Sentence Transformers, LangChain, Gemini / Groq / OpenAI |
| Infra | Docker Compose |

---

## Data and Auto-Update

Leagle ships with a broad set of seed datasets and an automated ingestion pipeline:

- `backend/scripts/seed_datasets.py` populates Qdrant with SEC Form 10-K content, GDPR and DPDP regulatory benchmarks, LexGLUE legal reference data, GDPR case samples, and custom regulatory training data.
- `backend/scripts/seed_demo_data.py` provides a quick demo seed with sample regulations and internal policies for local testing.
- `backend/scripts/seed_large_dataset.py` ingests larger legal datasets and can be used to expand the vector store from curated sources.
- `backend/scripts/seed_compliance_engine.py` builds the compliance engine from policies and regulations and triggers auto-impact data generation.
- `backend/scripts/seed_uk_manual.py` loads UK legislative samples and manual sync content.

The backend also includes sync and maintenance utilities that help keep the vector store aligned with incoming data:

- `backend/services/sync_manager.py` coordinates global synchronization across jurisdiction-specific legislative services.
- `backend/scripts/verify_syncs.py` validates jurisdictional sync services and ingests new regulations from supported feeds.
- `backend/scripts/migrate_qdrant.py` migrates and refreshes Qdrant points when the schema or collection needs updating.

Leagle tracks jurisdiction metadata for all documents so that regulations can be searched, analyzed, and deduplicated by country or region. Its Qdrant index stores `jurisdiction` payloads and the ingestion pipeline avoids semantic duplicate detection across different countries.

### Supported Jurisdictions

Leagle currently supports sync services for:

- United Kingdom
- United States (Federal)
- European Union
- India
- Australia
- Canada
- Germany
- France
- Japan
- China
- Russia
- Brazil
- Singapore
- South Korea
- Mexico
- South Africa
- UAE

### Auto-Update Workflow

1. New regulation documents are ingested through the API or sync services.
2. Jurisdiction-specific legislative services fetch official feeds and news sources for supported countries.
3. The ingestion pipeline chunks text, generates embeddings, and upserts vectors into Qdrant with jurisdiction metadata.
4. Policy impact analysis and heatmap data are updated automatically for newly ingested content.
5. Verification scripts such as `verify_syncs.py` can be run periodically to confirm fresh regulation syncs and keep the dataset current.

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 1. Clone and configure

```bash
git clone https://github.com/your-username/Leagle.git
cd Leagle
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://user:password@127.0.0.1/compliance_db
QDRANT_HOST=127.0.0.1
QDRANT_PORT=6333
REDIS_URL=redis://127.0.0.1:6379/0

# Choose an LLM provider and add its key
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
# Or use Groq:
# LLM_PROVIDER=groq
# GROQ_API_KEY=your-key-here
```

### 2. Start infrastructure

```bash
docker compose up -d
```

Wait for PostgreSQL, Qdrant, and Redis to become healthy:

```bash
docker ps
```

### 3. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Seed the vector database with demo content:

```bash
python scripts/seed_demo_data.py
```

Start the API server:

```bash
uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3001** in your browser.

---

## Project Structure

```
Leagle/
├── backend/
│   ├── core/              # Config, database connection
│   ├── models/            # SQLAlchemy models (Regulation, Policy, Impact, Alert)
│   ├── routers/           # API endpoints (regulations, policies, impact, alerts, rag)
│   ├── services/          # Business logic
│   │   ├── qdrant_service.py       # Vector DB operations (embed, upsert, search)
│   │   ├── rag_pipeline.py         # LangChain RAG chains (impact analysis, Q&A)
│   │   ├── risk_scorer.py          # Hybrid ML + rule-based risk scoring
│   │   ├── alert_engine.py         # Risk detection and alert generation
│   │   ├── ingestion.py            # Document parsing and chunking
│   │   ├── websocket_service.py    # Socket.IO real-time broadcasts
│   │   └── summarization_service.py
│   ├── scripts/           # Data seeding scripts
│   └── main.py            # FastAPI app + Socket.IO wrapper
│
├── frontend/
│   └── src/app/
│       ├── components/    # Dashboard, SemanticSearch, RiskHeatmap, AlertsPanel
│       ├── api/           # Axios client for backend communication
│       ├── store/         # Zustand state management
│       ├── hooks/         # Custom React hooks
│       └── page.jsx       # Main application shell
│
├── docker-compose.yml     # PostgreSQL, Qdrant, Redis
└── .env                   # Environment configuration
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/regulations` | List all monitored regulations |
| `POST` | `/api/regulations/ingest` | Upload and embed a new regulation |
| `GET` | `/api/regulations/{id}/similar` | Find semantically similar regulations |
| `GET` | `/api/policies` | List all internal policies |
| `POST` | `/api/impact/analyze` | Run impact analysis (regulation vs. policy) |
| `GET` | `/api/impact/heatmap` | Get the risk heatmap data |
| `GET` | `/api/alerts` | Get all compliance alerts |
| `POST` | `/api/rag/explain` | Semantic Q&A over the regulation knowledge base |

---

## How Impact Analysis Works

When a new regulation is ingested:

1. **Chunking** — The regulation text is split into smaller content chunks.
2. **Embedding** — Each chunk is converted to a vector using `all-MiniLM-L6-v2`.
3. **Storage** — Vectors are upserted into Qdrant with metadata like source, category, and jurisdiction.
4. **Retrieval** — The system retrieves the most relevant chunks for analysis.
5. **Analysis** — Retrieved context, regulation, and policy text are sent to the LLM with a prompt.
6. **Scoring** — The hybrid risk scorer produces a risk level.
7. **Alerting** — High-risk findings can generate real-time alerts.

The LLM returns structured JSON with impact level, affected clauses, compliance gaps, recommended actions, and deadlines.

---

## Seeded Data

Demo and production datasets include:

- **GDPR** — Article 5, 32, 33 and related EU privacy controls
- **India DPDP Act** — Data principal rights and compliance requirements
- **PCI-DSS v3.2.1** — Payment card data security controls
- **SOC 2 Type II** — Security and compliance controls for service organizations
- **SEC Form 10-K content** — Corporate compliance benchmark material
- **LexGLUE and legal case datasets** — Regulatory reference and training content for risk scoring
- Internal policy examples for Data Retention, Access Control, and Incident Response
- Curated regulation-to-policy mapping datasets

---

## About This Project

Leagle is a compliance intelligence engine designed for practical regulatory analysis and rapid adaptation. It helps teams connect regulations to policy controls, surface risks, and deliver actionable remediation guidance more quickly.

---

## Disclaimer

This system is a decision-support tool. It is not a substitute for qualified legal counsel. Always validate critical compliance decisions with domain experts.

---

## What’s Next

- Live regulatory feed ingestion and auto-update pipelines
- Multi-language embedding support
- Fine-tuned risk classification model trained on labeled compliance data
- Audit trail and certification workflow
- Role-based access control for enterprise teams
