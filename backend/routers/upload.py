from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
import logging
from core.auth import require_admin
from services.pdf_service import extract_text_from_pdf
from services.chunk_service import split_text
from services.embedding_service import generate_embeddings
from services.qdrant_service import upsert_vectors

logger = logging.getLogger(__name__)
router = APIRouter()

# Configuration
MAX_FILE_SIZE_MB = 50

class IngestionResponse(BaseModel):
    """Response schema for ingestion pipeline"""
    status: str
    message: str
    document_id: str = None
    extraction: dict = None
    chunking: dict = None
    embeddings: dict = None
    pipeline_stats: dict = None


@router.post("/upload", response_model=IngestionResponse, dependencies=[Depends(require_admin)])
async def upload_pdf(file: UploadFile = File(...), debug: bool = False):
    """
    Complete PDF ingestion pipeline: Extract → Chunk → Embed
    
    Args:
        file: PDF file to ingest
        debug: Enable detailed logging and intermediate outputs
        
    Returns:
        IngestionResponse with pipeline results and metadata
    """
    filename = file.filename or "unknown.pdf"
    
    try:
        # Validate file type
        if not filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported"
            )
        
        logger.info(f"Starting ingestion for: {filename}")
        
        # 1. Read PDF
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"File size ({file_size_mb:.2f}MB) exceeds limit ({MAX_FILE_SIZE_MB}MB)"
            )
        
        # 2. Extract text
        extraction_result = extract_text_from_pdf(contents, filename)
        extracted_text = extraction_result["text"]
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from PDF"
            )
        
        logger.info(f"Text extraction complete: {extraction_result['char_count']} chars")
        
        # 3. Chunk text (token-based by default)
        chunking_result = split_text(
            extracted_text,
            chunking_strategy="token"
        )
        chunks = chunking_result["chunks"]
        
        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No chunks generated from extracted text"
            )
        
        logger.info(f"Chunking complete: {len(chunks)} chunks")
        
        # 4. Generate embeddings
        embedding_result = generate_embeddings(chunks, debug=debug)
        embeddings = embedding_result["embeddings"]
        
        if len(embeddings) != len(chunks):
            logger.warning(
                f"Embedding count mismatch: {len(embeddings)} embeddings vs {len(chunks)} chunks"
            )
        
        logger.info(f"Embedding generation complete: {len(embeddings)} embeddings")
        
        # 5. Persist to Qdrant
        metadata = {
            "title": filename,
            "filename": filename,
            "file_size": file_size_mb,
            "num_pages": extraction_result["num_pages"],
            "uploaded": True,
        }
        point_ids = upsert_vectors(
            vectors=embeddings,
            chunks=chunks,
            metadata=metadata,
            source_type="policy" # Tag as policy for comparison against regulations
        )
        
        logger.info(f"Persisted {len(point_ids)} points to Qdrant")
        
        # Compile response
        response_data = {
            "status": "success",
            "message": "PDF ingestion pipeline completed successfully 🚀",
            "document_id": filename,  # In production, use database ID
            "pipeline_stats": {
                "file_size_mb": round(file_size_mb, 2),
                "extracted_chars": extraction_result["char_count"],
                "extracted_pages": extraction_result["num_pages"],
                "num_chunks": len(chunks),
                "num_embeddings": len(embeddings),
                "embedding_model": embedding_result["model"],
                "tokens_used": embedding_result["tokens_used"],
                "chunking_strategy": chunking_result["strategy"]
            }
        }
        
        # Include detailed outputs only in debug mode
        if debug:
            response_data["extraction"] = {
                "char_count": extraction_result["char_count"],
                "num_pages": extraction_result["num_pages"],
                "metadata": extraction_result["metadata"],
                "text_preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
            }
            response_data["chunking"] = {
                "num_chunks": chunking_result["num_chunks"],
                "strategy": chunking_result["strategy"],
                "total_tokens": chunking_result.get("total_tokens", "N/A"),
                "sample_chunks": chunks[:3]  # First 3 chunks for preview
            }
            response_data["embeddings"] = {
                "num_embeddings": len(embeddings),
                "model": embedding_result["model"],
                "tokens_used": embedding_result["tokens_used"],
                "batch_metadata": embedding_result["batch_metadata"]
            }
        
        logger.info(f"Ingestion completed for: {filename}")
        return IngestionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion pipeline failed for {filename}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {str(e)}"
        )