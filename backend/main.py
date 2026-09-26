import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import create_tables
from core.auth import get_current_user, require_admin
from services.qdrant_service import ensure_collection_exists
from routers import regulations, policies, impact, alerts, rag, upload, analytics, whatsapp
from routers.public_api import router as public_api_router
from core.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run on startup and shutdown."""
    # Fail fast if Clerk auth vars are missing in non-development environments
    if settings.environment != "development":
        if not settings.clerk_jwks_url or not settings.clerk_issuer:
            raise RuntimeError(
                "CLERK_JWKS_URL and CLERK_ISSUER must be set in production. "
                "Copy .env.example and fill in your Clerk domain."
            )

    port = os.getenv("PORT", "8000")
    logger.info(f"starting on port {port}")
    
    # Run heavy startup tasks in background to allow Uvicorn to bind the port immediately
    async def startup_tasks():
        await create_tables()
        await asyncio.to_thread(ensure_collection_exists)
        
        # Check if database has any regulations; if 0, auto-seed curated dataset into DB & Qdrant
        try:
            from core.database import AsyncSessionLocal
            from models.regulation import Regulation
            from sqlalchemy import select, func
            async with AsyncSessionLocal() as db:
                count_res = await db.execute(select(func.count(Regulation.id)))
                count = count_res.scalar() or 0
                if count == 0:
                    logger.info("🌱 Database has 0 regulations. Auto-seeding initial regulatory dataset into DB & Qdrant...")
                    from services.ingestion import ingest_regulation
                    from scripts.seed_demo_data import DEMO_REGULATIONS
                    for r in DEMO_REGULATIONS:
                        try:
                            await ingest_regulation(
                                db=db,
                                title=r["title"],
                                text=r["text"],
                                source=r.get("source", "Standard"),
                                category=r.get("category", "General"),
                                jurisdiction=r.get("jurisdiction", "Global"),
                            )
                        except Exception as reg_err:
                            logger.error(f"Failed to seed {r.get('title')}: {reg_err}")
                    await db.commit()
                    logger.info("✅ Auto-seeding completed.")
                else:
                    logger.info(f"📊 Database already initialized with {count} regulations.")

                # Check if database has any policies; if 0, auto-seed sample policies
                from models.policy import Policy
                pol_count_res = await db.execute(select(func.count(Policy.id)))
                pol_count = pol_count_res.scalar() or 0
                if pol_count == 0:
                    logger.info("🌱 Database has 0 policies. Auto-seeding curated company policies into DB & Qdrant...")
                    from services.ingestion import ingest_policy
                    from scripts.seed_demo_data import SAMPLE_POLICIES
                    for p in SAMPLE_POLICIES:
                        try:
                            await ingest_policy(
                                db=db,
                                title=p["title"],
                                content=p["text"],
                                department=p.get("department", "Compliance"),
                                owner=p.get("owner", "Compliance Officer"),
                            )
                        except Exception as pol_err:
                            logger.error(f"Failed to seed policy {p.get('title')}: {pol_err}")
                    await db.commit()
                    logger.info("✅ Policy auto-seeding completed.")
                else:
                    logger.info(f"📊 Database already initialized with {pol_count} policies.")
        except Exception as e:
            logger.error(f"Error during auto-seeding check: {e}")
        
    asyncio.create_task(startup_tasks())
    
    # Export tokens for external libraries
    if settings.hf_token:
        os.environ["HF_TOKEN"] = settings.hf_token
        os.environ["HUGGING_FACE_HUB_TOKEN"] = settings.hf_token
        
    # Start background scheduler
    start_scheduler()
        
    logger.info("Infrastructure ready.")
    yield
    stop_scheduler()
    logger.info("Shutting down...")


app = FastAPI(
    title="Leagle AI Institutional Protocol",
    version="1.0.0",
    description="Institutional-grade regulatory intelligence engine",
    lifespan=lifespan,
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Leagle AI Institutional Protocol",
        "status": "active",
        "documentation": "/docs",
        "version": "1.0.0",
        "neural_engine": "online"
    }

# ── CORS ─────────────────────────────────────────────────────────────────────
# Pull explicit origins from env; never use * with credentials.
_cors_origins = list(settings.allowed_origins) if settings.allowed_origins else []
if not _cors_origins:
    # Safe dev default
    _cors_origins = ["http://localhost:3000"]

# Also allow all Vercel preview deployment URLs dynamically
_cors_origin_regex = r"https://leagle.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}", "type": type(exc).__name__},
    )

from services.uk_legis_service import sync_uk_feed
from services.sync_manager import sync_all_jurisdictions, sync_jurisdiction
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from fastapi import Depends

@app.post("/api/regulations/sync/uk", dependencies=[Depends(require_admin)])
async def trigger_uk_sync(db: AsyncSession = Depends(get_db)):
    count = await sync_uk_feed(db, limit=10)
    return {"status": "success", "count": count}

@app.post("/api/regulations/sync/all", dependencies=[Depends(require_admin)])
async def trigger_global_sync(db: AsyncSession = Depends(get_db)):
    results = await sync_all_jurisdictions(db, limit_per_source=10)
    return {"status": "success", "results": results}

@app.post("/api/regulations/sync/{jurisdiction}", dependencies=[Depends(require_admin)])
async def trigger_jurisdiction_sync(jurisdiction: str, db: AsyncSession = Depends(get_db)):
    """Trigger a sync for a specific jurisdiction by key (e.g. 'canada', 'japan', 'germany')."""
    count = await sync_jurisdiction(db, jurisdiction=jurisdiction.lower(), limit=10)
    if count == -1:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Unknown jurisdiction '{jurisdiction}'")
    return {"status": "success", "jurisdiction": jurisdiction, "count": count}

# ── Protected routers (Clerk JWT required) ────────────────────────────────────
_auth = [Depends(get_current_user)]

app.include_router(regulations.router, prefix="/api/regulations", tags=["regulations"], dependencies=_auth)
app.include_router(policies.router, prefix="/api/policies", tags=["policies"], dependencies=_auth)
app.include_router(impact.router, prefix="/api/impact", tags=["impact"], dependencies=_auth)
# alerts.router handles its own HTTP auth per route so websocket /ws is not blocked by HTTPBearer
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"], dependencies=_auth)
app.include_router(upload.router, prefix="/api/ingest", tags=["ingest"], dependencies=_auth)
# analytics.router handles its own auth per route so /risk-heatmap is public
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# WhatsApp webhook — Twilio signs its own requests; no Clerk JWT
if settings.enable_whatsapp:
    app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["whatsapp"])

# External public API — uses its own X-Protocol-Key mechanism
app.include_router(public_api_router, prefix="/api/v1/neural", tags=["public-api"])

from sqlalchemy import text

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/health/db")
async def health_check_db(db: AsyncSession = Depends(get_db)):
    """Check database connection explicitly."""
    try:
        await asyncio.wait_for(db.execute(text("SELECT 1")), timeout=5.0)
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        from fastapi import HTTPException
        logger.error(f"Health check DB connection failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
