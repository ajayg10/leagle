# Local Development Setup Guide

Complete step-by-step instructions to set up CodeWizards locally with Qdrant, Redis, backend, and frontend.

**Estimated Time**: 20-30 minutes  
**Prerequisites**: Docker, Python 3.14+, Node.js 18+, Git

---

## Phase 1: Prerequisites Check

### 1.1 Verify Docker Installation

```bash
docker --version
docker compose --version
```

**Expected output:**
```
Docker version 27.x.x
Docker Compose version v2.x.x
```

If not installed, download from https://www.docker.com/products/docker-desktop

### 1.2 Verify Python Installation

```bash
python --version
```

**Expected output:** Python 3.14.x or higher

### 1.3 Verify Node Installation

```bash
node --version
npm --version
```

**Expected output:** Node 18+, npm 9+

---

## Phase 2: Clone/Access Repository

```bash
# Navigate to your projects directory
cd ~/Projects

# Clone the repository (or access existing)
git clone https://github.com/your-org/CodeWizards.git
cd CodeWizards
```

---

## Phase 3: Environment Configuration

### 3.1 Create Environment File

```bash
cp .env.example .env
```

### 3.2 Update `.env` with Your Credentials

```bash
# Open .env in your editor
nano .env
# or
code .env
```

**Set these values:**

```dotenv
# Database (already configured for development - skip for now)
DATABASE_URL=postgresql+asyncpg://neondb_owner:YOUR_PASSWORD@your-neon-endpoint.neon.tech/neondb?sslmode=require

# Qdrant (local Docker)
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=regulations_v1

# Redis (local Docker)
REDIS_URL=redis://localhost:6379/0

# LLM - Get free key at https://aistudio.google.com/app/apikey
GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
```

**Note:** For local development, Qdrant and Redis will run in Docker containers automatically.

---

## Phase 4: Start Infrastructure (Qdrant + Redis)

### 4.1 Start Docker Services

From the project root:

```bash
docker compose up -d
```

This starts:
- **Qdrant** (vector database) on port 6333
- **Redis** (message queue) on port 6379

### 4.2 Verify Services Are Running

```bash
docker compose ps
```

**Expected output:**
```
NAME      IMAGE              STATUS
qdrant    qdrant:v1.9.1      Up 2 minutes
redis     redis:7-alpine     Up 2 minutes
```

### 4.3 Test Qdrant Connection

```bash
curl -s http://localhost:6333/health | jq .
```

**Expected output:**
```json
{
  "title": "qdrant",
  "version": "1.9.1",
  "status": "ok"
}
```

### 4.4 Test Redis Connection

```bash
redis-cli -p 6379 ping
```

**Expected output:**
```
PONG
```

---

## Phase 5: Backend Setup

### 5.1 Navigate to Backend

```bash
cd backend
```

### 5.2 Create Python Virtual Environment

```bash
python -m venv venv
```

### 5.3 Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### 5.4 Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.136.0 sqlalchemy-2.0.49 qdrant-client-1.17.1 ...
```

This may take 2-5 minutes.

### 5.5 Test Backend Imports

```bash
python -c "import fastapi; import qdrant_client; print('✅ All imports successful')"
```

**Expected output:**
```
✅ All imports successful
```

### 5.6 Seed Demo Data to Qdrant

This populates Qdrant with 9 demo regulatory documents:

```bash
python scripts/seed_demo_data.py
```

**Expected output:**
```
✅ Qdrant collection ready (regulations_v1)
✅ Embedded GDPR Article 5 (1 chunk, 384-dim)
✅ Embedded GDPR Article 32 (1 chunk, 384-dim)
✅ Embedded GDPR Article 33 (1 chunk, 384-dim)
✅ Embedded DPDP Act (1 chunk, 384-dim)
✅ Embedded SOC 2 Type II (1 chunk, 384-dim)
✅ Embedded PCI-DSS (1 chunk, 384-dim)
✅ Embedded Data Retention Policy (1 chunk, 384-dim)
✅ Embedded Access Control Policy (1 chunk, 384-dim)
✅ Embedded Incident Response Policy (1 chunk, 384-dim)

