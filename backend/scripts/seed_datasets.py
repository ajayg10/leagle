"""
Master Dataset Seeding Script

This script populates Qdrant with:
1. SEC Forms (10-K) - Corporate compliance benchmark
2. Regulatory Data (GDPR, DPDP Act, LexGLUE) - Legal reference
3. Prepares Legal Case Data - Risk scorer training

Usage:
    cd backend && python scripts/seed_datasets.py

Or with options:
    python scripts/seed_datasets.py --sec-only
    python scripts/seed_datasets.py --regulatory-only
    python scripts/seed_datasets.py --prepare-ml-data
    python scripts/seed_datasets.py --all
"""

import sys
import os
import argparse
import asyncio
import logging
from typing import Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.dataset_loader import (
    SECDatasetSeeder,
    LegalCaseDatasetPreparer,
    RegulatoryDatasetSeeder,
)
from services.qdrant_service import ensure_collection_exists

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def seed_all_datasets(
    seed_sec: bool = True,
    seed_regulatory: bool = True,
    prepare_ml: bool = True,
    sec_max_companies: int = 100,
) -> Dict[str, int]:
    """
    Seed all datasets into Qdrant.
    
    Returns:
        Dict with counts of what was seeded
    """
    results = {}
    
    print("\n" + "="*80)
    print("CODEWIZARDS AI COMPLIANCE SYSTEM - DATASET SEEDING")
    print("="*80)
    
    # Ensure Qdrant collection exists
    print("\n[1/4] Ensuring Qdrant collection...")
    try:
        ensure_collection_exists()
        print("✅ Qdrant collection ready\n")
    except Exception as e:
        print(f"❌ Error ensuring Qdrant collection: {e}")
        return results
    
    # Seed SEC Dataset
    if seed_sec:
        print("[2/4] Seeding SEC Form 10-K Dataset...")
        print("     (Corporate compliance benchmark - Hybrid Storage Active)")
        try:
            sec_chunks = await SECDatasetSeeder.seed_sec_data(
                max_companies=sec_max_companies,
                max_documents_per_company=1,
                summarize=True,
            )
            results["sec_chunks"] = sec_chunks
        except Exception as e:
            logger.error(f"Error seeding SEC data: {e}")
            results["sec_chunks"] = 0
    else:
        print("[2/4] ⊘ Skipping SEC Dataset")
    
    # Seed Regulatory Dataset
    if seed_regulatory:
        print("\n[3/4] Seeding Regulatory Data...")
        print("     (GDPR, DPDP Act, LexGLUE benchmark)")
        try:
            reg_chunks = RegulatoryDatasetSeeder.seed_regulatory_data()
            lex_chunks = RegulatoryDatasetSeeder.seed_from_lexglue()
            gdpr_chunks = await RegulatoryDatasetSeeder.seed_gdpr_cases(max_samples=500)
            custom_chunks = RegulatoryDatasetSeeder.seed_custom_training_data()
            results["regulatory_chunks"] = reg_chunks + lex_chunks + gdpr_chunks + custom_chunks
        except Exception as e:
            logger.error(f"Error seeding regulatory data: {e}")
            results["regulatory_chunks"] = 0
    else:
        print("\n[3/4] ⊘ Skipping Regulatory Dataset")
    
    # Prepare ML Training Data
    if prepare_ml:
        print("\n[4/4] Preparing Legal Case Data for ML Risk Scorer...")
        print("     (Training data for predicting risk levels 0-100)")
        try:
            ml_samples = LegalCaseDatasetPreparer.prepare_legal_case_data(
                output_file="backend/ml/legal_training_data.jsonl",
                max_samples=5000,
            )
            results["ml_training_samples"] = ml_samples
        except Exception as e:
            logger.error(f"Error preparing ML data: {e}")
            results["ml_training_samples"] = 0
    else:
        print("\n[4/4] ⊘ Skipping ML Data Preparation")
    
    # Summary
    print("\n" + "="*80)
    print("SEEDING COMPLETE - SUMMARY")
    print("="*80)
    
    total_qdrant_chunks = results.get("sec_chunks", 0) + results.get("regulatory_chunks", 0)
    
    print(f"\n✅ SEC Dataset:              {results.get('sec_chunks', 0):,} chunks")
    print(f"✅ Regulatory Dataset:       {results.get('regulatory_chunks', 0):,} chunks")
    print(f"✅ ML Training Samples:      {results.get('ml_training_samples', 0):,} samples")
    print(f"\n📊 Total Qdrant Vectors:     {total_qdrant_chunks:,}")
    
    if total_qdrant_chunks > 0:
        print(f"\n🎯 Your Qdrant database now contains {total_qdrant_chunks:,} regulatory/compliance chunks.")
        print("   When you ingest a new policy, the system will:")
        print("   1. Search Qdrant for similar regulations")
        print("   2. Compare against SEC benchmark practices")
        print("   3. Predict risk level using the trained ML model")
        print("   4. Generate remediation recommendations via Gemini API")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Ingest your company policies via the FastAPI endpoint")
    print("2. Upload a new regulation and trigger impact analysis")
    print("3. Watch Qdrant find similar docs + ML score the risk")
    print("\nConsult README.md and LLM.md for full API documentation.")
    print("="*80 + "\n")
    
    return results


def main():
    """CLI entrypoint"""
    parser = argparse.ArgumentParser(
        description="Seed CodeWizards compliance system with regulatory datasets"
    )
    parser.add_argument(
        "--sec-only",
        action="store_true",
        help="Seed only SEC dataset"
    )
    parser.add_argument(
        "--regulatory-only",
        action="store_true",
        help="Seed only regulatory data"
    )
    parser.add_argument(
        "--prepare-ml-data",
        action="store_true",
        help="Prepare ML training data only"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Seed everything (default if no flag specified)"
    )
    parser.add_argument(
        "--sec-companies",
        type=int,
        default=100,
        help="Max SEC companies to load (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Determine what to seed
    seed_sec = seed_regulatory = prepare_ml = False
    
    if args.sec_only:
        seed_sec = True
    elif args.regulatory_only:
        seed_regulatory = True
    elif args.prepare_ml_data:
        prepare_ml = True
    else:
        # Default: seed everything
        seed_sec = seed_regulatory = prepare_ml = True
    
    # Run seeding
    results = asyncio.run(seed_all_datasets(
        seed_sec=seed_sec,
        seed_regulatory=seed_regulatory,
        prepare_ml=prepare_ml,
        sec_max_companies=args.sec_companies,
    ))
    
    # Exit with appropriate code
    if results.get("sec_chunks", 0) + results.get("regulatory_chunks", 0) + results.get("ml_training_samples", 0) > 0:
        sys.exit(0)
    else:
        print("⚠️  No data was seeded. Check logs for errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
