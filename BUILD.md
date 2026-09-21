# BUILD.md — AI Compliance Management System
## Complete Step-by-Step Implementation Guide for LLMs

> **READ THIS FIRST — HOW TO USE THIS FILE**
> This file is designed so that any LLM can build this project from scratch without losing context.
> Each section ends with a `✅ CHECKPOINT` — verify it before moving to the next section.
> Never skip a checkpoint. If it fails, fix it before continuing.
> Pinned package versions are tested and correct. Do not upgrade without verifying compatibility.

---

## CONTEXT SNAPSHOT (Read at the start of every new session)

```
Project:    AI Compliance Management System
Stack:      Python 3.11 / FastAPI 0.115 / Qdrant 1.9 / Neon DB (Serverless PostgreSQL) / Next.js 16 / React 19
AI:         sentence-transformers (all-MiniLM-L6-v2) + LangChain 0.3 + Google Gemini API
Purpose:    Ingest regulations → embed → store in Qdrant → find impacted policies → LLM analysis
Qdrant role: Core intelligence engine (NOT an add-on). All semantic search depends on it.
LLM role:   Summarization + remediation recommendations (Gemini 1.5 Flash, free tier)
DB split:   Qdrant = unstructured vector search | Neon DB (serverless PostgreSQL) = structured relational data
```

---

## FULL REPO STRUCTURE (Build this first, reference always)

```
compliance-system/
├── docker-compose.yml
├── .env                          ← never commit this
├── .env.example
├── README.md
├── LLM.md
├── BUILD.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/             ← auto-generated migration files
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── regulation.py
│   │   ├── policy.py
│   │   ├── impact.py
│   │   └── alert.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── regulations.py
│   │   ├── policies.py
│   │   ├── impact.py
│   │   ├── alerts.py
│   │   └── rag.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── rag_pipeline.py
│   │   ├── risk_scorer.py
│   │   └── alert_engine.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── celery_tasks.py
│   └── scripts/
│       └── seed_qdrant.py
│
├── frontend/
│   ├── package.json
│   ├── next.config.mjs
│   ├── jsconfig.json
│   ├── postcss.config.mjs
│   ├── eslint.config.mjs
│   ├── public/
│   └── src/
│       └── app/
│           ├── globals.css
│           ├── layout.js
│           ├── page.js
│           ├── components/
│           │   ├── Dashboard.tsx
│           │   ├── RegulationIngest.tsx
│           │   ├── RiskHeatmap.tsx
│           │   ├── SemanticSearch.tsx
│           │   ├── ImpactAnalysis.tsx
│           │   └── AlertsPanel.tsx
│           ├── hooks/
│           │   └── useWebSocket.ts
│           └── api/
│
└── ml/
    ├── requirements_ml.txt
    ├── label_dataset.py
    ├── train_risk_scorer.py
    └── evaluate_model.py
```

---

## PHASE 0 — PREREQUISITES

### Required software
```bash
# Verify these are installed before starting
python --version        # must be 3.11+
node --version          # must be 20+
docker --version        # must be 24+
docker compose version  # must be 2.x (note: no hyphen in v2)
```

### Environment file — create `.env` at project root
```env
# .env — copy this, fill in real values

# Neon DB (Serverless PostgreSQL)
# Get your connection string from https://console.neon.tech
# Format: postgresql+asyncpg://user:password@region.neon.tech/dbname?sslmode=require
DATABASE_URL=postgresql+asyncpg://your_neon_user:your_neon_password@your-region.neon.tech/compliance_db?sslmode=require

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=regulations_v1

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM — get free key at https://aistudio.google.com
GEMINI_API_KEY=your_gemini_api_key_here

# App
SECRET_KEY=your_random_secret_key_here_min_32_chars
ENVIRONMENT=development
```

Also create `.env.example` (same content but with placeholder values — safe to commit).

> **Neon Setup:**
> 1. Sign up free at https://console.neon.tech
> 2. Create a new project and database
> 3. Copy the "Connection string" with `?sslmode=require` suffix
> 4. Paste into `DATABASE_URL` in `.env`

---

## PHASE 1 — INFRASTRUCTURE (Docker Compose)

### `docker-compose.yml`
```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.9.1        # pinned version
    container_name: compliance_qdrant
    ports:
      - "6333:6333"                    # REST API
      - "6334:6334"                    # gRPC
    volumes:
      - qdrant_storage:/qdrant/storage
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:6333/readyz || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5

  # PostgreSQL is now hosted on Neon (serverless) — no local container needed
  # Your DATABASE_URL will be provided by Neon console and stored in .env

  redis:
    image: redis:7-alpine
    container_name: compliance_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  qdrant_storage:
  redis_data:
```

### Start infrastructure
```bash
docker compose up -d
docker compose ps      # Qdrant and Redis should show "healthy" after ~30 seconds
```

### ✅ CHECKPOINT 1
```bash
curl http://localhost:6333/readyz          # should return {"result": "ok"}
curl http://localhost:6333/collections     # should return {"result": {"collections": []}}
redis-cli ping                             # should return PONG
# For Neon: verify DATABASE_URL is set in .env and starts with postgresql+asyncpg://
echo $DATABASE_URL
```

---

## PHASE 2 — BACKEND SETUP

### `backend/requirements.txt` — pinned versions
```text
# Web framework
fastapi==0.115.4
uvicorn[standard]==0.32.1
python-multipart==0.0.17         # for file upload endpoints

# Qdrant
qdrant-client==1.12.1            # official SDK

# Embeddings
sentence-transformers==3.3.1
torch==2.5.1                     # CPU version is fine for hackathon
numpy==1.26.4

# LangChain (split packages — this is the current structure as of 2024)
langchain==0.3.7
langchain-core==0.3.19
langchain-community==0.3.7
langchain-google-genai==2.0.5    # Gemini integration

# LLM
google-generativeai==0.8.3

# Database — SQLAlchemy 2.0 ORM + async PostgreSQL driver (works with both local PG and Neon)
sqlalchemy==2.0.36
alembic==1.14.0
asyncpg==0.30.0                  # async postgres driver (compatible with Neon)
psycopg2-binary==2.9.10          # sync driver (for alembic migrations)

# Data validation
pydantic==2.10.2
pydantic-settings==2.6.1

# Background tasks
celery==5.4.0
redis==5.2.0

# Scheduling (regulation scraper)
apscheduler==3.10.4

# Web scraping
httpx==0.28.0
beautifulsoup4==4.12.3

# PDF parsing
pypdf==5.1.0

# Utilities
python-dotenv==1.0.1
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4
```

### Install
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### `backend/core/config.py`
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database — works with both Neon (serverless PostgreSQL) and local PostgreSQL
    # Neon format: postgresql+asyncpg://user:password@region.neon.tech/dbname?sslmode=require
    database_url: str

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "regulations_v1"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    gemini_api_key: str

    # App
    secret_key: str
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

---

### `backend/core/database.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from core.config import settings

# NOTE: asyncpg requires the URL scheme to be postgresql+asyncpg://
# Works with both Neon (serverless PostgreSQL) and local PostgreSQL
# Neon tip: start with pool_size=5 for free tier (limited connections)
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_size=5,          # Neon free tier: ~20 connections total
    max_overflow=10,
    pool_pre_ping=True,   # Important for Neon: detect stale connections
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    """FastAPI dependency — injects an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    """Call this on app startup to create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

