# System Architecture - CodeWizards AI Compliance Management

## Executive Summary

CodeWizards is an **AI-powered compliance management system** that:
1. **Ingests** regulations + company policies  
2. **Analyzes** compliance gaps using RAG (retrieval-augmented generation)  
3. **Predicts** compliance risk with ML models trained on legal cases  
4. **Recommends** remediation actions via LLM  
5. **Tracks** compliance status with real-time alerts  

**Tech Stack**: FastAPI (Python), PostgreSQL (SQL), Qdrant (vectors), Redis (cache), Next.js (UI)

---

## System Components

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js/React)                                 │
│  - Regulation dashboard                                                          │
│  - Policy compliance checker                                                     │
│  - Real-time alert viewer                                                        │
│  - Impact analysis explorer                                                      │
└──────────────────────────────────────────▲───────────────────────────────────────┘
                                           │ WebSocket + REST APIs
                                           │
┌──────────────────────────────────────────┴───────────────────────────────────────┐
│                    FASTAPI Backend (Python 3.14)                                 │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  Routes                  Services                      Data                     │
│  ┌──────────────┐       ┌──────────────┐              ┌─────────────┐          │
│  │ Regulations  │──────→│ Qdrant       │◄─────────────│ PostgreSQL  │          │
│  │ Policies     │       │ Service      │              │ (Relations) │          │
│  │ Impact       │       │              │              │             │          │
│  │ Alerts       │       │ - Embed      │              │ - Regs      │          │
│  │ RAG/Chat     │       │ - Search     │              │ - Policies  │          │
│  │ Risk Score   │       │ - Upsert     │              │ - Impacts   │          │
│  └──────────────┘       └──────────────┘              │ - Alerts    │          │
│         │                                              └─────────────┘          │
│         │ Async I/O                                                             │
│         └─────────────────┬────────────────────────────────────────┐            │
│                           │                                        │            │
│             ┌─────────────v─────────────┐      ┌──────────────────v┐          │
│             │ RAG Pipeline Service      │      │ ML Risk Scorer    │          │
│             │ (LangChain + Gemini)      │      │ (scikit-learn)    │          │
│             │                           │      │                  │          │
│             │ - Retrieve from Qdrant    │      │ Input: Policy    │          │
│             │ - Format for LLM          │      │ Output: Risk 0-100
│             │ - Call Gemini 1.5 Flash   │      │                  │          │
│             │ - Generate recommendations│      └──────────────────┘          │
│             └──────────────────────────┘                                      │
│                                                                                │
└──────────────────────────────────────────────────────────────────────────────────┘
         │                                                              │
         │ Async Jobs                                  Semantic Search  │
         │                                             384-dim vectors  │
         │                                                              │
    ┌────v────────┐                                    ┌───────────────v────┐
    │ Redis Queue │                                    │  Qdrant (Vector DB) │
    │ (Celery)    │                                    │  regulations_v1     │
    │             │                                    │                    │
    │ - Embed     │                                    │ 1000+ chunks:      │
    │ - Index     │                                    │ - SEC 10-K forms   │
    │ - Alert     │                                    │ - GDPR articles    │
    └─────────────┘                                    │ - Legal judgments  │
                                                        │ - Policy texts     │
                                                        └────────────────────┘
                                           │ Training data
                                           │
                                    ┌──────v──────────┐
                                    │ ML Training Set │
                                    │ (legal_cases)   │
                                    │ 5000+ samples   │
                                    └─────────────────┘
```

---

## Core Workflows

### Workflow 1: Regulation Ingestion & Analysis

```
1. USER UPLOADS REGULATION
   ├─ Title: "GDPR Article 36"
   ├─ Text: "Where required, the controller..."
   ├─ Category: "data_privacy"
   └─ Effective Date: "2018-05-25"

2. EMBED & INDEX (Qdrant Service)
   ├─ Chunk text into 400-token pieces
   ├─ Generate 384-dim embeddings (all-MiniLM-L6-v2)
   ├─ Upsert to Qdrant with metadata
   └─ Done: <5s, indexed for search

3. SIMILARITY SEARCH
   ├─ Query Qdrant: "Find related regulations/policies"
   ├─ Return top-5 similar chunks:
   │  ├─ GDPR Article 35 (Impact Assessment)
   │  ├─ SEC 10-K Item 1A (Risk Factors)
   │  ├─ Company Policy: "Data Processing Guidelines"
   │  ├─ Legal Case: "Fine for failure to consult..."
   │  └─ Policy: "Vendor Management Process"
   └─ Score: 0.92, 0.88, 0.85, 0.79, 0.76