📊 Total chunks seeded: 9
```

### 5.7 Start Backend Server

```bash
python main.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
✅ FastAPI server started
```

Leave this terminal running.

### 5.8 Test Backend Health (New Terminal)

```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{"status":"healthy","service":"CodeWizards Compliance API","version":"0.1.0"}
```

---

## Phase 6: Frontend Setup

### 6.1 Open New Terminal and Navigate to Frontend

```bash
cd frontend
```

### 6.2 Install Node Dependencies

```bash
npm install
```

**Expected output:**
```
up to date, audited 150 packages in 2s
```

This may take 2-3 minutes on first run.

### 6.3 Start Development Server

```bash
npm run dev
```

**Expected output:**
```
> next dev
  ▲ Next.js 15.1.3
  - Local:        http://localhost:3000
  - Environments: .env.local

✓ Ready in 1.23s
```

Leave this terminal running.

---

## Phase 7: Verify Everything Works

### 7.1 Check All Services

Open your browser and test:

| Service | URL | Expected |
|---------|-----|----------|
| **Frontend** | http://localhost:3000 | Next.js welcome page |
| **Backend Health** | http://localhost:8000/health | JSON status |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Qdrant Health** | http://localhost:6333/health | JSON status |
| **Redis** | Terminal: `redis-cli ping` | PONG |

### 7.2 Test API Endpoint

```bash
curl -X POST http://localhost:8000/api/regulations/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Regulation",
    "text": "This is a test regulation about data privacy and security requirements.",
    "category": "data_privacy",
    "source": "TEST",
    "jurisdiction": "TEST",
    "effective_date": "2025-01-01"
  }'
```

**Expected response:**
```json
{
  "id": "abc-123-def",
  "title": "Test Regulation",
  "category": "data_privacy",
  "source": "TEST",
  "jurisdiction": "TEST",
  "risk_level": 50,
  "qdrant_ids": [10, 11, 12],
  "created_at": "2025-04-17T10:30:00Z"
}
```

### 7.3 Test Semantic Search

Use the regulation ID from above:

```bash
curl http://localhost:8000/api/regulations/{REGULATION_ID}/similar?top_k=5
```

**Expected response:**
```json
{
  "regulation_id": "abc-123-def",
  "query_title": "Test Regulation",
  "similar_documents": [
    {
      "qdrant_id": 1,
      "title": "GDPR Article 5",
      "source_type": "regulation",
      "source": "GDPR",
      "similarity_score": 0.92
    },
    ...
  ],
  "total_results": 5
}
```

---

## Phase 8: Terminal Setup Summary

You should now have 3 active terminals:

```
Terminal 1: Backend
$ cd backend && source venv/bin/activate && python main.py
▲ Listening on http://0.0.0.0:8000

Terminal 2: Frontend
$ cd frontend && npm run dev
▲ Next.js running on http://localhost:3000

Terminal 3: Admin
$ cd project-root
(for running scripts, tests, commands)
```

---

## Daily Development Workflow

### Start Servers (First Time Each Day)

```bash
# Terminal 1: Infrastructure
docker compose up -d

# Terminal 2: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 3: Frontend
cd frontend
npm run dev
```

### Stop Everything

```bash
# In any terminal
docker compose down

# Kill backend terminal (Ctrl+C)
# Kill frontend terminal (Ctrl+C)
```

### Fresh Start (If Issues)

```bash
# Stop everything
docker compose down

# Remove volumes (CAREFUL - deletes all data)
docker compose down -v

# Start fresh
docker compose up -d

# Backend
cd backend
python scripts/seed_demo_data.py
python main.py