---

## PHASE 3 — DATABASE MODELS (SQLAlchemy 2.0 style)

> **Context note:** SQLAlchemy 2.0 uses `Mapped[type]` annotations instead of `Column(Type)`. This is the correct current API.

### `backend/models/regulation.py`
```python
from sqlalchemy import String, Text, SmallInteger, Date, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from uuid import uuid4, UUID
from core.database import Base

class Regulation(Base):
    __tablename__ = "regulations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str | None] = mapped_column(String(200))       # "eu.gdpr", "india.sebi"
    category: Mapped[str | None] = mapped_column(String(100))     # "data_privacy", "finance", "labor"
    jurisdiction: Mapped[str | None] = mapped_column(String(100))
    effective_date: Mapped[date | None] = mapped_column(Date)
    raw_text: Mapped[str | None] = mapped_column(Text)
    qdrant_ids: Mapped[list[str] | None] = mapped_column(ARRAY(String))   # chunk UUIDs in Qdrant
    risk_level: Mapped[int] = mapped_column(SmallInteger, default=0)       # 0-100
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    impact_mappings: Mapped[list["ImpactMapping"]] = relationship(back_populates="regulation")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="regulation")
```

### `backend/models/policy.py`
```python
from sqlalchemy import String, Text, Date, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from uuid import uuid4, UUID
from core.database import Base

class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(String(200))
    owner: Mapped[str | None] = mapped_column(String(200))
    last_review: Mapped[date | None] = mapped_column(Date)
    qdrant_ids: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    impact_mappings: Mapped[list["ImpactMapping"]] = relationship(back_populates="policy")
```

### `backend/models/impact.py`
```python
from sqlalchemy import String, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid4, UUID
from core.database import Base

class ImpactMapping(Base):
    __tablename__ = "impact_mappings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    regulation_id: Mapped[UUID] = mapped_column(ForeignKey("regulations.id"), nullable=False)
    policy_id: Mapped[UUID] = mapped_column(ForeignKey("policies.id"), nullable=False)
    similarity: Mapped[float | None] = mapped_column(Float)           # cosine similarity 0–1
    impact_level: Mapped[str | None] = mapped_column(String(10))      # "HIGH"|"MEDIUM"|"LOW"
    llm_summary: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")   # "OPEN"|"RESOLVED"|"IGNORED"
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    regulation: Mapped["Regulation"] = relationship(back_populates="impact_mappings")
    policy: Mapped["Policy"] = relationship(back_populates="impact_mappings")
```

### `backend/models/alert.py`
```python
from sqlalchemy import String, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid4, UUID
from core.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    regulation_id: Mapped[UUID | None] = mapped_column(ForeignKey("regulations.id"))
    severity: Mapped[str | None] = mapped_column(String(10))          # "HIGH"|"MEDIUM"|"LOW"
    message: Mapped[str | None] = mapped_column(Text)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[datetime] = mapped_column(server_default=func.now())

    regulation: Mapped["Regulation"] = relationship(back_populates="alerts")
```

### `backend/models/__init__.py`
```python
# Import all models here so Alembic can detect them
from .regulation import Regulation
from .policy import Policy
from .impact import ImpactMapping
from .alert import Alert

__all__ = ["Regulation", "Policy", "ImpactMapping", "Alert"]
```

---

## PHASE 4 — DATABASE MIGRATIONS (Alembic)

```bash
cd backend
alembic init alembic
```

### Edit `alembic/env.py` — replace the relevant sections:
```python
# At the top, add these imports
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import your models so Alembic can detect them
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.config import settings
from core.database import Base
import models  # this triggers all model imports

# Replace target_metadata line:
target_metadata = Base.metadata

# Replace run_migrations_online function:
def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.database_url.replace(
        "postgresql+asyncpg", "postgresql"   # alembic uses sync driver
    )
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

### Generate and run migrations
```bash
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head
```

### ✅ CHECKPOINT 2
```bash
# Verify tables were created in Neon
# Option 1: Use Neon's web console at https://console.neon.tech
# Option 2: Connect via psql (if installed):
psql $DATABASE_URL -c "\dt"
# Should list: regulations, policies, impact_mappings, alerts, alembic_version
```

---

## PHASE 5 — QDRANT SERVICE

### `backend/services/qdrant_service.py`
```python
# IMPORTANT: qdrant-client 1.9+ API — use QdrantClient, not AsyncQdrantClient for simplicity
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    UpdateStatus,
)
from sentence_transformers import SentenceTransformer
from core.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)

# ── Singleton instances ──────────────────────────────────────────────────────
_qdrant_client: QdrantClient | None = None
_embedding_model: SentenceTransformer | None = None

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384
COLLECTION_NAME = settings.qdrant_collection  # "regulations_v1"


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            timeout=30,
        )
    return _qdrant_client


def get_embedding_model() -> SentenceTransformer:
    """Load model once, reuse across requests."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def ensure_collection_exists() -> None:
    """Idempotent — creates collection if it doesn't exist."""
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
    else:
        logger.info(f"Qdrant collection already exists: {COLLECTION_NAME}")


def chunk_text(text: str, max_tokens: int = 400) -> list[str]:
    """
    Simple word-based chunker with overlap.
    Using words not tokens for simplicity — ~1.3 words per token on average.
    400 tokens ≈ 520 words.
    """
    words = text.split()
    chunk_size = int(max_tokens * 1.3)
    overlap = chunk_size // 5   # 20% overlap between chunks
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def embed_and_upsert(
    text: str,
    metadata: dict,
    source_type: str = "regulation",
) -> list[str]:
    """
    Chunk text → embed each chunk → upsert to Qdrant.
    Returns list of point IDs (store these in PostgreSQL).
    """
    client = get_qdrant_client()
    model = get_embedding_model()
    chunks = chunk_text(text)

    points = []
    point_ids = []

    for i, chunk in enumerate(chunks):
        vector = model.encode(chunk, normalize_embeddings=True).tolist()
        point_id = str(uuid.uuid4())
        point_ids.append(point_id)
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "text": chunk,
                    "source_type": source_type,
                },
            )
        )

    result = client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,   # wait for indexing to complete
    )

    if result.status != UpdateStatus.COMPLETED:
        raise RuntimeError(f"Qdrant upsert failed: {result.status}")

    logger.info(f"Upserted {len(points)} chunks to Qdrant")
    return point_ids


def semantic_search(
    query_text: str,
    top_k: int = 5,
    category_filter: str | None = None,
    source_type_filter: str | None = None,
    score_threshold: float = 0.3,
) -> list[dict]:
    """
    Search Qdrant by semantic similarity.
    Optional filters by category or source_type.
    """
    client = get_qdrant_client()
    model = get_embedding_model()

    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()

    # Build optional filter
    must_conditions = []
    if category_filter:
        must_conditions.append(
            FieldCondition(key="category", match=MatchValue(value=category_filter))
        )
    if source_type_filter:
        must_conditions.append(
            FieldCondition(key="source_type", match=MatchValue(value=source_type_filter))
        )

    query_filter = Filter(must=must_conditions) if must_conditions else None

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter=query_filter,
        score_threshold=score_threshold,
    )

    return [
        {
            "score": round(hit.score, 4),
            "text": hit.payload.get("text", ""),
            "regulation_id": hit.payload.get("regulation_id"),
            "policy_id": hit.payload.get("policy_id"),
            "title": hit.payload.get("title", ""),
            "category": hit.payload.get("category", ""),
            "source_type": hit.payload.get("source_type", ""),
            "chunk_index": hit.payload.get("chunk_index", 0),
        }
        for hit in results
    ]