4. RAG PIPELINE ANALYSIS (LangChain + Gemini)
   ├─ Prompt: "New regulation: {text}, Context: {similar_docs}"
   │           "Analyze compliance requirements and identified gaps"
   ├─ Gemini Response:
   │  ├─ Impact Analysis: {impact_level, required_actions, timeline}
   │  ├─ Affected Policies: ["Data Processing Guidelines", "Vendor Mgmt"]
   │  ├─ Compliance Gaps: ["Missing Article 36 consultation clause"]
   │  ├─ Recommended Actions: ["Update policy to require 72h review", ...]
   │  └─ Risk Assessment: HIGH (based on ML model)
   └─ Store: Impact record linked to regulation + policy

5. ALERT GENERATION
   ├─ Type: COMPLIANCE_REQUIRED
   ├─ Severity: HIGH
   ├─ Message: "2 policies need updates for GDPR Art 36"
   └─ Notify: Legal team → real-time WebSocket alert

6. USER SEES
   ├─ Dashboard: New alert "2 policies impacted"
   ├─ Details: Which policies, which articles, why
   ├─ Actions: "Review impact analysis → Approve/Request changes"
   └─ Status Tracking: Mark as RESOLVED when policy updated
```

### Workflow 2: Policy Compliance Checker

```
1. USER UPLOADS COMPANY POLICY
   ├─ Title: "Data Retention Policy v2.3"
   ├─ Content: "Retain personal data for 1 year..."
   ├─ Department: "Legal"
   └─ Owner: "jane@company.com"

2. SIMILARITY SEARCH (What regulations apply?)
   ├─ Embed policy → Qdrant semantic search
   ├─ Find all relevant regulations:
   │  ├─ GDPR Article 5c (Data minimization - 1 year is excessive)
   │  ├─ GDPR Article 17 (Right to erasure)
   │  ├─ DPDP Act Section 10 (Data retention period)
   │  └─ SOC 2 Principle C1 (Data availability)
   └─ Return matches with confidence scores

3. FOR EACH RELEVANT REGULATION:
   ├─ Retrieve regulation text (already indexed)
   ├─ Call LLM: "Policy: {policy_text}, Rule: {rule_text}, Compliant?"
   ├─ LLM Response: {is_compliant: bool, gaps: [str], severity: str}
   └─ Mark HIGH RISK if gaps found

4. GENERATE COMPLIANCE REPORT
   ├─ Summary: "86% compliant, 2 gaps identified"
   ├─ Compliant Rules: ✅ GDPR Art 28, ✅ SOC 2 C1
   ├─ Non-Compliant: 
   │  ├─ ❌ GDPR Art 5c: Retention = 1 year (rule says <6 months for temp data)
   │  ├─ ❌ DPDP Act: No erasure procedure defined
   └─ Recommended Changes: ["List action items for policy update"]

5. STORE IMPACT RECORD
   ├─ Type: POLICY_ASSESSMENT
   ├─ Policy ID → Regulation ID mapping
   ├─ Compliance status & gap details
   └─ Next review: 30 days

6. USER SEES
   ├─ Compliance score: 86%
   ├─ 2 issues to fix, estimated effort: 2 hours
   ├─ Action items in priority order
   └─ Health indicator: "Red - Requires immediate attention"
```

### Workflow 3: ML Risk Prediction

```
BACKGROUND PROCESS (Runs on all regulations/policies):

1. NEW REGULATION ARRIVES
   ├─ Store in PostgreSQL
   ├─ Embed to Qdrant ✓
   └─ Feed to ML risk scorer...

2. ML RISK SCORER
   ├─ Input: Regulation text
   ├─ Model: Trained on 5000 legal case outcomes
   │         (text description → fine amount)
   ├─ Extract features: Regulatory keywords, violation types
   ├─ Predict: Risk score 0-100
   └─ Example: GDPR breach without notification → 89 (very high)

3. SCORE INTERPRETATION
   ├─ 0-30: LOW RISK - Standard operational requirement
   ├─ 31-70: MEDIUM RISK - Significant compliance effort
   └─ 71-100: HIGH RISK - Heavy penalties, regulatory scrutiny

4. STORE & ALERT
   ├─ Save risk_level to Regulation record
   ├─ If score > 70: Trigger HIGH priority alert
   ├─ Highlight policies that don't address this risk
   └─ Schedule follow-up review in 7 days

5. USER SEES
   ├─ Risk indicator on regulation card: 🔴 HIGH (84)
   ├─ Tooltip: "Based on 23 similar legal cases..."
   ├─ Estimated fines: "$500K - $5M if violated"
   └─ Policy gaps: "3 company policies don't fully address"