# Frontend
cd frontend
npm run dev
```

---

## Access Points

Once everything is running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend App** | http://localhost:3000 | Main UI (React/Next.js) |
| **API Docs** | http://localhost:8000/docs | Interactive API testing (Swagger) |
| **API (ReDoc)** | http://localhost:8000/redoc | Alternative API docs |
| **Qdrant Console** | http://localhost:6333/dashboard | Vector DB UI |
| **Backend API** | http://localhost:8000 | REST endpoints |

---

## Troubleshooting

### Docker Issues

**Problem:** "Docker daemon is not running"
```bash
# Start Docker Desktop or
docker-machine start default
```

**Problem:** "Port 6333 already in use"
```bash
# Find process using port
lsof -i :6333

# Kill it (careful!) or change port in docker-compose.yml
```

### Backend Issues

**Problem:** "ModuleNotFoundError: No module named 'fastapi'"
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem:** "Connection refused on port 8000"
```bash
# Make sure backend is running
curl http://localhost:8000/health

# If not, start it
python main.py
```

### Frontend Issues

**Problem:** "Module not found: Cannot find module 'react'"
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Problem:** "Port 3000 already in use"
```bash
# Use different port
npm run dev -- -p 3001
```

### Qdrant Issues

**Problem:** "Connection refused on port 6333"
```bash
# Check if Docker containers are running
docker compose ps

# If not, start them
docker compose up -d

# Verify
curl http://localhost:6333/health
```

**Problem:** "Collection not found"
```bash
# Seed demo data
cd backend
python scripts/seed_demo_data.py
```

---

## Next Steps After Setup

1. **Interactive API Testing**
   - Open http://localhost:8000/docs
   - Try endpoints in Swagger UI

2. **Frontend Development**
   - Edit files in `frontend/src/`
   - Changes auto-reload on save

3. **Backend Development**
   - Edit Python files in `backend/`
   - Restart `python main.py` to see changes

4. **Implement More Routers**
   - Create `backend/routers/impact.py` for compliance analysis
   - Create `backend/routers/alerts.py` for notifications
   - See [NEXT_STEPS.md](NEXT_STEPS.md) for templates

5. **Add More Data**
   - Run `python scripts/seed_datasets.py --sec-only` to load SEC forms
   - Or upload regulations via API

---

## Project Structure Reference

```
CodeWizards/
├── docker-compose.yml          ← Infrastructure (Qdrant + Redis)
├── .env                        ← Environment variables
├── .env.example               ← Template
│
├── backend/
│   ├── main.py               ← FastAPI app entry point
│   ├── requirements.txt       ← Python dependencies
│   ├── venv/                ← Virtual environment
│   ├── core/
│   │   ├── config.py        ← Settings from .env
│   │   └── database.py      ← SQLAlchemy setup
│   ├── models/
│   │   ├── regulation.py
│   │   ├── policy.py
│   │   ├── impact.py
│   │   └── alert.py
│   ├── routers/
│   │   ├── regulations.py   ← Implemented
│   │   └── policies.py      ← Implemented
│   ├── services/
│   │   ├── qdrant_service.py     ← Vector DB operations
│   │   └── dataset_loader.py     ← Data ingestion
│   └── scripts/
│       └── seed_demo_data.py     ← Demo data (9 chunks)
│
└── frontend/
    ├── package.json          ← Node dependencies
    ├── next.config.mjs       ← Next.js config
    └── src/
        ├── app/
        │   ├── page.js      ← Home page
        │   ├── layout.js    ← Layout wrapper
        │   └── globals.css  ← Styles
        └── components/      ← React components
```

---

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **System Architecture**: [SYSTEM_ARCHITECTURE.md](../SYSTEM_ARCHITECTURE.md)
- **Next Steps**: [NEXT_STEPS.md](../NEXT_STEPS.md)
- **Dataset Info**: [DATASETS.md](../DATASETS.md)
- **Progress**: [PROGRESS.md](../PROGRESS.md)

