from sentence_transformers import SentenceTransformer
import logging
import numpy as np
from typing import List, Dict

logger = logging.getLogger(__name__)

# Lazy-load model to avoid loading at startup
_model = None


def get_model():
    """Get or create embedding model with lazy initialization."""
    global _model
    if _model is None:
        logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("✅ Embedding model loaded successfully")
    return _model


# Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 32


def generate_embeddings(chunks: List[str], debug: bool = False) -> Dict:
    """
    Generate embeddings for text chunks using SentenceTransformer.
    """

    if not chunks or len(chunks) == 0:
        raise ValueError("No chunks provided for embedding")

    try:
        model = get_model()
        all_embeddings = []
        batch_metadata = []
        embedding_dim = 0

        # Calculate number of batches
        num_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

        for batch_num in range(num_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(chunks))
            batch_chunks = chunks[start_idx:end_idx]

            batch_info = {
                "batch_id": batch_num,
                "chunk_count": len(batch_chunks),
                "start_idx": start_idx,
                "end_idx": end_idx,
                "chunk_sizes": [len(c) for c in batch_chunks],
                "status": "pending"
            }

            try:
                # Generate embeddings
                embeddings = model.encode(batch_chunks, convert_to_tensor=False)

                # Convert numpy array to list of lists
                if isinstance(embeddings, np.ndarray):
                    embeddings_list = embeddings.tolist()
                    if embedding_dim == 0:
                        embedding_dim = embeddings.shape[1]
                else:
                    embeddings_list = embeddings

                all_embeddings.extend(embeddings_list)

                batch_info["status"] = "success"
                batch_info["embedding_count"] = len(embeddings_list)
                batch_info["embedding_dim"] = embedding_dim

                logger.info(
                    f"Batch {batch_num + 1}/{num_batches} processed successfully | "
                    f"Chunks: {len(batch_chunks)} | "
                    f"Embeddings: {len(embeddings_list)} | "
                    f"Dimension: {embedding_dim}"
                )

            except Exception as e:
                batch_info["status"] = "failed"
                batch_info["error"] = str(e)
                logger.error(f"Batch {batch_num + 1} failed: {str(e)}")
                raise

            batch_metadata.append(batch_info)

        # Ensure all_embeddings is a proper list
        total_embeddings = len(all_embeddings) if isinstance(all_embeddings, list) else 0

        logger.info(
            f"Embedding generation complete | "
            f"Total chunks: {len(chunks)} | "
            f"Total embeddings: {total_embeddings} | "
            f"Batches: {num_batches}"
        )

        return {
            "embeddings": all_embeddings,
            "num_embeddings": total_embeddings,
            "batches_processed": num_batches,
            "batch_metadata": batch_metadata if debug else None,
            "model": EMBEDDING_MODEL,
            "embedding_dim": embedding_dim,
            "tokens_used": 0,
            "debug": debug
        }

    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise