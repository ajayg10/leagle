# PDF Ingestion Pipeline - Architecture & Design Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                                 │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Ingest Component                                                │   │
│  │  - File upload with validation                                  │   │
│  │  - Loading state management                                     │   │
│  │  - Debug mode toggle                                            │   │
│  │  - Result display with statistics                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                 ↓ HTTP POST
                    /api/ingest/upload?debug=true
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Router: /api/ingest/upload                                      │   │
│  │  - File type validation (PDF only)                              │   │
│  │  - File size validation (50MB limit)                            │   │
│  │  - HTTPException handling (400, 413, 422, 500)                  │   │
│  │  - Response schema validation                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                 ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Stage 1: PDF Extraction (pdf_service.py)                      │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │ extract_text_from_pdf(file_bytes, filename)             │  │    │
│  │  │                                                          │  │    │
│  │  │ INPUT:  Binary PDF file                                 │  │    │
│  │  │                                                          │  │    │
│  │  │ VALIDATION:                                             │  │    │
│  │  │  ✓ Size check (50MB)                                    │  │    │
│  │  │  ✓ Corruption check (PyPDF reader)                      │  │    │
│  │  │  ✓ Per-page validation                                  │  │    │
│  │  │  ✓ Empty text detection                                 │  │    │
│  │  │                                                          │  │    │
│  │  │ OUTPUT: {                                               │  │    │
│  │  │   "text": extracted_text,                               │  │    │
│  │  │   "num_pages": 45,                                      │  │    │
│  │  │   "char_count": 125000,                                 │  │    │
│  │  │   "metadata": {                                         │  │    │
│  │  │     "file_size_mb": 2.34,                               │  │    │
│  │  │     "pages_extracted": 45,                              │  │    │
│  │  │     "page_details": [...]                               │  │    │
│  │  │   }                                                      │  │    │
│  │  │ }                                                        │  │    │
│  │  │                                                          │  │    │
│  │  │ LOGGING: "PDF extraction successful: ... 2.34MB"       │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                 ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Stage 2: Text Chunking (chunk_service.py)                    │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │ split_text(text, strategy="token", chunk_size, overlap) │  │    │
│  │  │                                                          │  │    │
│  │  │ INPUT:  Extracted text (125,000 chars)                 │  │    │
│  │  │                                                          │  │    │
│  │  │ TOKENIZATION (tiktoken):                               │  │    │
│  │  │  125,000 chars → ~25,000 tokens (GPT-3.5/4)           │  │    │
│  │  │                                                          │  │    │
│  │  │ CHUNKING STRATEGY:                                      │  │    │
│  │  │  Token-based (PRIMARY):                                 │  │    │
│  │  │   ✓ 512 tokens per chunk                                │  │    │
│  │  │   ✓ 100 tokens overlap                                  │  │    │
│  │  │   ✓ 50 chunks generated                                 │  │    │
│  │  │   ✓ Respects semantic boundaries                        │  │    │
│  │  │                                                          │  │    │
│  │  │  Character-based (FALLBACK if tokenization fails):      │  │    │
│  │  │   • 500 chars per chunk                                 │  │    │
│  │  │   • 50 chars overlap                                    │  │    │
│  │  │                                                          │  │    │
│  │  │ OUTPUT: {                                               │  │    │
│  │  │   "chunks": ["chunk1...", "chunk2...", ...],           │  │    │
│  │  │   "num_chunks": 50,                                     │  │    │
│  │  │   "strategy": "token",                                  │  │    │
│  │  │   "total_tokens": 25000,                                │  │    │
│  │  │   "chunk_metadata": [                                   │  │    │
│  │  │     {"chunk_id": 0, "token_count": 512, ...},          │  │    │
│  │  │     {...}                                               │  │    │
│  │  │   ]                                                      │  │    │
│  │  │ }                                                        │  │    │
│  │  │                                                          │  │    │
│  │  │ LOGGING: "Token-based chunking... 25000 tokens"        │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                 ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Stage 3: Embedding Generation (embedding_service.py)        │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │ generate_embeddings(chunks, debug=True)                 │  │    │
│  │  │                                                          │  │    │
│  │  │ INPUT:  List of 50 chunks                              │  │    │
│  │  │                                                          │  │    │
│  │  │ BATCHING STRATEGY:                                      │  │    │
│  │  │  ┌─────────────────────────────────────────────────┐   │  │    │
│  │  │  │ Batch 1: Chunks 1-20                            │   │  │    │
│  │  │  │ ├─ Call OpenAI API with retry logic             │   │  │    │
│  │  │  │ ├─ Retry 1 (2s delay if rate limited)           │   │  │    │
│  │  │  │ ├─ Retry 2 (4s delay if rate limited)           │   │  │    │
│  │  │  │ ├─ Retry 3 (8s delay if rate limited)           │   │  │    │
│  │  │  │ ├─ Response: 20 embeddings (1536-dims each)      │   │  │    │
│  │  │  │ └─ Log: "Batch 1/3 success: 20 embeddings"      │   │  │    │
│  │  │  │                                                  │   │  │    │
│  │  │  │ Batch 2: Chunks 21-40                           │   │  │    │
│  │  │  │ ├─ Same process...                               │   │  │    │
│  │  │  │ └─ Response: 20 embeddings                       │   │  │    │
│  │  │  │                                                  │   │  │    │
│  │  │  │ Batch 3: Chunks 41-50                           │   │  │    │
│  │  │  │ ├─ Same process...                               │   │  │    │
│  │  │  │ └─ Response: 10 embeddings                       │   │  │    │
│  │  │  └─────────────────────────────────────────────────┘   │  │    │
│  │  │                                                          │  │    │
│  │  │ OUTPUT: {                                               │  │    │
│  │  │   "embeddings": [                                       │  │    │
│  │  │     [0.123, -0.456, 0.789, ...],  // 1536 dims         │  │    │
│  │  │     [0.234, -0.567, 0.890, ...],                       │  │    │
│  │  │     ...                                                 │  │    │
│  │  │   ],                                                    │  │    │
│  │  │   "num_embeddings": 50,                                 │  │    │
│  │  │   "batches_processed": 3,                               │  │    │
│  │  │   "model": "text-embedding-3-small",                    │  │    │
│  │  │   "tokens_used": 500000,                                │  │    │
│  │  │   "batch_metadata": [{...}, {...}, {...}]              │  │    │
│  │  │ }                                                        │  │    │
│  │  │                                                          │  │    │
│  │  │ LOGGING: "Embedding complete... 500K tokens used"      │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                 ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Stage 4: Response Compilation                               │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │ Response Schema:                                         │  │    │
│  │  │ {                                                        │  │    │
│  │  │   "status": "success",                                  │  │    │
│  │  │   "message": "PDF ingestion pipeline completed! 🚀",   │  │    │
│  │  │   "document_id": "document.pdf",                        │  │    │
│  │  │   "pipeline_stats": {                                   │  │    │
│  │  │     "file_size_mb": 2.34,                               │  │    │
│  │  │     "extracted_chars": 125000,                          │  │    │
│  │  │     "extracted_pages": 45,                              │  │    │
│  │  │     "num_chunks": 50,                                   │  │    │
│  │  │     "num_embeddings": 50,                               │  │    │
│  │  │     "embedding_model": "text-embedding-3-small",        │  │    │
│  │  │     "tokens_used": 500000,                              │  │    │
│  │  │     "chunking_strategy": "token"                        │  │    │
│  │  │   },                                                     │  │    │
│  │  │   "extraction": { /* optional, debug mode only */ },    │  │    │
│  │  │   "chunking": { /* optional, debug mode only */ },      │  │    │
│  │  │   "embeddings": { /* optional, debug mode only */ }     │  │    │
│  │  │ }                                                        │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                 ↓ HTTP 200 OK
                         (or appropriate error code)
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    Frontend (React) - Display                            │
│  - Success message                                                       │
│  - Pipeline statistics                                                   │
│  - Optional debug information                                            │
│  - Error messages with context                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Timeline