```

---

## Data Models

### PostgreSQL Schema

```sql
-- REGULATIONS TABLE (External compliance rules)
regulations:
  - id (UUID PRIMARY KEY)
  - title (VARCHAR) -- "GDPR Article 5"
  - category (VARCHAR, indexed) -- "data_privacy"
  - raw_text (TEXT) -- Full regulation text
  - source (VARCHAR) -- "GDPR", "DPDP_ACT", "SEC", ...
  - jurisdiction (VARCHAR) -- "EU", "INDIA", "US", ...
  - effective_date (TIMESTAMP)
  - risk_level (SMALLINT 0-100) -- ML risk score
  - qdrant_ids (ARRAY OF INTEGER) -- Chunk IDs for deletion
  - created_at (TIMESTAMP, indexed)
  - updated_at (TIMESTAMP)

-- POLICIES TABLE (Company internal policies)
policies:
  - id (UUID PRIMARY KEY)
  - title (VARCHAR) -- "Data Retention Policy"
  - content (TEXT)
  - department (VARCHAR, indexed) -- "Legal", "IT", ...
  - owner (VARCHAR) -- Email of responsible party
  - version (VARCHAR) -- "v2.3"
  - qdrant_ids (ARRAY)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)

-- IMPACT_MAPPINGS TABLE (Junction: Regulation → Policy impact)
impact_mappings:
  - id (UUID PRIMARY KEY)
  - regulation_id (UUID FK, indexed)
  - policy_id (UUID FK, indexed)
  - similarity_score (FLOAT 0-1) -- Qdrant match score
  - impact_level (ENUM: LOW/MEDIUM/HIGH)
  - llm_summary (TEXT) -- "Policy fails to include…"
  - reasoning (TEXT) -- Detailed gap analysis
  - recommended_actions (ARRAY OF TEXT)
  - status (ENUM: OPEN/RESOLVED/IGNORED, indexed)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)
  - reviewed_by (VARCHAR, nullable)
  - reviewed_at (TIMESTAMP, nullable)

-- ALERTS TABLE (Compliance notifications)
alerts:
  - id (UUID PRIMARY KEY)
  - regulation_id (UUID FK, indexed)
  - severity (VARCHAR: LOW/MEDIUM/HIGH/CRITICAL)
  - title (VARCHAR)
  - message (TEXT)
  - acknowledged (BOOLEAN, indexed)
  - acknowledged_at (TIMESTAMP, nullable)
  - acknowledged_by (VARCHAR, nullable)
  - created_at (TIMESTAMP, indexed)
  - updated_at (TIMESTAMP)
```

### Qdrant Vector Store

```
Collection: regulations_v1

Each Point (chunk):
  - id: auto-generated integer
  - vector: 384-dimensional embedding (all-MiniLM-L6-v2)
  - payload (metadata):
    {
      "source_type": "regulation" | "policy" | "sec_form" | "legal_case",
      "source_id": "uuid",
      "title": "GDPR Article 5",
      "category": "data_privacy",
      "jurisdiction": "EU",
      "chunk_index": 0,
      "total_chunks": 3,
      "created_at": "2025-01-15T10:30:00Z"
    }
```

---

## API Endpoints (FastAPI)

### Regulations
```
POST   /api/regulations/ingest
       Body: {title, text, category, source, jurisdiction, effective_date}
       Returns: {id, status, qdrant_ids}

GET    /api/regulations/{id}
       Returns: {id, title, text, risk_level, qdrant_ids, impact_mappings}

GET    /api/regulations/{id}/similar
       Params: ?top_k=5&category_filter=data_privacy
       Returns: [{id, title, similarity_score, source_type}, ...]

DELETE /api/regulations/{id}
       Deletes from PostgreSQL + Removes vectors from Qdrant

PUT    /api/regulations/{id}/risk
       Body: {risk_level}
       Returns: Updated regulation with new risk score
```

### Policies
```
POST   /api/policies/ingest
       Body: {title, content, department, owner, version}
       Returns: {id, status, qdrant_ids}

GET    /api/policies/{id}
       Returns: {id, title, content, department, impact_mappings}

POST   /api/policies/{id}/compliance-check
       Returns: {compliance_score, gaps, impacted_regulations, recommendations}

PUT    /api/policies/{id}
       Body: {title, content, version}
       Returns: Updated policy (re-embedded)
```

### Impact Analysis
```
POST   /api/impact/analyze
       Body: {regulation_id, policy_id}
       Returns: {impact_level, llm_summary, recommended_actions, status}

GET    /api/impact?regulation_id=xxx&open_only=true
       Returns: [{regulation_id, policy_id, impact_level, status}, ...]

PUT    /api/impact/{id}/resolve
       Body: {status, resolved_by, notes}
       Returns: Updated impact record with new status
```

### Alerts
```
GET    /api/alerts?severity=HIGH&acknowledged=false
       Returns: [{id, title, severity, created_at}, ...]

