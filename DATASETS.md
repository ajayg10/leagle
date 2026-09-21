# Datasets Integration Guide

## Overview

The CodeWizards AI Compliance Management System integrates three high-quality datasets to provide:

1. **SEC Forms (10-K)** - Corporate compliance benchmark & knowledge base
2. **Legal Text Classification** - Risk scorer training data  
3. **Global Regulatory Data** - GDPR, DPDP Act, LexGLUE, SOC 2, PCI-DSS

---

## Dataset Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FROM EXTERNAL SOURCES:          FROM BUILT-IN:               │
│  ├─ HuggingFace Hub               ├─ GDPR Articles 5,32,33   │
│  │  ├─ PleIAs/SEC                │  ├─ DPDP Act (India)      │
│  │  ├─ amohankumar/legal-fca     │  ├─ SOC 2 Type II         │
│  │  └─ lex_glue                   │  ├─ PCI-DSS v3.2.1        │
│  ├─ Kaggle                         │  └─ Sample Policies       │
│  ├─ Government Websites            │                           │
│  │  ├─ data.gov.in (DPDP)         │                           │
│  │  └─ EUR-Lex (GDPR)             │                           │
│  └─ PDF/Web Scraping              │                           │
│                                    │                           │
├─────────────────────────────────────────────────────────────────┤
│          services/dataset_loader.py - Parse & Chunk             │
├─────────────────────────────────────────────────────────────────┤
│   Embedding: sentence-transformers/all-MiniLM-L6-v2 (384-dim)   │
├─────────────────────────────────────────────────────────────────┤
│     Qdrant Vector Database (Core Intelligence Engine)           │
│  9+ regulatory chunks + company policy vectors                   │
│  Semantic search enables finding related regulations/policies    │
│                                                                 │
│  When user uploads a new regulation:                            │
│  1. Embed regulation → Qdrant similarity search                 │
│  2. Return top-K similar docs from benchmark                    │
│  3. Use LLM to analyze compliance gaps                          │
│  4. Predict risk using trained ML model                        │
│  5. Generate remediation recommendations                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Dataset 1: SEC Forms (PleIAs/SEC)

### Purpose
**Benchmark & Knowledge Base**: Real-world examples of how companies translate regulations into actual policies.

### Data Source
- **HuggingFace Hub**: `PleIAs/SEC`
- **Content**: Full text SEC Form 10-K annual reports
- **Key Sections**: Item 1A (Risk Factors), Item 1 (Business), Item 9A (Controls & Procedures)

### Why It Works
- Publicly disclosed, official company "policies"
- Shows how 100+ companies interpret compliance requirements
- Provides "Competitor Benchmark" for policy review

### Integration
```python
# Load SEC dataset
from services.dataset_loader import SECDatasetSeeder

chunks_seeded = SECDatasetSeeder.seed_sec_data(
    max_companies=100,
    max_documents_per_company=3,
)
```

### Usage in Compliance System
When analyzing a new regulation:
```
New Regulation → Embed → Qdrant Search → Find similar company practices
                                         ↓
                         "100 other companies handle this rule like this..."
```

---

## Dataset 2: Legal Text Classification

### Purpose
**ML Training Data**: Teach the Risk Scorer to predict risk levels (0-100).

### Data Source
- **Kaggle**: `amohankumar/legal-fca`
- **Content**: ~25,000 Federal Court of Australia cases with outcomes
- **Outcome Mapping**: Text description → Verdict → Fine amount

### Why It Works
- **Labeled Data**: Each case links "text describing violation" to "outcome/fine"
- Example: "Company failed to notify users of data breach → $2M fine" = HIGH risk
- Trains ML model to predict risk from policy text alone

### Integration
```python
# Prepare legal case data for ML training
from services.dataset_loader import LegalCaseDatasetPreparer

samples_prepared = LegalCaseDatasetPreparer.prepare_legal_case_data(
    output_file="backend/ml/legal_training_data.jsonl",
    max_samples=5000,
)
```

### Output Format (JSONL)
```json
{
  "text": "Company Q failed to implement access controls, leading to data breach affecting 50,000 users...",
  "risk_level": "HIGH",
  "fine_amount": 2000000,
  "violation_type": "data_privacy",
  "outcome": "Liable - $2M fine imposed"
}
```