```
User uploads PDF
    ↓ (100ms)
PDF validated & read into memory
    ↓ (50ms)
Text extracted from pages → 125K chars
    ↓ (10ms)
Text tokenized → 25K tokens
    ↓ (50ms)
Tokens split into 50 chunks (512 tokens each, 100 token overlap)
    ↓ (5s)
Batched embedding generation:
    Batch 1 (20 chunks) → 20 embeddings ✓
    Batch 2 (20 chunks) → 20 embeddings ✓
    Batch 3 (10 chunks) → 10 embeddings ✓
    ↓ (200ms)
Response compiled with statistics
    ↓
HTTP 200 OK returned to client
    ↓
Frontend displays results
```

**Total Time: ~5.5 seconds**
**Cost: ~$0.0015 USD** (500K tokens @ $0.00003 per 1K tokens)

---

## Error Handling Flow

```
Upload Request
    ↓
File Type Check
    ├─ ❌ Not PDF → 400 Bad Request
    ├─ ✓ PDF → Continue
    ↓
File Size Check
    ├─ ❌ > 50MB → 413 Payload Too Large
    ├─ ✓ ≤ 50MB → Continue
    ↓
Extraction Phase
    ├─ ❌ Corrupted PDF → 500 Internal Server Error
    ├─ ❌ No text extracted → 422 Unprocessable Entity
    ├─ ✓ Text extracted → Continue
    ↓
Chunking Phase
    ├─ ❌ Empty text → 422 Unprocessable Entity
    ├─ ✓ Chunks generated → Continue
    ↓
Embedding Phase
    ├─ ❌ Rate limited (attempt 1) → Wait 2s, retry
    ├─ ❌ Rate limited (attempt 2) → Wait 4s, retry
    ├─ ❌ Rate limited (attempt 3) → Wait 8s, retry
    ├─ ❌ Still rate limited → 500 Internal Server Error
    ├─ ❌ Quota exceeded → 500 Internal Server Error
    ├─ ✓ Embeddings generated → Continue
    ↓
Success Response (200 OK)
    └─ Return pipeline statistics and optional debug data
```

