from fastapi import APIRouter, Request, BackgroundTasks
from twilio.rest import Client
from fastapi.responses import Response
import requests
import os
import logging

# Import your existing pipeline services
from services.pdf_service import extract_text_from_pdf
from services.chunk_service import split_text
from services.embedding_service import generate_embeddings
from services.intel_service import RegulationIntelligenceService
from services.qdrant_service import upsert_vectors
from services.risk_scorer import score_regulation

router = APIRouter()
logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

logger.info(f"✅ Twilio initialized: SID={TWILIO_ACCOUNT_SID[:10] if TWILIO_ACCOUNT_SID else 'NOT SET'}...")


@router.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Complete Twilio WhatsApp PDF ingestion workflow.
    Flow: Download PDF → Ack → Background Process (Extract → Chunk → Embed → Store → Report)
    """
    try:
        # 1️⃣ Parse Twilio form data
        form = await request.form()
        logger.info(f"📬 Webhook received | Form keys: {list(form.keys())}")
        
        from_number = form.get("From", "unknown")
        num_media = int(form.get("NumMedia", 0))
        logger.info(f"📲 Message from: {from_number} | Media count: {num_media}")

        # 2️⃣ Check if media attached
        if num_media == 0:
            logger.warning("⚠️ No media received")
            return _twilio_response("Please send a PDF file 📄")

        # 3️⃣ Extract media URL and type
        media_url = form.get("MediaUrl0")
        media_type = form.get("MediaContentType0")
        logger.info(f"📎 Media: {media_type} | URL: {media_url[:50]}...")

        # 4️⃣ Validate PDF
        if not media_type or "pdf" not in media_type.lower():
            logger.warning(f"❌ Invalid media type: {media_type}")
            return _twilio_response("Only PDF files are supported 📄")

        # 5️⃣ Download PDF from Twilio (Sync download to ensure URL validity)
        try:
            logger.info(f"⬇️  Downloading PDF from Twilio...")
            response = requests.get(
                media_url,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                timeout=30
            )
            response.raise_for_status()
            pdf_bytes = response.content
            logger.info(f"✅ PDF downloaded: {len(pdf_bytes)} bytes")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to download PDF: {str(e)}")
            return _twilio_response(f"❌ Failed to download PDF. Try again.")

        # 🚀 TRIGGER BACKGROUND TASK
        background_tasks.add_task(process_whatsapp_workflow, pdf_bytes, from_number)
        
        # 6️⃣ Return immediate acknowledgment
        return _twilio_response("📄 RECEIVED! I am analyzing your PDF document now. This take a few moments. I'll send the report here shortly!")

    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {str(e)}", exc_info=True)
        return _twilio_response("❌ An unexpected error occurred. Try again.")


async def process_whatsapp_workflow(pdf_bytes: bytes, from_number: str):
    """Background task to handle heavy processing and send outbound reply."""
    logger.info(f"🔄 Starting background workflow for {from_number}")
    
    # Initialize Twilio client for outbound messages
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    whatsapp_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

    try:
        # 1️⃣ Extract text from PDF
        logger.info(f"🔄 Extracting text...")
        extraction_result = extract_text_from_pdf(pdf_bytes, "whatsapp_media.pdf")
        extracted_text = extraction_result["text"]
        num_pages = extraction_result["num_pages"]
        char_count = extraction_result["char_count"]
        
        if not extracted_text.strip():
            _send_whatsapp_outbound(client, whatsapp_from, from_number, "❌ No text found in PDF. Try another file.")
            return

        # 2️⃣ Chunk text
        logger.info(f"✂️  Chunking text...")
        chunking_result = split_text(extracted_text, chunking_strategy="token")
        chunks = chunking_result["chunks"]

        # 3️⃣ Generate embeddings
        logger.info(f"🧠 Generating embeddings...")
        embedding_result = generate_embeddings(chunks, debug=False)
        embeddings = embedding_result["embeddings"]
        num_embeddings = embedding_result["num_embeddings"]

        # 4️⃣ Store in Qdrant
        try:
            logger.info(f"💾 Storing vectors in Qdrant...")
            metadata = {
                "title": "WhatsApp PDF",
                "filename": "whatsapp_media.pdf",
                "source": "whatsapp",
                "sender": from_number,
                "num_pages": num_pages,
                "char_count": char_count,
            }
            upsert_vectors(
                vectors=embeddings,
                chunks=chunks,
                metadata=metadata,
                source_type="policy"
            )
        except Exception as qe:
            logger.error(f"❌ Qdrant storage failed: {str(qe)}")

        # 5️⃣ Generate Intelligence Report
        logger.info(f"🧠 Generating Intelligence Profile...")
        analysis_snippet = extracted_text[:10000]
        
        try:
            intel = await RegulationIntelligenceService.get_regulation_intel(
                title="WhatsApp Ingested Policy",
                text=analysis_snippet
            )
            
            risk_score = intel.get('risk_score', 5)
            explanation = intel.get('explanation', 'Document analyzed')[:400]
            impact_areas = intel.get('impact_areas', ['General'])
            
            report_msg = (
                f"📊 POLICY ANALYSIS COMPLETE\n\n"
                f"Pages: {num_pages}\n"
                f"Chunks: {len(chunks)}\n"
                f"Risk Score: {risk_score}/10\n\n"
                f"Summary:\n{explanation}\n\n"
                f"Impact Areas: {', '.join(impact_areas[:3])}\n\n"
                f"✅ Indexed & Secured"
            )
        except Exception as ie:
            logger.error(f"⚠️ Intelligence Profile failed: {str(ie)}")
            report_msg = (
                f"✅ PDF INGESTED SUCCESS\n\n"
                f"Pages: {num_pages}\n"
                f"Chunks: {len(chunks)}\n"
                f"Embeddings: {num_embeddings}\n\n"
                f"Document indexed successfully, but AI analysis failed."
            )

        # 6️⃣ Send Outbound Notification
        logger.info(f"📤 Sending final report to {from_number}")
        _send_whatsapp_outbound(client, whatsapp_from, from_number, report_msg)
        logger.info(f"🎉 Background pipeline complete for {from_number}")

    except Exception as e:
        logger.error(f"❌ Background process error: {str(e)}", exc_info=True)
        _send_whatsapp_outbound(client, whatsapp_from, from_number, f"❌ Sorry, an error occurred while processing your PDF: {str(e)}")


def _send_whatsapp_outbound(client: Client, from_num: str, to_num: str, message: str):
    """Helper to send outbound WhatsApp message."""
    try:
        # Truncate to 1600 chars (WhatsApp limit)
        if len(message) > 1550:
            message = message[:1547] + "..."
            
        client.messages.create(
            from_=from_num,
            body=message,
            to=to_num
        )
    except Exception as e:
        logger.error(f"❌ Failed to send Twilio outbound: {str(e)}")


def _twilio_response(message: str) -> Response:
    """Send a simple TwiML message response."""
    # Truncate if too long
    if len(message) > 1000:
        message = message[:997] + "..."
    
    # Escape special XML characters
    message = (message.replace("&", "&amp;")
                      .replace("<", "&lt;")
                      .replace(">", "&gt;")
                      .replace('"', "&quot;")
                      .replace("'", "&apos;"))
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""
    
    return Response(content=twiml, media_type="application/xml")