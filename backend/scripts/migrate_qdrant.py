import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
LOCAL_HOST = "localhost"
LOCAL_PORT = 6333
CLOUD_URL = "https://f1d87fa6-88e7-4b73-907f-14f94da2a085.eu-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6YTE0ZTFiNGYtY2UzYy00NDgxLTgyMjAtNWI1ZTZkOWQyYjQ3In0.NwDNIlA9bCipek8fa_yGfgimGIG6s88_MeTpY4PFq7M"
COLLECTION_NAME = "regulations_v1"
VECTOR_SIZE = 384

def migrate():
    # 1. Connect to both
    logger.info("🔌 Connecting to local and cloud Qdrant...")
    local_client = QdrantClient(host=LOCAL_HOST, port=LOCAL_PORT)
    cloud_client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY)

    # 2. Ensure cloud collection exists
    try:
        collections = cloud_client.get_collections()
        if not any(c.name == COLLECTION_NAME for c in collections.collections):
            logger.info(f"🆕 Creating collection '{COLLECTION_NAME}' on cloud...")
            cloud_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
    except Exception as e:
        logger.error(f"❌ Error checking cloud collections: {e}")
        return

    # 3. Scroll all points from local
    logger.info(f"📜 Extracting data from local '{COLLECTION_NAME}'...")
    offset = None
    total_migrated = 0
    
    while True:
        points, next_page = local_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            with_payload=True,
            with_vectors=True,
            scroll_filter=None,
            offset=offset
        )
        
        if not points:
            break
            
        # 4. Upsert to cloud
        upsert_points = [
            PointStruct(
                id=p.id,
                vector=p.vector,
                payload=p.payload
            ) for p in points
        ]
        
        cloud_client.upsert(
            collection_name=COLLECTION_NAME,
            points=upsert_points
        )
        
        total_migrated += len(points)
        logger.info(f"✅ Migrated {total_migrated} points...")
        
        if not next_page:
            break
        offset = next_page

    logger.info(f"🎉 Migration Complete! Total points: {total_migrated}")

if __name__ == "__main__":
    migrate()
