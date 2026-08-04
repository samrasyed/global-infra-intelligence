from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Company, Article, Investment
from app.schemas import CompanyOut, ArticleListItem, InvestmentOut

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")
    return company


@router.get("/{company_id}/articles", response_model=list[ArticleListItem])
def company_articles(company_id: str, db: Session = Depends(get_db), limit: int = 20):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")
    q = db.query(Article).options(joinedload(Article.threat)).join(Article.companies).filter(
        Company.id == company_id
    ).order_by(Article.published_at.desc()).limit(limit)
    return q.all()


@router.get("/{company_id}/investments", response_model=list[InvestmentOut])
def company_investments(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")
    return db.query(Investment).filter(Investment.company_id == company_id).all()
