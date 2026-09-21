"""
Test script for Qdrant integration.
Verifies that embedding, upserting, and searching work end-to-end.

Usage:
    cd backend && python scripts/test_qdrant.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.qdrant_service import (
    ensure_collection_exists,
    embed_and_upsert,
    semantic_search,
)

def main():
    print("\n" + "="*80)
    print("QDRANT INTEGRATION TEST")
    print("="*80 + "\n")
    
    # Step 1: Ensure collection exists
    print("Step 1: Ensuring Qdrant collection exists...")
    try:
        ensure_collection_exists()
        print("✅ Collection ready\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False
    
    # Step 2: Embed and upsert sample regulation
    print("Step 2: Embedding and upserting sample GDPR regulation...")
    sample_text = """
    GDPR Article 83 - Penalties
    
    1. In the case of an infringement of this Regulation, in addition to or instead of any other 
    administrative or non-administrative sanctions available under Union or Member State law, the 
    competent authority may impose administrative fines up to EUR 20 000 000, or in the case of an 
    enterprise, in addition to or instead of any other administrative or non-administrative sanctions 
    available under Union or Member State law, up to 4 % of the annual worldwide turnover, whichever is higher.
    
    2. Infringements of the following provisions shall be subject to administrative fines up to 
    EUR 10 000 000, or in the case of an enterprise, in addition to or instead of any other 
    administrative or non-administrative sanctions available under Union or Member State law, up to 2 % 
    of the annual worldwide turnover, whichever is higher.
    """
    
    try:
        metadata = {
            "regulation_id": "gdpr-article-83",
            "title": "GDPR Article 83 - Penalties",
            "category": "data_privacy",
            "jurisdiction": "EU",
            "source": "eu.gdpr",
        }
        ids = embed_and_upsert(sample_text, metadata, source_type="regulation")
        print(f"✅ Upserted {len(ids)} chunks\n")
        print(f"   Chunk IDs: {ids}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False
    
    # Step 3: Perform semantic search
    print("Step 3: Performing semantic search...")
    queries = [
        "What are the penalties for data privacy violations?",
        "GDPR fines and sanctions",
        "data breach notification requirements",
    ]
    
    for query in queries:
        print(f"\n   Query: \"{query}\"")
        try:
            results = semantic_search(query, top_k=3, score_threshold=0.3)
            if results:
                for i, result in enumerate(results, 1):
                    print(f"   [{i}] Score: {result['score']:.3f} | {result['title']}")
                    print(f"       Text: {result['text'][:80]}...")
            else:
                print("   (no results)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80 + "\n")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
