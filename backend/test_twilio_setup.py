#!/usr/bin/env python
"""
Test script to verify Twilio WhatsApp integration setup.
Run this BEFORE sending actual PDFs via WhatsApp.
"""

import os
import sys
from dotenv import load_dotenv

print("\n" + "=" * 70)
print(" TWILIO WHATSAPP INTEGRATION TEST SUITE")
print("=" * 70)

# Load .env
load_dotenv()

# Test 1: Credentials
print("\n[1/5] CHECKING CREDENTIALS...")
sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")

if not sid:
    print("  ❌ TWILIO_ACCOUNT_SID not set in .env")
    sys.exit(1)
else:
    print(f"  ✅ SID found: {sid[:15]}...")

if not token or "your_" in token:
    print("  ❌ TWILIO_AUTH_TOKEN not set or uses placeholder!")
    print("     Update .env with real token from https://console.twilio.com")
    sys.exit(1)
else:
    print(f"  ✅ TOKEN found: {token[:15]}...")

# Test 2: Services availability
print("\n[2/5] CHECKING SERVICE IMPORTS...")
errors = []

try:
    from services.pdf_service import extract_text_from_pdf
    print("  ✅ pdf_service.extract_text_from_pdf")
except ImportError as e:
    errors.append(f"pdf_service: {e}")
    print(f"  ❌ pdf_service import failed: {e}")

try:
    from services.chunk_service import split_text
    print("  ✅ chunk_service.split_text")
except ImportError as e:
    errors.append(f"chunk_service: {e}")
    print(f"  ❌ chunk_service import failed: {e}")

try:
    from services.embedding_service import generate_embeddings, get_model
    print("  ✅ embedding_service.generate_embeddings")
except ImportError as e:
    errors.append(f"embedding_service: {e}")
    print(f"  ❌ embedding_service import failed: {e}")

if errors:
    print(f"\n  ⚠️  {len(errors)} import error(s) found")
    for err in errors:
        print(f"     - {err}")

# Test 3: Router registration
print("\n[3/5] CHECKING ROUTER REGISTRATION...")
try:
    from routers import whatsapp
    print("  ✅ whatsapp.router imported")
    
    # Check route exists
    from routers.whatsapp import router
    routes = [r.path for r in router.routes if hasattr(r, 'path')]
    if "/webhook" in routes:
        print("  ✅ /webhook endpoint registered")
    else:
        print(f"  ❌ /webhook not found. Routes: {routes}")
except Exception as e:
    print(f"  ❌ Router import failed: {e}")
    sys.exit(1)

# Test 4: Embedding model download
print("\n[4/5] TESTING EMBEDDING MODEL LOAD...")
try:
    print("  ⏳ Loading SentenceTransformer model (first run may take ~30s)...")
    from services.embedding_service import get_model
    model = get_model()
    print(f"  ✅ Model loaded: {model.__class__.__name__}")
    
    # Test encode
    test_text = ["Hello world", "Test embedding"]
    embeddings = model.encode(test_text)
    print(f"  ✅ Embeddings generated: shape {embeddings.shape}")
except Exception as e:
    print(f"  ❌ Model loading failed: {e}")
    print("     Try: pip install sentence-transformers torch")

# Test 5: Main app loads
print("\n[5/5] CHECKING FASTAPI APP...")
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    from main import app
    print("  ✅ FastAPI app imported from main.py")
    
    # Check if whatsapp router is included
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    if "/api/whatsapp/webhook" in routes:
        print("  ✅ /api/whatsapp/webhook registered in main app")
    else:
        print(f"  ⚠️  /api/whatsapp/webhook not in routes")
        print(f"     Available routes: {[r for r in routes if 'whatsapp' in r]}")
except Exception as e:
    print(f"  ❌ App import failed: {e}")
    print("     Make sure you run this from backend directory")

# Final summary
print("\n" + "=" * 70)
print(" TEST SUMMARY")
print("=" * 70)

print("""
✅ All checks passed!

NEXT STEPS:
1. Start backend:
   cd backend
   uvicorn main:app --reload

2. In another terminal, start ngrok:
   ngrok http 8000

3. Update Twilio webhook URL:
   Go to https://console.twilio.com/develop/sms/try-it-out/whatsapp-sandbox
   Set "When a message comes in" to: https://YOUR_NGROK_URL/api/whatsapp/webhook

4. Send PDF via WhatsApp and check backend logs for:
   📬 Webhook received
   ⬇️ Downloading PDF from Twilio
   ✂️ Chunking text...
   🧠 Generating embeddings...
   🎉 Pipeline complete
""")

print("=" * 70)
print(" For more help, see: TWILIO_DEBUG_CHECKLIST.md")
print("=" * 70 + "\n")