def delete_points(point_ids: list[str]) -> None:
    """Remove points from Qdrant (call when deleting a regulation/policy)."""
    client = get_qdrant_client()
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=point_ids,
        wait=True,
    )
```

### ✅ CHECKPOINT 3
```python
# Run this test script to verify Qdrant works end-to-end
# backend/scripts/test_qdrant.py
from services.qdrant_service import ensure_collection_exists, embed_and_upsert, semantic_search

ensure_collection_exists()

ids = embed_and_upsert(
    text="GDPR Article 83 requires controllers to pay fines up to 4% of annual global turnover for violations.",
    metadata={"regulation_id": "test-001", "title": "GDPR Art 83", "category": "data_privacy"},
)
print(f"Stored chunk IDs: {ids}")

results = semantic_search("What are the penalties for data privacy violations?")
for r in results:
    print(f"Score: {r['score']} | {r['title']} | {r['text'][:100]}")
```
```bash
cd backend && python scripts/test_qdrant.py
# Expected: prints chunk IDs, then at least 1 result with score > 0.5
```

---

## PHASE 6 — INGESTION SERVICE

### `backend/services/ingestion.py`
```python
import io
import logging
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.regulation import Regulation
from models.policy import Policy
from services.qdrant_service import embed_and_upsert, ensure_collection_exists
from uuid import UUID

logger = logging.getLogger(__name__)


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_parts.append(extracted.strip())
    return "\n\n".join(text_parts)


async def ingest_regulation(
    db: AsyncSession,
    title: str,
    text: str,
    source: str | None = None,
    category: str | None = None,
    jurisdiction: str | None = None,
    effective_date=None,
) -> Regulation:
    """
    Full ingestion pipeline for a regulation:
    1. Save raw text to PostgreSQL
    2. Chunk + embed + upsert to Qdrant
    3. Update PostgreSQL record with Qdrant chunk IDs
    4. Run risk scorer
    """
    ensure_collection_exists()

    # Step 1: Create PostgreSQL record (without Qdrant IDs yet)
    regulation = Regulation(
        title=title,
        raw_text=text,
        source=source,
        category=category,
        jurisdiction=jurisdiction,
        effective_date=effective_date,
    )
    db.add(regulation)
    await db.flush()   # get the UUID without committing

    # Step 2: Embed + store in Qdrant
    metadata = {
        "regulation_id": str(regulation.id),
        "title": title,
        "source": source or "",
        "category": category or "uncategorized",
        "jurisdiction": jurisdiction or "",
    }
    point_ids = embed_and_upsert(text=text, metadata=metadata, source_type="regulation")

    # Step 3: Update record with Qdrant IDs
    regulation.qdrant_ids = point_ids

    # Step 4: Score risk (import here to avoid circular imports)
    from services.risk_scorer import score_regulation
    regulation.risk_level = score_regulation(text)

    await db.commit()
    await db.refresh(regulation)

    logger.info(f"Ingested regulation: {title} | Risk: {regulation.risk_level} | Chunks: {len(point_ids)}")
    return regulation


async def ingest_policy(
    db: AsyncSession,
    title: str,
    content: str,
    department: str | None = None,
    owner: str | None = None,
) -> Policy:
    """Ingest a company policy — same pipeline as regulation."""
    ensure_collection_exists()

    policy = Policy(title=title, content=content, department=department, owner=owner)
    db.add(policy)
    await db.flush()

    metadata = {
        "policy_id": str(policy.id),
        "title": title,
        "department": department or "",
    }
    point_ids = embed_and_upsert(text=content, metadata=metadata, source_type="policy")
    policy.qdrant_ids = point_ids

    await db.commit()
    await db.refresh(policy)
    return policy
```

---

## PHASE 7 — RISK SCORER SERVICE

### `backend/services/risk_scorer.py`
```python
"""
Risk scorer — two modes:
1. RULE-BASED (default, zero training needed) — good enough for demo
2. ML MODEL (optional, load if model file exists)

Risk score 0-100:
  HIGH   (70-100): fines, mandatory disclosure, criminal liability
  MEDIUM (40-69):  implementation requirements, audit obligations
  LOW    (0-39):   guidelines, recommendations, soft obligations
"""
import re
import os
import logging

logger = logging.getLogger(__name__)

# High-risk signal words — expand this list as needed
HIGH_RISK_KEYWORDS = [
    "fine", "penalty", "sanction", "criminal", "imprisonment", "prohibit",
    "mandatory", "must", "shall", "required", "obligation", "breach",
    "violation", "infringement", "liability", "enforcement", "immediate",
    "ban", "suspend", "revoke", "terminate", "injunction",
]

MEDIUM_RISK_KEYWORDS = [
    "audit", "review", "assess", "report", "disclose", "notify", "implement",
    "establish", "maintain", "ensure", "comply", "compliance", "document",
    "record", "monitor", "inspect", "certify", "approve", "deadline",
]

LOW_RISK_KEYWORDS = [
    "recommend", "should", "consider", "encourage", "may", "optional",
    "guideline", "best practice", "suggest", "advise", "guidance",
]


def _rule_based_score(text: str) -> int:
    """Fast heuristic scoring. No model needed."""
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    word_count = max(len(words), 1)

    high_hits = sum(1 for w in HIGH_RISK_KEYWORDS if w in text_lower)
    medium_hits = sum(1 for w in MEDIUM_RISK_KEYWORDS if w in text_lower)
    low_hits = sum(1 for w in LOW_RISK_KEYWORDS if w in text_lower)

    # Density-based scoring (hits per 100 words)
    high_density = (high_hits / word_count) * 100
    medium_density = (medium_hits / word_count) * 100

    # Check for fine amounts (strong HIGH signal)
    fine_pattern = re.search(
        r'(€|£|\$|usd|eur)\s*[\d,]+\s*(million|billion|thousand)?|'
        r'[\d,]+\s*%(.*?)(annual|revenue|turnover)',
        text_lower
    )
    has_fine_amount = bool(fine_pattern)

    # Scoring logic
    if has_fine_amount or high_density > 2.0:
        base = 75
    elif high_hits >= 3 or medium_density > 3.0:
        base = 50
    elif medium_hits >= 2:
        base = 35
    else:
        base = 15

    # Modifiers
    score = base
    score += min(high_hits * 3, 20)
    score += min(medium_hits * 1, 10)
    score -= min(low_hits * 2, 10)
    score += 10 if has_fine_amount else 0

    return max(0, min(100, score))


def _load_ml_model():
    """Load trained sklearn model if it exists."""
    model_path = "models/risk_scorer.pkl"
    if os.path.exists(model_path):
        import joblib
        logger.info("Loading ML risk scorer model")
        return joblib.load(model_path)
    return None


_ml_model = None
_ml_model_checked = False


