from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from src.utils.settings import settings
from typing import Optional
qdrant_client = None

def init_qdrant(dim: int = 1536):
    global qdrant_client
    qdrant_client = QdrantClient(
        url=settings.qdrant_host,
        api_key=getattr(settings, "qdrant_api_key", None)
    )
    existing_collections = qdrant_client.get_collections().collections
    if settings.qdrant_collection_name not in [c.name for c in existing_collections]:
        qdrant_client.recreate_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

def insert_vector(id: str, vector: list[float], payload: Optional[dict] = None):
    if qdrant_client is None:
        raise RuntimeError("Qdrant client not initialized. Call init_qdrant() first.")
    if payload is None:
        payload = {}
    qdrant_client.upsert(
        collection_name=settings.qdrant_collection_name,
        points=[
            PointStruct(id=id, vector=vector, payload=payload)
        ]
    )

def search_vector(query: list[float], k: int = 5):
    if qdrant_client is None:
        raise RuntimeError("Qdrant client not initialized. Call init_qdrant() first.")
    return qdrant_client.search(
        collection_name=settings.qdrant_collection_name,
        query_vector=query,
        limit=k
    )