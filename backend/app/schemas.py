from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    iso2: Optional[str] = None
    iso3: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    risk_score: float = 0.0


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: Optional[str] = None
    sector: Optional[str] = None


class ThreatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    level: str
    score: float
    factors: Optional[dict] = None


class InvestmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    amount_usd: Optional[float] = None
    currency_raw: Optional[str] = None
    description: Optional[str] = None


class ArticleListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    source: Optional[str] = None
    image_url: Optional[str] = None
    published_at: Optional[datetime] = None
    infra_category: Optional[str] = None
    summary: Optional[str] = None
    threat: Optional[ThreatOut] = None
    countries: list[CountryOut] = []
    companies: list[CompanyOut] = []
    matched_keywords: list[str] = []


class ArticleDetail(ArticleListItem):
    url: str
    clean_text: Optional[str] = None
    geopolitical_topics: Optional[list[str]] = None
    investment: Optional[InvestmentOut] = None


class InfrastructureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    country: Optional[CountryOut] = None


class DashboardKPIs(BaseModel):
    articles_today: int
    threat_events_today: int
    countries_tracked: int
    companies_tracked: int
    total_investment_usd: float
    average_threat_score: float


class ChartPoint(BaseModel):
    label: str
    value: float


class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    articles_per_day: list[ChartPoint]
    threat_distribution: list[ChartPoint]
    top_countries: list[ChartPoint]
    top_companies: list[ChartPoint]
    infrastructure_categories: list[ChartPoint]