### Usage in Compliance System
```
Policy Text → ML Model → Risk Score 0-100
"Our policy: ...weak access controls..."
                     ↓
                 ML predicts 65 (HIGH RISK)
                     ↓
           "This policy leaves you exposed to $1-3M fines"
```

---

## Dataset 3: Global Regulatory Data

### Built-In Regulations (No Download Required)
Quick-start seeding includes:

| Regulation | Articles | Coverage |
|---|---|---|
| **GDPR** | Articles 5, 32, 33 | Data principles, security, breach notification |
| **India DPDP Act** | Chapter 2 | Data rights, consent, erasure |
| **SOC 2 Type II** | Full | Controls, availability, processing integrity |
| **PCI-DSS** | v3.2.1 | Payment card data security |

### External Regulatory Sources

#### GDPR (EU)
- **Source**: HuggingFace - `Johny201/gdpr-articles`
- **Coverage**: All 99 articles of EU data protection
- **Usage**: Primary Europe compliance baseline

#### Indian DPDP Act
- **Source**: `IndiaCode.nic.in` (official gazette)
- **Coverage**: India's 2023 digital personal data law
- **Usage**: Unique Indian requirements not in GDPR

#### LexGLUE (Legal NLP Benchmark)
- **HuggingFace**: `lex_glue`
- **Coverage**: Multi-sector legal documents (contracts, statutes, cases)
- **Role**: Cross-sector compliance patterns

### Integration
```python
# Seed built-in regulatory data
from services.dataset_loader import RegulatoryDatasetSeeder

chunks = RegulatoryDatasetSeeder.seed_regulatory_data()

# Also seed LexGLUE benchmark
chunks += RegulatoryDatasetSeeder.seed_from_lexglue()
```

---

## Quick Start Scripts

### 1. Fast Demo (Built-In Data Only)
```bash
cd backend
python scripts/seed_demo_data.py
```
**Output**: 9 chunks (GDPR, DPDP, SOC 2, PCI-DSS, sample policies)  
**Time**: <1 minute  
**Best For**: Local development, quick testing

### 2. Full Dataset Seeding (HuggingFace + External)
```bash
cd backend
python scripts/seed_datasets.py --all
```
**Output**: 1000+ chunks  
**Time**: 5-15 minutes (depends on internet)  
**What it does**:
- Loads SEC 10-K forms (100 companies)
- Prepares legal case data for ML (5,000 samples)
- Seeds all regulatory data (GDPR, DPDP, LexGLUE)

### 3. Seed Individual Datasets
```bash
# SEC dataset only
python scripts/seed_datasets.py --sec-only --sec-companies 50

# Regulatory data only
python scripts/seed_datasets.py --regulatory-only

# Prepare ML training data
python scripts/seed_datasets.py --prepare-ml-data
```

---

## Dataset Flow Through System

### Step 1: Ingest Regulation
User uploads new GDPR Article:
```bash
curl -X POST http://localhost:8000/api/regulations/ingest \
  -H "Content-Type: application/json" \
  -d '{"title":"GDPR Art 30","text":"Records of processing...","category":"data_privacy"}'
```

### Step 2: Embed → Qdrant
```python
# In backend/services/ingestion.py
text, metadata = acquire_regulation()
chunk_ids = embed_and_upsert(text, metadata, source_type="regulation")
# Now in Qdrant: new chunks + similarity to existing SEC/regulatory data
```

### Step 3: RAG Pipeline Retrieval
```python
# Fast semantic search in Qdrant
similar_docs = semantic_search(
    query_text=regulation_text,
    top_k=5,
    category_filter="data_privacy",
)

# Results include:
# - Similar GDPR articles (high semantic match)
# - SEC 10-K sections addressing same issue (benchmark)
# - Existing company policies that will be impacted
```

### Step 4: LLM Analysis
```python
# services/rag_pipeline.py
context = format_similar_docs(similar_docs)
llm_analysis = gemini.analyze_impact(
    regulation=regulation_text,
    policy=company_policy,
    context=context,  # The retrieved dataset pieces
)
```

### Step 5: ML Risk Scoring
```python
# services/risk_scorer.py
risk_score = model.predict(regulation_text) # 0-100
# Model trained on legal_training_data.jsonl from Dataset 2
```

