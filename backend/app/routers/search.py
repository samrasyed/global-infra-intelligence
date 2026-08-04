from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import embeddings as vec

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
def semantic_search(
    q: str = Query(..., min_length=2),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Global AI search, e.g. 'Chinese investments in Africa' or
    'undersea cable incidents'. Backed by ChromaDB cosine similarity over
    sentence-transformer embeddings of article title + clean text.
    Falls back to database keyword search if vector DB is not available.
    """
    try:
        results = vec.search(q, n_results=limit)
        return {
            "query": q,
            "results": [
                {
                    "article_id": r["id"],
                    "title": r["metadata"].get("title"),
                    "source": r["metadata"].get("source"),
                    "infra_category": r["metadata"].get("infra_category"),
                    "relevance": round(1 - r["distance"], 3) if r["distance"] is not None else None,
                    "snippet": r["document"][:280],
                }
                for r in results
            ],
        }
    except Exception:
        # Fallback to database keyword search
        from app.models import Article
        words = [w.strip().lower() for w in q.split() if w.strip()]
        query_obj = db.query(Article).filter(Article.processed == True)  # noqa: E712
        for word in words:
            query_obj = query_obj.filter(
                Article.title.ilike(f"%{word}%") |
                Article.clean_text.ilike(f"%{word}%") |
                Article.source.ilike(f"%{word}%")
            )
        articles = query_obj.order_by(Article.published_at.desc()).limit(limit).all()
        return {
            "query": q,
            "results": [
                {
                    "article_id": a.id,
                    "title": a.title,
                    "source": a.source,
                    "infra_category": a.infra_category.value if a.infra_category else None,
                    "relevance": 1.0,
                    "snippet": a.summary[:280] if a.summary else (a.clean_text[:280] if a.clean_text else ""),
                }
                for a in articles
            ]
        }
