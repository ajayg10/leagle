"""
Quick-Start Dataset Seeding Script

This script seeds Qdrant with built-in regulatory compliance data
for immediate demo/testing without waiting for HuggingFace downloads.

For production use, see seed_datasets.py for full dataset integration.

Usage:
    cd backend && python scripts/seed_demo_data.py
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.qdrant_service import embed_and_upsert, ensure_collection_exists

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Curated regulatory and compliance data for quick seeding
DEMO_REGULATIONS = [
    # GDPR - Data Privacy
    {
        "title": "GDPR Article 5 - Principles of Processing",
        "text": """
        Personal data shall be:
        (a) processed lawfully, fairly and in a transparent manner in relation to the data subject ('lawfulness, fairness and transparency');
        (b) collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes ('purpose limitation');
        (c) adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed ('data minimisation');
        (d) accurate and, where necessary, kept up to date; every reasonable step must be taken to erase or rectify personal data that is inaccurate ('accuracy');
        (e) kept in a form which permits identification of data subjects for no longer than is necessary ('storage limitation');
        (f) processed in a manner that ensures appropriate security of the personal data, including protection against unauthorised or unlawful processing ('integrity and confidentiality').
        """,
        "category": "data_privacy",
        "jurisdiction": "EU",
        "source": "GDPR",
        "article": "Article 5",
    },
    {
        "title": "GDPR Article 32 - Security of Processing",
        "text": """
        Taking into account the state of the art, the costs of implementation and the nature, scope, context and purposes of processing as well as the risk of varying likelihood and severity for the rights and freedoms of natural persons, the controller and processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including, as appropriate:
        (a) the encryption of personal data;
        (b) the ability to ensure the ongoing confidentiality, integrity, availability and resilience of processing systems and services;
        (c) the ability to restore the availability and access to personal data in a timely manner in the event of a physical or technical incident;
        (d) a process for regularly testing, assessing and evaluating the effectiveness of technical and organisational measures for ensuring the security of the processing.
        """,
        "category": "data_privacy",
        "jurisdiction": "EU",
        "source": "GDPR",
        "article": "Article 32",
    },
    {
        "title": "GDPR Article 33 - Notification of a Personal Data Breach",
        "text": """
        In the case of a personal data breach, the controller shall without undue delay and, where feasible, not later than 72 hours after having become aware of the personal data breach, notify the personal data breach to the supervisory authority unless the personal data breach is unlikely to result in a risk to the rights and freedoms of natural persons.
        If the notification to the supervisory authority is not made within 72 hours, it shall be accompanied by reasons for the delay.
        """,
        "category": "data_privacy",
        "jurisdiction": "EU",
        "source": "GDPR",
        "article": "Article 33",
    },
    # India DPDP Act
    {
        "title": "India Digital Personal Data Protection Act - Data Rights",
        "text": """
        The Digital Personal Data Protection Act, 2023 (DPDP Act) establishes the rights of data principals:
        1. Right to notice before data collection
        2. Right to consent before processing
        3. Right to access collected data
        4. Right to correction of inaccurate data
        5. Right to erasure under prescribed circumstances
        6. Right to grievance redressal within 30 days
        
        Class definitions:
        - 'Sensitive Personal Data': financial, health, sexual orientation, genetic, biometric data
        - 'Critical Personal Data': identity documents, payment instruments, precise location
        """,
        "category": "data_privacy",
        "jurisdiction": "India",
        "source": "DPDP Act",
        "article": "Chapter 2",
    },
    # Generic Compliance
    {
        "title": "SOC 2 Type II Compliance - Controls & Procedures",
        "text": """
        SOC 2 Type II audit procedures verify:
        1. Security Controls - Access management, encryption, network security
        2. Availability - System uptime, disaster recovery, backup procedures
        3. Processing Integrity - Complete, accurate, timely processing
        4. Confidentiality - Sensitive info protection and access restrictions
        5. Privacy - Personal data handling per privacy policies
        
        Common findings:
        - Inadequate access controls leading to unauthorized viewing
        - Missing encryption of data in transit
        - Incomplete audit trails and logging
        - Insufficient segregation of duties
        """,
        "category": "compliance",
        "jurisdiction": "US",
        "source": "SOC 2",
        "article": "Type II Audit",
    },
    # Finance/Payments
    {
        "title": "PCI-DSS Data Security Standard - Payment Processing",
        "text": """
        Payment Card Industry Data Security Standard (PCI-DSS) v3.2.1 requires:
        
        Requirement 1: Install and maintain firewall configuration
        Requirement 2: Do not use vendor-supplied defaults
        Requirement 3: Protect stored cardholder data
        Requirement 4: Encrypt transmission of cardholder data across public networks
        Requirement 5: Use and regularly update anti-virus software
        Requirement 6: Develop secure systems and applications
        Requirement 7: Restrict access to cardholder data by business need
        Requirement 8: Assign unique ID to each person with computer access
        Requirement 9: Restrict physical access to cardholder data
        Requirement 10: Track and monitor access to network resources
        """,
        "category": "financial",
        "jurisdiction": "Global",
        "source": "PCI-DSS",
        "article": "v3.2.1",
    },
]

# Sample company policies for testing impact analysis
SAMPLE_POLICIES = [
    {
        "title": "Data Retention Policy",
        "text": """
        Our organization retains personal data for as long as necessary to fulfill the purposes for which it was collected,
        or as required by law. Retention periods vary by data type:
        
        - Customer contact data: 5 years after last interaction
        - Financial records: 7 years per legal requirement
        - HR personnel files: 3 years after employment termination
        - Server logs: 90 days
        - CCTV footage: 30 days
        
        Deletion is performed securely using certified data destruction methods.
        """,
        "category": "data_privacy",
        "department": "Legal",
    },
    {
        "title": "Access Control and Authentication Policy",
        "text": """
        All systems shall enforce multi-factor authentication (MFA) for:
        - Administrative accounts (required before deployment)
        - Employee VPN access (RSA tokens or authenticator apps)
        - Database access from non-production networks
        
        Password requirements:
        - Minimum 12 characters
        - Mixed case, numbers, special characters
        - Change every 90 days for admin accounts
        - Change every 180 days for regular users
        
        Privileged access review performed quarterly with audit logging.
        """,
        "category": "security",
        "department": "IT",
    },
    {
        "title": "Incident Response and Breach Notification",
        "text": """
        Upon discovery of a security incident or data breach:
        
        1. Within 1 hour: Notify CISO and incident response team
        2. Within 24 hours: Preliminary assessment of scope and impact
        3. Within 72 hours: Notification to regulatory authorities if required
        4. Within 3 days: Customer notification if personal data at risk
        5. Ongoing: Forensic investigation and root cause analysis
        
        Documentation includes: timeline, affected data, remediation steps, preventative measures.
        Annual breach simulation testing mandatory.
        """,
        "category": "incident_management",
        "department": "Security",
    },
    {
        "title": "Financial Reporting and Audit Policy",
        "text": """
        This policy governs the accuracy and transparency of financial disclosures:
        1. All revenue must be recognized in accordance with GAAP standards.
        2. Monthly reconciliation of all corporate accounts is mandatory.
        3. External audits will be conducted annually to verify balance sheet integrity.
        4. Any discrepancy over $10,000 must be reported to the Audit Committee.
        
        Failure to comply may lead to regulatory sanctions and internal disciplinary action.
        """,
        "category": "financial",
        "department": "Finance",
    },
    {
        "title": "Recruitment and Equal Opportunity Policy",
        "text": """
        Our hiring practices ensure fairness and diversity:
        1. All job descriptions must use gender-neutral language.
        2. Background checks are required for all permanent employees.
        3. Employee data (IDs, addresses) must be stored in encrypted HR systems.
        4. Interviews must be conducted by at least two different team members to avoid bias.
        
        Personal data of unsuccessful candidates is deleted after 6 months.
        """,
        "category": "data_privacy",
        "department": "HR",
    },
    {
        "title": "Ethical Marketing and Advertising Policy",
        "text": """
        All marketing materials must be truthful and compliant:
        1. No deceptive claims about product performance are permitted.
        2. Email marketing must include a clear 'unsubscribe' option.
        3. Customer testimonial data must be used only with written consent.
        4. Competitive comparisons must be based on objective, third-party data.
        """,
        "category": "compliance",
        "department": "Marketing",
    },
]


def seed_demo_data() -> int:
    """Seed built-in compliance and regulatory data into Qdrant"""
    
    print("\n" + "="*80)
    print("CODEWIZARDS - QUICK START DATA SEEDING")
    print("="*80 + "\n")
    
    # Ensure collection exists
    print("Step 1: Initializing Qdrant...")
    try:
        ensure_collection_exists()
        print("✅ Qdrant collection ready\n")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 0
    
    # Seed regulations
    print("Step 2: Seeding regulatory compliance data...")
    total_chunks = 0
    
    for reg in DEMO_REGULATIONS:
        try:
            metadata = {
                "title": reg["title"],
                "category": reg["category"],
                "jurisdiction": reg["jurisdiction"],
                "source": reg["source"],
                "article": reg.get("article", ""),
            }
            
            chunk_ids = embed_and_upsert(
                text=reg["text"],
                metadata=metadata,
                source_type="regulation",
            )
            total_chunks += len(chunk_ids)
            print(f"  ✅ {reg['source']:10} | {reg['title'][:40]:40} | {len(chunk_ids)} chunks")
        
        except Exception as e:
            logger.error(f"  ❌ Error seeding {reg['title']}: {e}")
    
    # Seed policies
    print("\nStep 3: Seeding sample company policies...")
    for policy in SAMPLE_POLICIES:
        try:
            metadata = {
                "title": policy["title"],
                "category": policy["category"],
                "department": policy["department"],
                "source": "company_policy",
            }
            
            chunk_ids = embed_and_upsert(
                text=policy["text"],
                metadata=metadata,
                source_type="policy",
            )
            total_chunks += len(chunk_ids)
            print(f"  ✅ {policy['department']:10} | {policy['title'][:40]:40} | {len(chunk_ids)} chunks")
        
        except Exception as e:
            logger.error(f"  ❌ Error seeding {policy['title']}: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("SEEDING COMPLETE")
    print("="*80)
    print(f"\n📊 Total chunks seeded: {total_chunks}")
    print(f"\nYour Qdrant database now contains {total_chunks} regulatory & policy chunks.")
    print("\nReady to test:")
    print("  1. POST /api/regulations/ingest - Upload a new regulation")
    print("  2. POST /api/impact/analyze - Analyze impact on policies")
    print("  3. POST /api/rag/explain - Q&A over regulations")
    print("  4. GET  /api/regulations/{id}/similar - Find similar regulations")
    print("\n" + "="*80 + "\n")
    
    return total_chunks


if __name__ == "__main__":
    try:
        total = seed_demo_data()
        sys.exit(0 if total > 0 else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
