"""
ChromaDB-backed vector store. Uses sentence-transformers (all-MiniLM-L6-v2,
free/local, no API key) to embed article text, and exposes a simple
`upsert_article` / `search` interface used by both global search and the
RAG chatbot.
"""
import os
from functools import lru_cache

CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_store")


@lru_cache(maxsize=1)
def _client():
    import chromadb
    return chromadb.PersistentClient(path=CHROMA_DIR)


@lru_cache(maxsize=1)
def _collection():
    return _client().get_or_create_collection(name="articles")


@lru_cache(maxsize=1)
def _embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def upsert_article(article_id: str, text: str, metadata: dict) -> None:
    embedding = _embedder().encode(text[:4000]).tolist()
    _collection().upsert(ids=[article_id], embeddings=[embedding], metadatas=[metadata], documents=[text[:4000]])


def search(query: str, n_results: int = 8) -> list[dict]:
    embedding = _embedder().encode(query).tolist()
    result = _collection().query(query_embeddings=[embedding], n_results=n_results)
    out = []
    ids = result.get("ids", [[]])[0]
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]
    for i in range(len(ids)):
        out.append({"id": ids[i], "document": docs[i], "metadata": metas[i], "distance": dists[i]})
    return out