### Step 6: User Sees
```json
{
  "impact": "HIGH",
  "risk_score": 78,
  "affected_policies": [
    "Data Retention Policy",
    "Access Control Policy"
  ],
  "recommendation": "Update retention periods to 30 days max...",
  "similar_regulations": [
    "GDPR Article 5 (Principles)",
    "SEC 10-K Item 1A (Risk Factors)"
  ]
}
```

---

## Data Quality & Maintenance

### Chunk Size Strategy
- **Regulations**: 400 tokens per chunk (~1.6KB)
- **Policies**: 512 tokens per chunk (~2KB)
- **SEC Forms**: 800 tokens per chunk (~3.2KB)

**Rationale**: Balances semantic coherence (finding related regulations) with coverage (more chunks = more matches).

### Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384-dim vectors
- **Speed**: ~1000 sentences/second on CPU
- **Reason**: Free, small, accurate for legal text

### Qdrant Collection
```python
# Created automatically by ensure_collection_exists()
Collection: regulations_v1
  - Distance: COSINE similarity (0-1 scale)
  - Size: Unlimited (scales to millions of vectors)
  - Indexed: Yes (ANN search <100ms per query)
```

### Updating Datasets
To add new external data:

1. **Create custom loader** in `services/dataset_loader.py`:
   ```python
   class MyDatasetLoader:
       def parse_my_data(self, sample):
           return text, metadata
   ```

2. **Add to seed script** in `scripts/seed_datasets.py`:
   ```python
   chunks = MyDatasetLoader.load_and_seed(max_samples=1000)
   ```

3. **Run seeding**:
   ```bash
   python scripts/seed_datasets.py
   ```

---

## Storage & Deployment

### Local Development
- Qdrant: Docker container (`qdrant/qdrant:v1.9.1`)
- Storage: Persistent volume `qdrant_storage`
- Data survives container restarts

### Production Deployment
- **Option 1**: Managed Qdrant Cloud (https://cloud.qdrant.io)
- **Option 2**: Self-hosted Qdrant with persistent storage
- **Option 3**: Larger cloud deployments with replication

### Backup Strategy
```bash
# Export all vectors
qdrant-cli --host localhost --port 6333 \
    export regulations_v1 backup.tar.gz

# Import to new instance
qdrant-cli --host newhost --port 6333 \
    import regulations_v1 backup.tar.gz
```

---

## Performance Benchmarks

| Operation | Time | Notes |
|---|---|---|
| Embed 1 document | ~100ms | CPU (all-MiniLM-L6-v2) |
| Upsert 100 chunks to Qdrant | ~200ms | HTTP batch request |
| Semantic search (top-5 results) | ~50ms | ANN indexing |
| RAG pipeline (retrieve + LLM) | ~2-5s | Gemini API latency |

---

## FAQ

**Q: Can I use different embedding models?**  
A: Yes! Install any `sentence-transformers` model and update `EMBEDDING_MODEL` in `qdrant_service.py`. **Warning**: This invalidates all existing vectors; you'll need to re-seed Qdrant.

**Q: Which dataset should I prioritize?**  
A: 
1. **Data 3 (regulatory)** first - core compliance rules
2. **Data 1 (SEC)** second - industry best practices  
3. **Data 2 (legal cases)** third - ML model training

**Q: Can I add my own policies?**  
A: Yes! Upload via endpoint:
```bash
POST /api/policies/ingest
{"title": "...", "content": "...", "department": "..."}
```
System embeds and stores in Qdrant automatically.

**Q: What if I want to remove a dataset?**  
A: Clear and reseed:
```bash
# In Qdrant console or API
DELETE /collections/regulations_v1

# Then reseed
python scripts/seed_demo_data.py
```

---

## Resources

- **SEC Dataset**: https://huggingface.co/datasets/PleIAs/SEC
- **Legal Cases**: https://www.kaggle.com/datasets/amohankumar/legal-text-classification-dataset
- **LexGLUE**: https://huggingface.co/datasets/lex_glue
- **GDPR Text**: https://huggingface.co/datasets/Johny201/gdpr-articles
- **Sentence Transformers**: https://www.sbert.net/
- **Qdrant Docs**: https://qdrant.tech/documentation/

