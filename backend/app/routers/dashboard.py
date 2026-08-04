from datetime import datetime, timedelta
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Article, Threat, Country, Company, Investment, InfraCategory
from app.schemas import DashboardResponse, DashboardKPIs, ChartPoint

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    since = datetime.utcnow() - timedelta(days=14)

    articles_today = db.query(Article).filter(func.date(Article.published_at) == today).count()
    threat_events_today = db.query(Threat).join(Article).filter(
        func.date(Article.published_at) == today, Threat.level.in_(["high", "critical"])
    ).count()
    countries_tracked = db.query(Country).count()
    companies_tracked = db.query(Company).count()
    total_investment = db.query(func.coalesce(func.sum(Investment.amount_usd), 0.0)).scalar()
    avg_threat = db.query(func.coalesce(func.avg(Threat.score), 0.0)).scalar()

    recent_articles = db.query(Article).filter(Article.published_at >= since).all()
    per_day = Counter(a.published_at.date().isoformat() for a in recent_articles if a.published_at)
    articles_per_day = [ChartPoint(label=d, value=v) for d, v in sorted(per_day.items())]

    threats = db.query(Threat).all()
    level_counts = Counter(t.level for t in threats)
    threat_distribution = [ChartPoint(label=lvl, value=level_counts.get(lvl, 0))
                            for lvl in ["low", "medium", "high", "critical"]]

    country_counts = Counter()
    for a in db.query(Article).all():
        for c in a.countries:
            country_counts[c.name] += 1
    top_countries = [ChartPoint(label=n, value=v) for n, v in country_counts.most_common(10)]

    company_counts = Counter()
    for a in db.query(Article).all():
        for c in a.companies:
            company_counts[c.name] += 1
    top_companies = [ChartPoint(label=n, value=v) for n, v in company_counts.most_common(10)]

    infra_counts = Counter(a.infra_category for a in db.query(Article).all() if a.infra_category)
    infra_categories = [ChartPoint(label=cat.value, value=cnt) for cat, cnt in infra_counts.most_common()]

    return DashboardResponse(
        kpis=DashboardKPIs(
            articles_today=articles_today,
            threat_events_today=threat_events_today,
            countries_tracked=countries_tracked,
            companies_tracked=companies_tracked,
            total_investment_usd=total_investment or 0.0,
            average_threat_score=round(avg_threat or 0.0, 1),
        ),
        articles_per_day=articles_per_day,
        threat_distribution=threat_distribution,
        top_countries=top_countries,
        top_companies=top_companies,
        infrastructure_categories=infra_categories,
    )