def score_regulation(text: str) -> int:
    """
    Primary entry point.
    Uses ML model if available, falls back to rule-based.
    """
    global _ml_model, _ml_model_checked

    if not _ml_model_checked:
        _ml_model = _load_ml_model()
        _ml_model_checked = True

    if _ml_model is not None:
        try:
            proba = _ml_model.predict_proba([text])[0]   # [low, medium, high]
            # Convert probability to 0-100 score
            score = int(proba[1] * 40 + proba[2] * 80)
            return max(0, min(100, score))
        except Exception as e:
            logger.warning(f"ML model failed, using rule-based: {e}")

    return _rule_based_score(text)


def score_to_level(score: int) -> str:
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"
```

---

## PHASE 8 — RAG PIPELINE

### `backend/services/rag_pipeline.py`
```python
"""
RAG Pipeline using LangChain 0.3.x + Qdrant + Google Gemini.

IMPORTANT: LangChain 0.3.x import paths (breaking changes from 0.1.x):
  - langchain_community.vectorstores.Qdrant  → use qdrant_client directly (simpler)
  - langchain_google_genai.ChatGoogleGenerativeAI  → correct import
  - langchain_core.prompts.ChatPromptTemplate  → correct import
"""
import logging
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.qdrant_service import semantic_search
from core.config import settings

logger = logging.getLogger(__name__)


def _get_llm() -> ChatGoogleGenerativeAI:
    """Instantiate Gemini LLM. gemini-1.5-flash is free tier."""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.1,    # low temperature for factual compliance analysis
        max_tokens=2048,
    )


IMPACT_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a senior compliance officer with expertise in regulatory analysis.
Analyze whether a new regulation impacts an existing company policy.
Always respond with a valid JSON object — no markdown, no preamble, just JSON.

Response format:
{{
  "impact_level": "HIGH" | "MEDIUM" | "LOW",
  "affected_clauses": ["list of specific policy sections affected"],
  "compliance_gaps": ["specific gaps found in the policy"],
  "recommended_actions": [
    {{"step": 1, "action": "...", "deadline_days": 30, "owner": "Legal/IT/HR/..."}}
  ],
  "compliance_deadline": "YYYY-MM-DD or null if not specified",
  "reasoning": "2-3 sentence explanation of the impact assessment"
}}"""),
    ("human", """RELEVANT REGULATORY CONTEXT (retrieved from knowledge base):
{context}

NEW REGULATION:
{regulation_text}

EXISTING COMPANY POLICY TO ANALYZE:
{policy_text}

Analyze the impact and respond with JSON only."""),
])

SEMANTIC_SEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a compliance expert. Answer questions about regulations
using only the provided context. Be specific and cite regulation names when possible.
If the context doesn't contain enough information, say so clearly."""),
    ("human", """CONTEXT FROM REGULATORY DATABASE:
{context}

QUESTION: {question}

Answer based on the context above:"""),
])


async def analyze_impact(
    regulation_text: str,
    policy_text: str,
    regulation_title: str = "",
    policy_title: str = "",
) -> dict:
    """
    Core RAG function: given a regulation and a policy,
    retrieve relevant context from Qdrant and use LLM to analyze impact.
    """
    # Step 1: Retrieve semantically similar chunks from Qdrant
    similar_chunks = semantic_search(
        query_text=regulation_text,
        top_k=5,
        score_threshold=0.3,
    )

    context = "\n\n---\n\n".join([
        f"[{chunk.get('title', 'Unknown')} | Score: {chunk['score']}]\n{chunk['text']}"
        for chunk in similar_chunks
    ])

    if not context:
        context = "No additional context available in the knowledge base."

    # Step 2: Run LLM chain
    llm = _get_llm()
    chain = IMPACT_ANALYSIS_PROMPT | llm | StrOutputParser()

    try:
        raw_response = await chain.ainvoke({
            "context": context,
            "regulation_text": f"{regulation_title}\n\n{regulation_text}"[:3000],
            "policy_text": f"{policy_title}\n\n{policy_text}"[:2000],
        })

        # Parse JSON response
        # Strip any accidental markdown code fences
        clean = raw_response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]

        result = json.loads(clean)
        result["source_chunks"] = [c["text"][:200] for c in similar_chunks]
        result["similarity_scores"] = [c["score"] for c in similar_chunks]
        return result

    except json.JSONDecodeError as e:
        logger.error(f"LLM returned invalid JSON: {raw_response[:500]}")
        # Fallback: return structured error response
        return {
            "impact_level": "UNKNOWN",
            "compliance_gaps": ["Analysis failed — manual review required"],
            "recommended_actions": [],
            "compliance_deadline": None,
            "reasoning": f"Automated analysis failed: {str(e)}",
            "raw_response": raw_response,
        }


async def rag_question_answer(question: str) -> dict:
    """
    General RAG Q&A over the regulation knowledge base.
    Used by the /api/rag/explain endpoint.
    """
    chunks = semantic_search(query_text=question, top_k=7, score_threshold=0.25)
    context = "\n\n---\n\n".join([
        f"[{c.get('title', '')} | {c.get('category', '')}]\n{c['text']}"
        for c in chunks
    ])

    llm = _get_llm()
    chain = SEMANTIC_SEARCH_PROMPT | llm | StrOutputParser()

    answer = await chain.ainvoke({"context": context, "question": question})

    return {
        "answer": answer,
        "sources": [{"title": c.get("title"), "score": c["score"]} for c in chunks],
    }
```

---

## PHASE 9 — ALERT ENGINE

### `backend/services/alert_engine.py`
```python
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.regulation import Regulation
from models.policy import Policy
from models.impact import ImpactMapping
from models.alert import Alert
from services.qdrant_service import semantic_search
from services.risk_scorer import score_to_level

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLDS = {
    "HIGH": 0.75,
    "MEDIUM": 0.50,
    "LOW": 0.30,
}


async def run_impact_analysis(
    db: AsyncSession,
    regulation: Regulation,
) -> list[ImpactMapping]:
    """
    For a newly ingested regulation:
    1. Search Qdrant for similar policy chunks (source_type=policy)
    2. Create ImpactMapping records
    3. Fire alerts for HIGH/MEDIUM impacts
    Returns list of created ImpactMapping records.
    """
    if not regulation.raw_text:
        return []

    # Search specifically in policy vectors
    similar_policies = semantic_search(
        query_text=regulation.raw_text[:1000],   # use first 1000 chars as query
        top_k=10,
        source_type_filter="policy",
        score_threshold=SIMILARITY_THRESHOLDS["LOW"],
    )

    # Deduplicate by policy_id (take the highest score per policy)
    seen_policy_ids: dict[str, dict] = {}
    for result in similar_policies:
        pid = result.get("policy_id")
        if pid and (pid not in seen_policy_ids or result["score"] > seen_policy_ids[pid]["score"]):
            seen_policy_ids[pid] = result

    mappings_created = []

    for policy_id_str, result in seen_policy_ids.items():
        score = result["score"]
        impact_level = (
            "HIGH" if score >= SIMILARITY_THRESHOLDS["HIGH"]
            else "MEDIUM" if score >= SIMILARITY_THRESHOLDS["MEDIUM"]
            else "LOW"
        )

        # Check if mapping already exists
        existing = await db.execute(
            select(ImpactMapping).where(
                ImpactMapping.regulation_id == regulation.id,
                ImpactMapping.policy_id == policy_id_str,
            )
        )
        if existing.scalar_one_or_none():
            continue

        mapping = ImpactMapping(
            regulation_id=regulation.id,
            policy_id=policy_id_str,
            similarity=score,
            impact_level=impact_level,
            status="OPEN",
        )
        db.add(mapping)
        mappings_created.append(mapping)

        # Create alert for HIGH and MEDIUM impacts
        if impact_level in ("HIGH", "MEDIUM"):
            alert = Alert(
                regulation_id=regulation.id,
                severity=impact_level,
                message=(
                    f"{impact_level} impact detected: Regulation '{regulation.title}' "
                    f"affects policy (similarity: {score:.2f}). "
                    f"Risk score: {regulation.risk_level}/100."
                ),
            )
            db.add(alert)

    await db.commit()
    logger.info(f"Created {len(mappings_created)} impact mappings for: {regulation.title}")
    return mappings_created
