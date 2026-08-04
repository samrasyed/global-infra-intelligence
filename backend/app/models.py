import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, ForeignKey, Table, Enum, Boolean, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_id() -> str:
    return uuid.uuid4().hex


class ThreatLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InfraCategory(str, enum.Enum):
    UNDERSEA_CABLE = "undersea_cable"
    PORT = "port"
    RAILWAY = "railway"
    AIRPORT = "airport"
    SHIPPING = "shipping"
    SEMICONDUCTOR = "semiconductor"
    DATA_CENTER = "data_center"
    AI_INFRASTRUCTURE = "ai_infrastructure"
    NUCLEAR = "nuclear"
    RARE_EARTH = "rare_earth"
    CRITICAL_MINERALS = "critical_minerals"
    OIL = "oil"
    LNG = "lng"
    PIPELINE = "pipeline"
    POWER_GRID = "power_grid"
    RENEWABLE_ENERGY = "renewable_energy"
    WATER = "water"
    SATELLITE = "satellite"
    SPACE = "space"
    OTHER = "other"


# ---- association tables -----------------------------------------------

article_countries = Table(
    "article_countries", Base.metadata,
    Column("article_id", String, ForeignKey("articles.id")),
    Column("country_id", String, ForeignKey("countries.id")),
)

article_companies = Table(
    "article_companies", Base.metadata,
    Column("article_id", String, ForeignKey("articles.id")),
    Column("company_id", String, ForeignKey("companies.id")),
)

article_organizations = Table(
    "article_organizations", Base.metadata,
    Column("article_id", String, ForeignKey("articles.id")),
    Column("organization_id", String, ForeignKey("organizations.id")),
)


# ---- core entities ------------------------------------------------------

class Country(Base):
    __tablename__ = "countries"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, unique=True, nullable=False, index=True)
    iso2 = Column(String(2), index=True)
    iso3 = Column(String(3), index=True)
    region = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    risk_score = Column(Float, default=0.0)

    articles = relationship("Article", secondary=article_countries, back_populates="countries")
    infrastructures = relationship("Infrastructure", back_populates="country")
    investments = relationship("Investment", back_populates="country")


class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    sector = Column(String)
    country_id = Column(String, ForeignKey("countries.id"), nullable=True)

    articles = relationship("Article", secondary=article_companies, back_populates="companies")
    investments = relationship("Investment", back_populates="company")


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, unique=True, nullable=False, index=True)
    org_type = Column(String)  # government, ngo, alliance, regulator...

    articles = relationship("Article", secondary=article_organizations, back_populates="organizations")


class Infrastructure(Base):
    __tablename__ = "infrastructure"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    category = Column(Enum(InfraCategory), nullable=False, index=True)
    country_id = Column(String, ForeignKey("countries.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(Text)

    country = relationship("Country", back_populates="infrastructures")


class Threat(Base):
    __tablename__ = "threats"
    id = Column(String, primary_key=True, default=gen_id)
    article_id = Column(String, ForeignKey("articles.id"))
    level = Column(Enum(ThreatLevel), nullable=False)
    score = Column(Float, nullable=False)  # 0-100
    factors = Column(JSON)  # {"cyber_attack": True, "military_activity": False, ...}
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="threat")


class Investment(Base):
    __tablename__ = "investments"
    id = Column(String, primary_key=True, default=gen_id)
    article_id = Column(String, ForeignKey("articles.id"))
    company_id = Column(String, ForeignKey("companies.id"), nullable=True)
    country_id = Column(String, ForeignKey("countries.id"), nullable=True)
    amount_usd = Column(Float)
    currency_raw = Column(String)
    description = Column(Text)

    company = relationship("Company", back_populates="investments")
    country = relationship("Country", back_populates="investments")
    article = relationship("Article", back_populates="investment")


class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=gen_id)
    article_id = Column(String, ForeignKey("articles.id"))
    title = Column(String)
    event_date = Column(DateTime)
    event_type = Column(String)  # cyber_attack, acquisition, sanction, disruption...

    article = relationship("Article", back_populates="events")


class Article(Base):
    __tablename__ = "articles"
    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False, index=True)
    url_hash = Column(String, unique=True, index=True)  # dedup key
    source = Column(String, index=True)
    image_url = Column(String)
    published_at = Column(DateTime, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    raw_text = Column(Text)
    clean_text = Column(Text)
    summary = Column(Text)

    infra_category = Column(Enum(InfraCategory), index=True)
    geopolitical_topics = Column(JSON)  # ["China", "Semiconductors", "Sanctions"]

    processed = Column(Boolean, default=False)
    embedding_id = Column(String, nullable=True)  # id in the vector store

    countries = relationship("Country", secondary=article_countries, back_populates="articles")
    companies = relationship("Company", secondary=article_companies, back_populates="articles")
    organizations = relationship("Organization", secondary=article_organizations, back_populates="articles")
    threat = relationship("Threat", back_populates="article", uselist=False)
    investment = relationship("Investment", back_populates="article", uselist=False)
    events = relationship("Event", back_populates="article")

    @property
    def matched_keywords(self) -> list[str]:
        from app.services.nlp_pipeline import INFRA_KEYWORDS
        text_l = f"{self.title or ''} {self.raw_text or ''}".lower()
        matched = []
        for cat, keywords in INFRA_KEYWORDS.items():
            for kw in keywords:
                if kw in text_l:
                    matched.append(kw)
        return sorted(list(set(matched)))


class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"))
    article_id = Column(String, ForeignKey("articles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class SavedSearch(Base):
    __tablename__ = "saved_searches"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    query = Column(String)
    filters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="analyst")  # analyst, admin
    created_at = Column(DateTime, default=datetime.utcnow)


class RSSFeed(Base):
    __tablename__ = "rss_feeds"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    active = Column(Boolean, default=True)
    last_polled_at = Column(DateTime, nullable=True)
