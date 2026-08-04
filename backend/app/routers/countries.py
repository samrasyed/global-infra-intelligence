from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Country, Article
from app.schemas import CountryOut, ArticleListItem

router = APIRouter(prefix="/api/countries", tags=["countries"])


@router.get("", response_model=list[CountryOut])
def list_countries(db: Session = Depends(get_db)):
    return db.query(Country).order_by(Country.risk_score.desc()).all()


@router.get("/{country_id}", response_model=CountryOut)
def get_country(country_id: str, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(404, "Country not found")
    return country


@router.get("/{country_id}/articles", response_model=list[ArticleListItem])
def country_articles(country_id: str, db: Session = Depends(get_db), limit: int = 20):
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(404, "Country not found")
    q = db.query(Article).options(joinedload(Article.threat)).join(Article.countries).filter(
        Country.id == country_id
    ).order_by(Article.published_at.desc()).limit(limit)
    return q.all()
