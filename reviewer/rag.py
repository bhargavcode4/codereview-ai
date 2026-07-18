from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from . import config

_model = None
_client = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
    return _model


def _get_client():
    # path= runs Qdrant embedded/on-disk -- no separate server or container needed.
    global _client
    if _client is None:
        _client = QdrantClient(path=config.QDRANT_PATH)
    return _client


def ensure_collection():
    client = _get_client()
    if not client.collection_exists(config.COLLECTION_NAME):
        dim = _get_model().get_sentence_embedding_dimension()
        client.create_collection(
            collection_name=config.COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def ingest_documents(chunks: list):
    """chunks: list[str] -- style guide / past-review text chunks to embed and store."""
    ensure_collection()
    client = _get_client()
    model = _get_model()
    vectors = model.encode(chunks).tolist()
    points = [
        PointStruct(id=i, vector=vectors[i], payload={"text": chunks[i]})
        for i in range(len(chunks))
    ]
    client.upsert(collection_name=config.COLLECTION_NAME, points=points)


def retrieve(query: str, top_k: int = 3) -> list:
    client = _get_client()
    if not client.collection_exists(config.COLLECTION_NAME):
        return []
    model = _get_model()
    vector = model.encode([query])[0].tolist()
    hits = client.query_points(
        collection_name=config.COLLECTION_NAME, query=vector, limit=top_k
    ).points
    return [hit.payload["text"] for hit in hits]