```

---

## PHASE 10 — FASTAPI APPLICATION

### `backend/main.py`
```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import create_tables
from services.qdrant_service import ensure_collection_exists

# Import all routers
from routers import regulations, policies, impact, alerts, rag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run on startup and shutdown."""
    logger.info("Starting up...")
    await create_tables()
    ensure_collection_exists()
    logger.info("Infrastructure ready.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="AI Compliance Management System",
    version="1.0.0",
    description="Regulatory intelligence platform powered by Qdrant + LLM RAG",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(regulations.router, prefix="/api/regulations", tags=["regulations"])
app.include_router(policies.router, prefix="/api/policies", tags=["policies"])
app.include_router(impact.router, prefix="/api/impact", tags=["impact"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
```

### `backend/routers/regulations.py`
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db
from models.regulation import Regulation
from services.ingestion import ingest_regulation, parse_pdf
from services.alert_engine import run_impact_analysis
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter()


class RegulationCreate(BaseModel):
    title: str
    text: str
    source: Optional[str] = None
    category: Optional[str] = None
    jurisdiction: Optional[str] = None
    effective_date: Optional[date] = None


class RegulationResponse(BaseModel):
    id: str
    title: str
    source: Optional[str]
    category: Optional[str]
    risk_level: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/ingest", status_code=201)
async def ingest_regulation_text(
    payload: RegulationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Ingest regulation from raw text → embed → Qdrant → impact analysis."""
    regulation = await ingest_regulation(
        db=db,
        title=payload.title,
        text=payload.text,
        source=payload.source,
        category=payload.category,
        jurisdiction=payload.jurisdiction,
        effective_date=payload.effective_date,
    )
    # Trigger impact analysis in background (simplified: run synchronously for demo)
    await run_impact_analysis(db, regulation)

    return {"id": str(regulation.id), "title": regulation.title, "risk_level": regulation.risk_level}


@router.post("/upload-pdf", status_code=201)
async def upload_regulation_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Upload a regulation PDF → parse → ingest."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    file_bytes = await file.read()
    text = parse_pdf(file_bytes)

    if not text.strip():
        raise HTTPException(422, "Could not extract text from PDF")

    regulation = await ingest_regulation(db=db, title=title, text=text, category=category)
    await run_impact_analysis(db, regulation)

    return {"id": str(regulation.id), "title": regulation.title, "chunks_extracted": len(text.split())}


@router.get("/")
async def list_regulations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Regulation).order_by(desc(Regulation.created_at)).limit(50)
    )
    regulations = result.scalars().all()
    return [
        {
            "id": str(r.id), "title": r.title, "source": r.source,
            "category": r.category, "risk_level": r.risk_level,
            "created_at": r.created_at.isoformat(),
        }
        for r in regulations
    ]


@router.get("/{regulation_id}/similar")
async def get_similar_regulations(regulation_id: str, top_k: int = 5, db: AsyncSession = Depends(get_db)):
    """Find top-K semantically similar regulations using Qdrant."""
    result = await db.execute(select(Regulation).where(Regulation.id == regulation_id))
    regulation = result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(404, "Regulation not found")

    from services.qdrant_service import semantic_search
    similar = semantic_search(
        query_text=regulation.raw_text[:500],
        top_k=top_k + 1,
        source_type_filter="regulation",
    )
    # Exclude self
    filtered = [s for s in similar if s.get("regulation_id") != regulation_id][:top_k]
    return filtered
```

### `backend/routers/impact.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.impact import ImpactMapping
from models.regulation import Regulation
from models.policy import Policy
from services.rag_pipeline import analyze_impact

router = APIRouter()


