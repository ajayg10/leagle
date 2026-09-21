import tiktoken
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Configuration
TOKEN_CHUNK_SIZE = 512  # Tokens per chunk (optimal for embeddings)
TOKEN_OVERLAP = 100    # Tokens overlap between chunks
CHAR_CHUNK_SIZE = 500  # Fallback for character-based chunking
CHAR_OVERLAP = 50

def split_text(
    text: str, 
    chunking_strategy: str = "token",
    chunk_size: int = None,
    overlap: int = None
) -> Dict:
    """
    Split text into chunks with support for token-based or character-based chunking.
    
    Args:
        text: Input text to split
        chunking_strategy: "token" (recommended) or "character"
        chunk_size: Override default chunk size
        overlap: Override default overlap
        
    Returns:
        dict: {
            "chunks": [chunk_strings],
            "num_chunks": int,
            "chunk_metadata": [{chunk_info}],
            "strategy": str,
            "total_tokens": int (if token-based)
        }
    """
    if not text or not text.strip():
        raise ValueError("Cannot chunk empty text")
    
    try:
        if chunking_strategy == "token":
            return _split_by_tokens(text, chunk_size, overlap)
        else:
            return _split_by_characters(text, chunk_size, overlap)
    except Exception as e:
        logger.error(f"Chunking failed: {str(e)}")
        raise


def _split_by_tokens(text: str, chunk_size: int = None, overlap: int = None) -> Dict:
    """
    Token-based chunking using tiktoken.
    Respects semantic boundaries and is optimal for embedding models.
    """
    chunk_size = chunk_size or TOKEN_CHUNK_SIZE
    overlap = overlap or TOKEN_OVERLAP
    
    try:
        encoding = tiktoken.get_encoding("cl100k_base")  # GPT-3.5/4 tokenizer
        tokens = encoding.encode(text)
        
        total_tokens = len(tokens)
        chunks = []
        chunk_metadata = []
        
        # Create chunks with overlap
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = encoding.decode(chunk_tokens)
            
            chunks.append(chunk_text)
            chunk_metadata.append({
                "chunk_id": len(chunks) - 1,
                "token_count": len(chunk_tokens),
                "char_count": len(chunk_text),
                "start_token": i,
                "end_token": min(i + chunk_size, len(tokens))
            })
        
        logger.info(
            f"Token-based chunking successful | "
            f"Total tokens: {total_tokens} | "
            f"Chunks: {len(chunks)} | "
            f"Avg tokens/chunk: {total_tokens // max(len(chunks), 1)}"
        )
        
        return {
            "chunks": chunks,
            "num_chunks": len(chunks),
            "chunk_metadata": chunk_metadata,
            "strategy": "token",
            "total_tokens": total_tokens,
            "chunk_size_tokens": chunk_size,
            "overlap_tokens": overlap
        }
        
    except Exception as e:
        logger.error(f"Token-based chunking failed: {str(e)}. Falling back to character-based.")
        return _split_by_characters(text, CHAR_CHUNK_SIZE, CHAR_OVERLAP)


def _split_by_characters(text: str, chunk_size: int = None, overlap: int = None) -> Dict:
    """
    Character-based chunking. Simpler but doesn't respect token boundaries.
    Use when token-based chunking fails.
    """
    chunk_size = chunk_size or CHAR_CHUNK_SIZE
    overlap = overlap or CHAR_OVERLAP
    
    chunks = []
    chunk_metadata = []
    
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
        chunk_metadata.append({
            "chunk_id": len(chunks) - 1,
            "char_count": len(chunk),
            "start_char": i,
            "end_char": min(i + chunk_size, len(text))
        })
    
    logger.info(
        f"Character-based chunking | "
        f"Total chars: {len(text)} | "
        f"Chunks: {len(chunks)} | "
        f"Avg chars/chunk: {len(text) // max(len(chunks), 1)}"
    )
    
    return {
        "chunks": chunks,
        "num_chunks": len(chunks),
        "chunk_metadata": chunk_metadata,
        "strategy": "character",
        "total_chars": len(text),
        "chunk_size_chars": chunk_size,
        "overlap_chars": overlap
    }