from pypdf import PdfReader
import io
import logging

logger = logging.getLogger(__name__)

# Configuration
MAX_PDF_SIZE_MB = 50
MAX_CHARS_PER_PAGE = 100000

def extract_text_from_pdf(file_bytes, filename: str = ""):
    """
    Extract text from PDF with validation and logging.
    
    Args:
        file_bytes: PDF file content as bytes
        filename: Original filename for logging context
        
    Returns:
        dict: {
            "text": extracted_text,
            "num_pages": int,
            "char_count": int,
            "metadata": dict
        }
    """
    try:
        # Validate file size
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > MAX_PDF_SIZE_MB:
            raise ValueError(f"PDF size ({size_mb:.2f}MB) exceeds max allowed ({MAX_PDF_SIZE_MB}MB)")
        
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        page_metadata = []
        
        # Extract text with per-page tracking
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""
            
            # Validate page size
            if len(page_text) > MAX_CHARS_PER_PAGE:
                logger.warning(
                    f"Page {page_num} exceeds char limit: {len(page_text)} chars. "
                    f"Truncating for {filename}"
                )
                page_text = page_text[:MAX_CHARS_PER_PAGE]
            
            text += page_text
            page_metadata.append({
                "page_num": page_num,
                "char_count": len(page_text),
                "extracted": len(page_text) > 0
            })
        
        # Validate extraction
        if not text.strip():
            raise ValueError("No text could be extracted from PDF (possibly image-based)")
        
        logger.info(
            f"PDF extraction successful: {filename} | "
            f"Pages: {len(reader.pages)} | Chars: {len(text)} | Size: {size_mb:.2f}MB"
        )
        
        return {
            "text": text,
            "num_pages": len(reader.pages),
            "char_count": len(text),
            "metadata": {
                "filename": filename,
                "file_size_mb": round(size_mb, 2),
                "pages_extracted": sum(1 for p in page_metadata if p["extracted"]),
                "page_details": page_metadata
            }
        }
        
    except Exception as e:
        logger.error(f"PDF extraction failed for {filename}: {str(e)}")
        raise