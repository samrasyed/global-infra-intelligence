from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Article, Country, Company
from app.schemas import ArticleListItem, ArticleDetail

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=list[ArticleListItem])
def list_articles(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    country: Optional[str] = None,
    company: Optional[str] = None,
    infra_category: Optional[str] = None,
    threat_level: Optional[str] = None,
    source: Optional[str] = None,
):
    q = db.query(Article).options(
        joinedload(Article.threat), joinedload(Article.countries), joinedload(Article.companies)
    ).filter(Article.processed == True)  # noqa: E712

    if country:
        q = q.join(Article.countries).filter(Country.name.ilike(f"%{country}%"))
    if company:
        q = q.join(Article.companies).filter(Company.name.ilike(f"%{company}%"))
    if infra_category:
        q = q.filter(Article.infra_category == infra_category)
    if source:
        q = q.filter(Article.source.ilike(f"%{source}%"))

    q = q.order_by(Article.published_at.desc())
    articles = q.offset((page - 1) * page_size).limit(page_size).all()

    if threat_level:
        articles = [a for a in articles if a.threat and a.threat.level == threat_level]

    return articles


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: str, db: Session = Depends(get_db)):
    article = db.query(Article).options(
        joinedload(Article.threat), joinedload(Article.investment),
        joinedload(Article.countries), joinedload(Article.companies),
    ).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(404, "Article not found")
    return article


@router.get("/{article_id}/related", response_model=list[ArticleListItem])
def related_articles(article_id: str, db: Session = Depends(get_db), limit: int = 5):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(404, "Article not found")
    q = db.query(Article).filter(
        Article.infra_category == article.infra_category, Article.id != article_id
    ).order_by(Article.published_at.desc()).limit(limit)
    return q.all()