PUT    /api/alerts/{id}/acknowledge
       Body: {acknowledged_by}
       Returns: Updated alert with acknowledged_at timestamp

WebSocket /api/alerts/ws
       Subscribe to real-time alerts
       Receives: {event_type, data, timestamp}
```

### RAG / Compliance Chat
```
POST   /api/rag/chat
       Body: {query, regulation_id (optional), policy_id (optional)}
       Returns: {response, sources, confidence}
       
Example:
  Query: "What policies must we update for GDPR compliance?"
  Response: "Update 3 policies: Data Retention, Access Control, Incident Response"
  Sources: [GDPR Art 5, Art 32, Art 33]
```

### Risk Scoring
```
POST   /api/risk/predict
       Body: {text, type: "regulation" | "policy"}
       Returns: {risk_score (0-100), confidence, factors}

GET    /api/risk/stats
       Returns: {avg_risk_score, high_risk_count, trend}
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15 + React | UI/Dashboard |
| **API** | FastAPI 0.136 | REST endpoints + WebSocket |
| **Async** | Python 3.14 async/await | Non-blocking I/O |
| **Database** | Neon PostgreSQL | Relational data (regs, policies, impacts) |
| **ORM** | SQLAlchemy 2.0 | Type-safe database queries |
| **Vectors** | Qdrant 1.9.1 | Semantic search engine |
| **Embedding** | sentence-transformers | Text → 384-dim vectors |
| **LLM** | Google Gemini 1.5 Flash | Analysis & recommendations |
| **RAG** | LangChain 0.3.7 | Retrieval + Generation pipeline |
| **ML** | scikit-learn | Risk scoring model |
| **Cache** | Redis 7 | Celery task queue |
| **Tasks** | Celery | Async embedding/indexing jobs |
| **Migrations** | Alembic 1.18 | Schema version control |

---

## Deployment Architecture (Production)

```
┌──────────────────────────────────────────────────────────────────┐
│                     INTERNET                                     │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTPS
        ┌──────────────v────────────────┐
        │   Reverse Proxy (nginx)        │
        │   - SSL termination            │
        │   - Rate limiting              │
        │   - Load balancing             │
        └──────────────┬─────────────────┘
                       │
     ┌─────────────────┼─────────────────┐
     │                 │                 │
┌────v┐          ┌────v┐          ┌────v┐
│FE#1 │          │API#1│          │API#2│  (Kubernetes pods)
└─────┘          └─────┘          └─────┘
                     │
     ┌───────────────┴──────────────┐
     │                              │
┌────v──────────────┐    ┌─────────v────────┐
│ Neon PostgreSQL   │    │ Qdrant Managed   │  (Fully managed)
│ Serverless        │    │ Cloud            │
└───────────────────┘    └──────────────────┘
     │
   ┌─v───────────────────────────────────┐
   │ Redis (ElastiCache)                 │
   │ - Celery task queue                 │
   │ - Session cache                     │
   └─────────────────────────────────────┘
```

---

## Security Considerations

### Authentication
- [ ] JWT tokens from Auth0 or Keycloak
- [ ] API key for service-to-service calls
- [ ] WebSocket token validation

### Data Protection
- [ ] Encrypt GDPR text at rest in PostgreSQL
- [ ] Encrypt vectors at rest in Qdrant
- [ ] TLS for all network communication
- [ ] Role-based access control (Regulation Editor, Policy Owner, Reviewer)

### Audit Trail
- [ ] Log all regulation ingestions
- [ ] Track policy modifications (version history)
- [ ] Record all impact analysis decisions
- [ ] Alert acknowledgment audit trail

### Rate Limiting
- [ ] 100 requests/min per user for API
- [ ] 10 analyses/min for LLM calls (cost control)
- [ ] 1000 embeddings/hour for batch operations

---

## Performance Targets

| Operation | Target | Achieved |
|-----------|--------|----------|
| Embed regulation | <5s | ✅ |
| Semantic search | <100ms | ✅ (Qdrant ANN) |
| RAG analysis | 2-5s | ✅ (Gemini latency) |
| Policy compliance check | <10s | ⏳ (With 10 similar regs) |
| Dashboard load | <2s | 🎯 (Frontend optimization) |

---

## Next Steps

1. **Implement FastAPI routers** (regulations.py, policies.py, impact.py, alerts.py)
2. **Build RAG pipeline** (LangChain + Gemini integration)
3. **Train ML risk scorer** (scikit-learn on legal case data)
4. **Develop React components** (Dashboard, compliance checker, alert viewer)
5. **Setup CI/CD** (GitHub Actions → Docker → Kubernetes)
6. **Security hardening** (Auth, encryption, audit logging)