---

## Configuration & Tuning

### For Small/Medium PDFs (< 10MB)
```python
# All defaults are fine
TOKEN_CHUNK_SIZE = 512
BATCH_SIZE = 20
```

### For Large PDFs (10-50MB)
```python
# Consider reducing for faster feedback
TOKEN_CHUNK_SIZE = 256  # Smaller chunks
BATCH_SIZE = 10         # Smaller batches (more resilient)
```

### For High-Throughput Scenarios
```python
# Increase for efficiency
TOKEN_CHUNK_SIZE = 768  # Larger chunks
BATCH_SIZE = 50         # Larger batches (requires good rate limits)
```

### For Development/Testing
```python
# Enable debug mode
debug=true  # Returns detailed intermediate outputs
```

---

## Future Architecture (Phase 2+)

```
┌──────────────┐
│  Frontend    │
│   (React)    │
└───────┬──────┘
        │ Upload PDF
        ↓
┌──────────────────────────────────────┐
│     API Gateway / FastAPI            │
│  POST /api/ingest/upload            │
└─────┬────────────────────────────────┘
      │ Queue job
      ↓
┌──────────────────────────────────────┐
│  Message Queue (Redis/RabbitMQ)      │
│  Job ID: {uuid}                      │
└─────┬────────────────────────────────┘
      │ Worker picks up job
      ↓
┌──────────────────────────────────────┐
│  Celery Worker(s)                    │
│  - Extract                           │
│  - Chunk                             │
│  - Embed                             │
└─────┬────────────────────────────────┘
      │ Store results
      ↓
┌──────────────────────────────────────┐
│  Vector Database (Qdrant)            │
│  - Store embeddings                  │
│  - Enable semantic search            │
└──────────────────────────────────────┘

Frontend polls for status:
GET /api/ingest/status/{job_id}
→ Returns: "pending" | "processing" | "completed" | "failed"
```

---

## Key Metrics to Monitor

```
Performance:
- Total pipeline time (target: < 30s for 50MB)
- Embedding API latency (target: < 5s per batch)
- Token usage efficiency (tokens_used / document_size)

Reliability:
- Successful ingestions (target: 99.9%)
- Failed batches (target: < 1%)
- Rate limit hits (target: 0 after tuning)

Cost:
- Cost per document (tokens_used * price_per_token)
- Cost per chunk (cost_per_document / num_chunks)
- Daily/monthly embedding costs

Quality:
- Extraction success rate (text_extracted / total_uploads)
- Average chunk quality score (manual review sample)
- Semantic coherence of chunks
```

---

## Deployment Architecture

```
Production Server:
├── API Container (FastAPI)
│   ├── /routers/upload.py (endpoint)
│   ├── /services/pdf_service.py (extraction)
│   ├── /services/chunk_service.py (chunking)
│   └── /services/embedding_service.py (embedding)
├── Logging (stdout → ELK/Datadog)
├── Monitoring (Prometheus metrics)
└── Environment:
    ├── OPENAI_API_KEY
    ├── MAX_PDF_SIZE_MB
    └── Other configs

External Services:
├── OpenAI API (Embeddings)
└── Optional: Qdrant (Vector store)
```

This architecture is ready for production deployment! 🚀