@router.post("/analyze")
async def analyze_regulation_impact(
    regulation_id: str,
    policy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Full RAG impact analysis between a regulation and a policy."""
    reg_result = await db.execute(select(Regulation).where(Regulation.id == regulation_id))
    regulation = reg_result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(404, "Regulation not found")

    pol_result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = pol_result.scalar_one_or_none()
    if not policy:
        raise HTTPException(404, "Policy not found")

    analysis = await analyze_impact(
        regulation_text=regulation.raw_text or "",
        policy_text=policy.content or "",
        regulation_title=regulation.title,
        policy_title=policy.title,
    )

    # Update the impact mapping with LLM summary
    mapping_result = await db.execute(
        select(ImpactMapping).where(
            ImpactMapping.regulation_id == regulation_id,
            ImpactMapping.policy_id == policy_id,
        )
    )
    mapping = mapping_result.scalar_one_or_none()
    if mapping:
        mapping.impact_level = analysis.get("impact_level", mapping.impact_level)
        mapping.llm_summary = analysis.get("reasoning", "")
        await db.commit()

    return analysis


@router.get("/heatmap")
async def get_risk_heatmap(db: AsyncSession = Depends(get_db)):
    """Returns data for the 2D risk heatmap: departments × categories."""
    result = await db.execute(
        select(ImpactMapping, Policy, Regulation)
        .join(Policy, ImpactMapping.policy_id == Policy.id)
        .join(Regulation, ImpactMapping.regulation_id == Regulation.id)
        .where(ImpactMapping.status == "OPEN")
    )
    rows = result.all()

    # Build heatmap: {department: {category: max_risk_level}}
    heatmap: dict[str, dict[str, int]] = {}
    level_to_score = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

    for mapping, policy, regulation in rows:
        dept = policy.department or "Unknown"
        cat = regulation.category or "General"
        score = level_to_score.get(mapping.impact_level or "LOW", 1)
        if dept not in heatmap:
            heatmap[dept] = {}
        heatmap[dept][cat] = max(heatmap[dept].get(cat, 0), score)

    return {"heatmap": heatmap, "total_open_impacts": len(rows)}
```

### `backend/routers/rag.py`
```python
from fastapi import APIRouter
from pydantic import BaseModel
from services.rag_pipeline import rag_question_answer

router = APIRouter()

class RAGQuery(BaseModel):
    question: str

@router.post("/explain")
async def explain_regulation(payload: RAGQuery):
    """Natural language Q&A over the regulation knowledge base."""
    return await rag_question_answer(payload.question)
```

### `backend/routers/alerts.py`
```python
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update
from core.database import get_db
from models.alert import Alert
import asyncio, json

router = APIRouter()

# Simple in-memory WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()


@router.get("/")
async def get_alerts(db: AsyncSession = Depends(get_db), limit: int = 50):
    result = await db.execute(
        select(Alert).order_by(desc(Alert.sent_at)).limit(limit)
    )
    alerts = result.scalars().all()
    return [
        {
            "id": str(a.id), "severity": a.severity,
            "message": a.message, "acknowledged": a.acknowledged,
            "sent_at": a.sent_at.isoformat(),
        }
        for a in alerts
    ]


@router.patch("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    await db.execute(
        update(Alert).where(Alert.id == alert_id).values(acknowledged=True)
    )
    await db.commit()
    return {"status": "acknowledged"}


@router.websocket("/ws")
async def websocket_alerts(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    """Real-time alert stream via WebSocket."""
    await manager.connect(websocket)
    try:
        while True:
            # Poll for new unacknowledged alerts every 5 seconds
            result = await db.execute(
                select(Alert)
                .where(Alert.acknowledged == False)
                .order_by(desc(Alert.sent_at))
                .limit(5)
            )
            alerts = result.scalars().all()
            if alerts:
                await websocket.send_json({
                    "type": "alerts",
                    "data": [{"id": str(a.id), "severity": a.severity, "message": a.message} for a in alerts]
                })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Run the backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### ✅ CHECKPOINT 4
```bash
# All should return 200
curl http://localhost:8000/health
curl http://localhost:8000/docs        # FastAPI Swagger UI — verify all routes appear

# Test ingest
curl -X POST http://localhost:8000/api/regulations/ingest \
  -H "Content-Type: application/json" \
  -d '{"title":"GDPR Art 83","text":"Infringements shall be subject to fines up to 20 million euros or 4% of annual global turnover","category":"data_privacy"}'
# Expected: {"id": "...", "title": "GDPR Art 83", "risk_level": <number>}
```

---

## PHASE 11 — CELERY BACKGROUND TASKS

### `backend/tasks/celery_tasks.py`
```python
from celery import Celery
from core.config import settings

celery_app = Celery(
    "compliance",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,   # process one task at a time (safe for GPU/CPU bound work)
)


@celery_app.task(bind=True, max_retries=3)
def embed_and_store_async(self, text: str, metadata: dict, source_type: str = "regulation"):
    """
    Background task for embedding large documents.
    Use this for documents > 10 pages to avoid blocking the API.
    """
    try:
        from services.qdrant_service import embed_and_upsert
        point_ids = embed_and_upsert(text=text, metadata=metadata, source_type=source_type)
        return {"status": "success", "point_ids": point_ids}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)  # retry after 60s


@celery_app.task
def scrape_regulations_task():
    """Scheduled task: scrape gov sources for new regulations."""
    # Implement scraping logic here using httpx + BeautifulSoup
    pass
```

### Start Celery worker (separate terminal)
```bash
cd backend
celery -A tasks.celery_tasks worker --loglevel=info --concurrency=2
```

---

## PHASE 12 — DEMO SEED SCRIPT

### `backend/scripts/seed_qdrant.py`
```python
"""
Run this before the demo to populate Qdrant with realistic data.
Usage: cd backend && python scripts/seed_qdrant.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.qdrant_service import ensure_collection_exists, embed_and_upsert

SEED_REGULATIONS = [
    # DATA PRIVACY
    {"regulation_id": "gdpr-art-5", "title": "GDPR Article 5 - Data Processing Principles",
     "category": "data_privacy", "source": "eu.gdpr", "jurisdiction": "EU",
     "text": "Personal data shall be processed lawfully, fairly and in a transparent manner in relation to the data subject. Data must be collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes. Data shall be adequate, relevant and limited to what is necessary. Data shall be accurate and where necessary kept up to date. Data shall be kept in a form which permits identification for no longer than necessary."},

    {"regulation_id": "gdpr-art-17", "title": "GDPR Article 17 - Right to Erasure",
     "category": "data_privacy", "source": "eu.gdpr", "jurisdiction": "EU",
     "text": "The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her without undue delay and the controller shall have the obligation to erase personal data without undue delay where the data is no longer necessary in relation to the purposes for which it was collected, or where the data subject withdraws consent, or where the data subject objects to the processing."},

    {"regulation_id": "gdpr-art-33", "title": "GDPR Article 33 - Breach Notification",
     "category": "data_privacy", "source": "eu.gdpr", "jurisdiction": "EU",
     "text": "In the case of a personal data breach, the controller shall without undue delay and, where feasible, not later than 72 hours after having become aware of it, notify the personal data breach to the supervisory authority. The notification shall describe the nature of the breach, the categories and approximate number of data subjects concerned, the likely consequences, and the measures taken or proposed to address the breach."},

    {"regulation_id": "gdpr-art-83", "title": "GDPR Article 83 - General Conditions for Fines",
     "category": "data_privacy", "source": "eu.gdpr", "jurisdiction": "EU",
     "text": "Infringements of the following provisions shall be subject to administrative fines up to 20,000,000 EUR or up to 4% of the total worldwide annual turnover of the preceding financial year, whichever is higher. These include basic principles for processing, conditions for consent, data subjects rights, transfers of personal data to a recipient in a third country, and non-compliance with an order by the supervisory authority."},

    # FINANCE
    {"regulation_id": "sebi-lodr-2015", "title": "SEBI LODR - Listing Obligations and Disclosure Requirements",
     "category": "finance", "source": "india.sebi", "jurisdiction": "India",
     "text": "Every listed entity shall make disclosures of any events or information which, in the opinion of the board of directors of the listed entity, is material. The listed company shall disclose to the stock exchange within 24 hours from the occurrence of any event. The company shall maintain a structured digital database containing the names of such persons or entities as well as the Permanent Account Number or any other identifier authorized by law of such persons or entities with whom information is shared."},

    {"regulation_id": "rbi-kyc-2016", "title": "RBI KYC Master Direction 2016",
     "category": "finance", "source": "india.rbi", "jurisdiction": "India",
     "text": "Regulated entities shall put in place a Board approved KYC policy which shall incorporate the following four key elements: Customer Acceptance Policy, Risk Management, Customer Identification Procedures, and Monitoring of Transactions. The Customer Due Diligence process must be carried out at the time of commencement of account based relationship. Enhanced Due Diligence shall apply to higher risk customers including Politically Exposed Persons."},

    {"regulation_id": "sec-sox-302", "title": "SOX Section 302 - Corporate Responsibility",
     "category": "finance", "source": "us.sec", "jurisdiction": "US",
     "text": "The principal executive officer or officers and the principal financial officer or officers of each issuer shall certify in each annual or quarterly report that they have reviewed the report, that it does not contain any untrue statement of material fact, and that the financial statements fairly present in all material respects the financial condition. Officers who certify knowing the certification is false may face fines up to $5 million and imprisonment up to 20 years."},

    # LABOR
    {"regulation_id": "id-act-1947", "title": "Industrial Disputes Act 1947 - Retrenchment",
     "category": "labor", "source": "india.mol", "jurisdiction": "India",
     "text": "No workman employed in any industry who has been in continuous service for not less than one year under an employer shall be retrenched by that employer until the workman has been given one month's notice in writing indicating the reasons for retrenchment and the period of notice has expired, or the workman has been paid in lieu of such notice wages for the period of notice. The workman shall also be paid compensation equivalent to fifteen days average pay for every completed year of continuous service."},

    {"regulation_id": "posh-act-2013", "title": "POSH Act 2013 - Prevention of Sexual Harassment",
     "category": "labor", "source": "india.mol", "jurisdiction": "India",
     "text": "Every employer of a workplace shall constitute an Internal Committee to hear and redress grievances pertaining to sexual harassment. The employer shall organize workshops and awareness programmes at regular intervals for sensitizing employees. Any aggrieved woman may make a written complaint of sexual harassment to the Internal Committee within a period of three months from the date of incident. Failure to comply with provisions shall be punishable with fine which may extend to fifty thousand rupees."},

    {"regulation_id": "min-wages-act", "title": "Minimum Wages Act 1948",
     "category": "labor", "source": "india.mol", "jurisdiction": "India",
     "text": "Every employer shall pay to every employee engaged in a scheduled employment under him wages at a rate not less than the minimum rates of wages fixed by notification. If any employer pays to any employee less than the minimum rate of wages fixed for that class of employment, he shall be punishable with imprisonment for a term which may extend to six months or with fine which may extend to five hundred rupees or with both."},
]

async def seed():
    print("Seeding Qdrant with regulation data...")
    ensure_collection_exists()

    total_chunks = 0
    for reg in SEED_REGULATIONS:
        reg_id = reg.pop("regulation_id")
        text = reg.pop("text")
        metadata = {**reg, "regulation_id": reg_id}

        point_ids = embed_and_upsert(text=text, metadata=metadata, source_type="regulation")
        total_chunks += len(point_ids)
        print(f"  ✓ {metadata['title'][:50]} → {len(point_ids)} chunks")

    print(f"\n✅ Seeded {len(SEED_REGULATIONS)} regulations → {total_chunks} total chunks in Qdrant")

if __name__ == "__main__":
    asyncio.run(seed())
```

```bash
cd backend && python scripts/seed_qdrant.py
```

---

## PHASE 13 — FRONTEND

### Bootstrap
```bash
cd frontend
npm install

# Core UI and state
npm install @tanstack/react-query@5 zustand@4 axios socket.io-client@4

# UI components and charts
npm install recharts lucide-react react-dropzone
```

### `frontend/next.config.mjs`
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  rewrites: async () => [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    },
  ],
}

export default nextConfig
```

### `frontend/postcss.config.mjs`
```javascript
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}

export default config
```

### `frontend/src/app/globals.css` — Tailwind v4 setup
```css
@import "tailwindcss";
```

### `frontend/src/app/api/client.ts`
```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Regulations
export const getRegulations = () => api.get('/regulations/')
export const ingestRegulation = (data: {
  title: string; text: string; category?: string; source?: string
}) => api.post('/regulations/ingest', data)
export const uploadRegulationPDF = (formData: FormData) =>
  api.post('/regulations/upload-pdf', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const getSimilarRegulations = (id: string, topK = 5) =>
  api.get(`/regulations/${id}/similar?top_k=${topK}`)

// Policies
export const getPolicies = () => api.get('/policies/')
export const ingestPolicy = (data: { title: string; content: string; department?: string }) =>
  api.post('/policies/ingest', data)

// Impact
export const analyzeImpact = (regulationId: string, policyId: string) =>
  api.post('/impact/analyze', { regulation_id: regulationId, policy_id: policyId })
export const getHeatmap = () => api.get('/impact/heatmap')

// Alerts
export const getAlerts = () => api.get('/alerts/')
export const acknowledgeAlert = (id: string) => api.patch(`/alerts/${id}/acknowledge`)

// RAG
export const askQuestion = (question: string) =>
  api.post('/rag/explain', { question })

export default api
```

### `frontend/src/app/store/appStore.ts`
```typescript
import { create } from 'zustand'

interface Alert {
  id: string; severity: string; message: string; acknowledged: boolean
}

interface AppState {
  alerts: Alert[]
  unreadCount: number
  addAlerts: (alerts: Alert[]) => void
  markRead: () => void
}

export const useAppStore = create<AppState>((set) => ({
  alerts: [],
  unreadCount: 0,
  addAlerts: (newAlerts) =>
    set((state) => ({
      alerts: [...newAlerts, ...state.alerts].slice(0, 100),
      unreadCount: state.unreadCount + newAlerts.length,
    })),
  markRead: () => set({ unreadCount: 0 }),
}))
```

### `frontend/src/app/hooks/useWebSocket.ts`
```typescript
import { useEffect } from 'react'
import { useAppStore } from '../store/appStore'

export function useWebSocket() {
  const addAlerts = useAppStore((s) => s.addAlerts)

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/alerts/ws')

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'alerts') {
        addAlerts(data.data)
      }
    }

    ws.onerror = (e) => console.error('WebSocket error:', e)
    ws.onclose = () => console.log('WebSocket closed')

    return () => ws.close()
  }, [addAlerts])
}
```

### `frontend/src/app/components/SemanticSearch.tsx`
```typescript
import { useState } from 'react'
import { askQuestion } from '../api/client'
import { Search, Loader2 } from 'lucide-react'

export default function SemanticSearch() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const { data } = await askQuestion(query)
      setResult(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Semantic Regulation Search</h2>
      <p className="text-gray-500 mb-4 text-sm">
        Powered by Qdrant — searches by meaning, not just keywords
      </p>

      <div className="flex gap-2 mb-6">
        <input
          className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g. data breach notification deadline..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? <Loader2 className="animate-spin" size={16} /> : <Search size={16} />}
          Search
        </button>
      </div>

      {result && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-800 mb-2">AI Answer</h3>
            <p className="text-blue-900">{result.answer}</p>
          </div>

          {result.sources?.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2 text-gray-700">Sources (Qdrant similarity scores)</h3>
              {result.sources.map((src: any, i: number) => (
                <div key={i} className="flex items-center gap-3 mb-2">
                  <span className="text-sm text-gray-600 flex-1">{src.title}</span>
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${src.score * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500 w-10 text-right">
                    {(src.score * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
```

### `frontend/src/app/page.tsx`
```typescript
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import { useWebSocket } from './hooks/useWebSocket'
import SemanticSearch from './components/SemanticSearch'
// import other components as you build them

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
})

function AppContent() {
  useWebSocket()  // Connect WebSocket globally
  const [tab, setTab] = useState('search')

  const tabs = ['search', 'ingest', 'heatmap', 'alerts', 'impact']

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <h1 className="text-xl font-bold text-gray-900">
          AI Compliance Management System
        </h1>
      </header>
      <nav className="bg-white border-b px-6">
        <div className="flex gap-6">
          {tabs.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`py-3 text-sm font-medium capitalize border-b-2 ${
                tab === t
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </nav>
      <main className="p-6">
        {tab === 'search' && <SemanticSearch />}
        {/* Add other tab components here */}
      </main>
    </div>
  )
}

