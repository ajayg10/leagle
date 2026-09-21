from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import os

def reset_qdrant():
    client = QdrantClient("localhost", port=6333)
    collection_name = "regulations_v1"
    
    print(f"🗑️ Deleting collection '{collection_name}'...")
    try:
        client.delete_collection(collection_name)
        print("✅ Deleted.")
    except Exception as e:
        print(f"ℹ️ Collection possibly didn't exist: {e}")
        
    print(f"🏗️ Creating collection '{collection_name}'...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    print("✅ Collection recreated.")

if __name__ == "__main__":
    reset_qdrant()