export default function Home() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  )
}
```

### `frontend/src/app/layout.tsx`
```typescript
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Compliance Management System',
  description: 'Semantic regulation analysis and policy impact assessment',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

### Start frontend
```bash
cd frontend
npm run dev
# Opens at http://localhost:3000
```

### ✅ CHECKPOINT 5
```
1. Open http://localhost:3000
2. Navigate to "search" tab
3. Type: "data breach notification deadline"
4. Should return an AI answer + Qdrant similarity scores
```

---

## PHASE 14 — ML RISK SCORER TRAINING (Optional but recommended)

> Skip this for the hackathon if short on time. The rule-based scorer in Phase 7 is sufficient for demo.

### `ml/requirements_ml.txt`
```text
scikit-learn==1.5.2
pandas==2.2.3
joblib==1.4.2
datasets==3.1.0       # HuggingFace datasets
google-generativeai==0.8.3
```

### `ml/label_dataset.py`
```python
"""
Step 1: Auto-label raw regulation text using Gemini.
Run: python ml/label_dataset.py
"""
import json, time, pandas as pd
import google.generativeai as genai
from datasets import load_dataset

genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

def label_text(text: str) -> dict | None:
    prompt = f"""Rate the compliance risk of this regulation text.
Return ONLY a JSON object with no markdown: {{"score": 0-100, "level": "HIGH"|"MEDIUM"|"LOW", "category": "data_privacy"|"finance"|"labor"|"general"}}

Text: {text[:800]}"""
    try:
        resp = model.generate_content(prompt)
        return json.loads(resp.text.strip())
    except Exception as e:
        print(f"  Failed: {e}")
        return None

# Load EUR-Lex dataset from HuggingFace (no login needed)
print("Loading EUR-Lex dataset...")
ds = load_dataset("eurlex", "eurlex57k", split="train[:500]", trust_remote_code=True)

labeled = []
for i, item in enumerate(ds):
    text = item.get("text", "")[:800]
    if len(text) < 100:
        continue
    print(f"Labeling {i+1}/500: {text[:60]}...")
    label = label_text(text)
    if label:
        labeled.append({"text": text, **label})
    time.sleep(0.5)   # avoid rate limiting

df = pd.DataFrame(labeled)
df.to_csv("ml/labeled_regulations.csv", index=False)
print(f"Saved {len(df)} labeled examples to ml/labeled_regulations.csv")
print(df["level"].value_counts())
```

### `ml/train_risk_scorer.py`
```python
"""
Step 2: Train the risk classifier.
Run: python ml/train_risk_scorer.py
"""
import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

# Load labeled data
df = pd.read_csv("ml/labeled_regulations.csv").dropna(subset=["text", "level"])
label_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
df["label"] = df["level"].map(label_map)
df = df.dropna(subset=["label"])

print(f"Dataset: {len(df)} samples")
print(df["level"].value_counts())

X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"],
    test_size=0.2, random_state=42, stratify=df["label"]
)

# TF-IDF + Logistic Regression pipeline
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=15000,
        ngram_range=(1, 3),
        sublinear_tf=True,          # log-scale TF
        strip_accents="unicode",
        analyzer="word",
        token_pattern=r"\b[a-zA-Z]{2,}\b",
    )),
    ("clf", LogisticRegression(
        C=5.0,
        class_weight="balanced",
        max_iter=2000,
        solver="lbfgs",
        multi_class="multinomial",
    )),
])

# Cross-validation on training set
cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring="f1_macro")
print(f"CV F1 (macro): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

# Train on full training set
pipeline.fit(X_train, y_train)

# Evaluate
y_pred = pipeline.predict(X_test)
print("\nTest Set Report:")
print(classification_report(y_test, y_pred, target_names=["LOW", "MEDIUM", "HIGH"]))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save model
os.makedirs("backend/models", exist_ok=True)
joblib.dump(pipeline, "backend/models/risk_scorer.pkl")
print("\n✅ Model saved to backend/models/risk_scorer.pkl")
print("Restart the FastAPI server to use the ML model.")
```

---

## PHASE 15 — RUNNING THE FULL STACK

### All services in order
```bash
# Terminal 1 — Infrastructure
docker compose up -d

# Terminal 2 — Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3 — Celery worker
cd backend
source venv/bin/activate
celery -A tasks.celery_tasks worker --loglevel=info --concurrency=2

# Terminal 4 — Frontend
cd frontend
npm run dev

# Terminal 5 — Seed data (run once)
cd backend && python scripts/seed_qdrant.py
```

### ✅ FINAL CHECKPOINT
```bash
# 1. Infrastructure
curl http://localhost:6333/readyz          # Qdrant: {"result":"ok"}
curl http://localhost:8000/health          # FastAPI: {"status":"ok"}

# 2. Qdrant has data
curl http://localhost:6333/collections/regulations_v1  # shows vector count > 0

# 3. Ingest works
curl -X POST http://localhost:8000/api/regulations/ingest \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","text":"Companies must report data breaches within 72 hours or face fines.","category":"data_privacy"}'

# 4. Semantic search works
curl -X POST http://localhost:8000/api/rag/explain \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the penalties for GDPR violations?"}'

# 5. Frontend: http://localhost:5173 — search tab works
```

---

## QUICK REFERENCE — PACKAGE VERSIONS USED

| Package | Version | Notes |
|---|---|---|
| `fastapi` | 0.115.4 | async, WebSocket support built-in |
| `uvicorn[standard]` | 0.32.1 | ASGI server |
| `qdrant-client` | 1.12.1 | Official SDK; use `QdrantClient`, not `AsyncQdrantClient` |
| `sentence-transformers` | 3.3.1 | `normalize_embeddings=True` for cosine similarity |
| `langchain` | 0.3.7 | Split into langchain + langchain-core + langchain-community |
| `langchain-google-genai` | 2.0.5 | Use `ChatGoogleGenerativeAI` not `GoogleGenerativeAI` |
| `google-generativeai` | 0.8.3 | Use `gemini-1.5-flash` for free tier |
| `sqlalchemy` | 2.0.36 | Use `Mapped[type]` annotations not `Column(Type)` |
| `alembic` | 1.14.0 | Use sync driver (psycopg2) for migrations even with async app |
| `asyncpg` | 0.30.0 | Async PostgreSQL driver for SQLAlchemy |
| `pydantic` | 2.10.2 | `model_config = ConfigDict(from_attributes=True)` not `class Config` |
| `celery` | 5.4.0 | Use redis as both broker and backend |
| Node | 20+ | Required for Next.js 16 |
| `next` | 16.2.4 | Full-stack framework with file-based routing |
| `@tanstack/react-query` | v5 | Breaking change from v4: `useQuery` options changed |
| `tailwindcss` | v4 | `@import "tailwindcss"` in CSS, PostCSS plugin |

---

## COMMON ERRORS & FIXES

```
ERROR: asyncpg.exceptions.UndefinedTableError
FIX:   Run `alembic upgrade head` — tables not created yet

ERROR: qdrant_client.http.exceptions.UnexpectedResponse: status_code: 404
FIX:   Call ensure_collection_exists() on startup (already in main.py lifespan)

ERROR: ImportError: cannot import name 'Qdrant' from 'langchain_community.vectorstores'
FIX:   Use qdrant_client directly (as shown in rag_pipeline.py) — don't use LangChain Qdrant wrapper

ERROR: Cannot find module or socket.io connection fails in Next.js
FIX:   Use 'use client' directive in components that use WebSocket; ensure CORS is configured in FastAPI

ERROR: pydantic.errors.PydanticUserError: `from_attributes` not allowed
FIX:   Use `model_config = ConfigDict(from_attributes=True)` (Pydantic v2 syntax)

ERROR: sentence_transformers warning about tokenizer parallelism
FIX:   Set TOKENIZERS_PARALLELISM=false in .env — safe to ignore in dev

ERROR: CORS blocked on frontend
FIX:   Verify origins in main.py CORSMiddleware match your frontend URL exactly

ERROR: WebSocket connection failed
FIX:   Ensure next.config.mjs has rewrites configured; use ws:// not http:// in WebSocket URLs; mark components with 'use client'

ERROR: alembic can't detect model changes
FIX:   Ensure `import models` is in alembic/env.py before `target_metadata = Base.metadata`
```