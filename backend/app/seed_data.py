"""
Seed the DB with reference data (countries) and a handful of realistic demo
articles so every page renders meaningfully offline.

Run:  python -m app.seed_data
"""
from datetime import datetime, timedelta

from app.database import Base, engine, SessionLocal
from app.models import (
    Country, Company, Infrastructure, Article, Threat, Investment, InfraCategory, ThreatLevel
)

COUNTRIES = [
    ("United States", "US", "USA", "Americas", 39.8, -98.6, 42),
    ("China", "CN", "CHN", "Asia", 35.9, 104.2, 68),
    ("Taiwan", "TW", "TWN", "Asia", 23.7, 121.0, 74),
    ("India", "IN", "IND", "Asia", 20.6, 79.0, 38),
    ("Russia", "RU", "RUS", "Europe", 61.5, 105.3, 81),
    ("Australia", "AU", "AUS", "Oceania", -25.3, 133.8, 22),
    ("Germany", "DE", "DEU", "Europe", 51.2, 10.4, 24),
    ("Vietnam", "VN", "VNM", "Asia", 14.1, 108.3, 41),
    ("Nigeria", "NG", "NGA", "Africa", 9.1, 8.7, 55),
    ("Saudi Arabia", "SA", "SAU", "Middle East", 23.9, 45.1, 47),
]

COMPANIES = [
    ("TSMC", "Semiconductors", "Taiwan"),
    ("COSCO Shipping", "Shipping", "China"),
    ("China State Construction", "Infrastructure", "China"),
    ("Vestas", "Renewable Energy", "Germany"),
    ("Adani Ports", "Ports", "India"),
    ("Rosneft", "Oil & Gas", "Russia"),
]

INFRA = [
    ("Kaohsiung Port", "port", "Taiwan", 22.6, 120.3),
    ("HinOc3 Undersea Cable Landing", "undersea_cable", "Taiwan", 25.0, 121.6),
    ("Hsinchu Science Park Fab", "semiconductor", "Taiwan", 24.8, 121.0),
    ("Gwadar Port", "port", "Nigeria", 25.1, 62.3),
    ("Loyang Rare Earth Facility", "rare_earth", "China", 34.6, 112.4),
    ("Northern Grid Interconnector", "power_grid", "Germany", 53.0, 9.0),
]

ARTICLES = [
    {
        "title": "Taiwan reports disruption to undersea cable near northern coast",
        "url": "https://example-news.test/articles/taiwan-cable-disruption",
        "source": "Reuters World",
        "text": (
            "Taiwan's telecom regulator said a subsea cable serving northern data links suffered "
            "an outage this week, reviving concerns about sabotage of undersea cable infrastructure "
            "near Taiwan. Military officials said naval patrols were increased near the cable landing "
            "site as authorities investigate. The disruption briefly affected internet traffic before "
            "backup routing restored service."
        ),
        "countries": ["Taiwan", "China"],
        "companies": [],
        "infra": "undersea_cable",
        "days_ago": 1,
    },
    {
        "title": "TSMC announces $12 billion investment in new Arizona chip fab",
        "url": "https://example-news.test/articles/tsmc-arizona-investment",
        "source": "AP Top News",
        "text": (
            "TSMC said it will invest $12 billion to expand semiconductor fabrication capacity in "
            "Arizona, its largest overseas chip fab commitment yet. The investment is aimed at "
            "diversifying supply chains for advanced chips amid export restrictions on China. "
            "Analysts said the move reduces Taiwan's exposure to concentration risk."
        ),
        "countries": ["United States", "Taiwan"],
        "companies": ["TSMC"],
        "infra": "semiconductor",
        "days_ago": 2,
    },
    {
        "title": "COSCO Shipping deepens stake in African port terminal",
        "url": "https://example-news.test/articles/cosco-africa-port-stake",
        "source": "Google News - Ports & Shipping",
        "text": (
            "Chinese state-owned COSCO Shipping has acquired a larger stake in a West African port "
            "terminal as part of continued Belt and Road infrastructure investment. The acquisition "
            "raises questions among Western officials about strategic control of critical shipping "
            "chokepoints, though local officials welcomed the funding for port modernization."
        ),
        "countries": ["Nigeria", "China"],
        "companies": ["COSCO Shipping"],
        "infra": "port",
        "days_ago": 3,
    },
    {
        "title": "Cyberattack disrupts regional power grid operator in Germany",
        "url": "https://example-news.test/articles/germany-grid-cyberattack",
        "source": "BBC World",
        "text": (
            "A cyberattack targeted a regional power grid operator in northern Germany, causing brief "
            "outages before systems were isolated, officials said. The ransomware incident is under "
            "investigation and has raised alarm about the vulnerability of Europe's electric grid to "
            "state-linked hacking groups. No sanctions have yet been announced."
        ),
        "countries": ["Germany"],
        "companies": [],
        "infra": "power_grid",
        "days_ago": 1,
    },
    {
        "title": "Australia approves new rare earth mining project amid China tensions",
        "url": "https://example-news.test/articles/australia-rare-earth-project",
        "source": "Google News - Rare Earth & Minerals",
        "text": (
            "Australia's government approved a new rare earth mining project intended to reduce reliance "
            "on Chinese critical minerals processing. The $800 million investment includes a domestic "
            "refining facility, part of a broader push among Western allies to secure critical mineral "
            "supply chains outside of China."
        ),
        "countries": ["Australia", "China"],
        "companies": [],
        "infra": "rare_earth",
        "days_ago": 4,
    },
    {
        "title": "Vietnam signs data center investment deal with regional cloud provider",
        "url": "https://example-news.test/articles/vietnam-data-center-deal",
        "source": "Google News - Data Centers & AI",
        "text": (
            "Vietnam signed an agreement for a new hyperscale data center campus to support AI "
            "infrastructure demand in Southeast Asia. The $450 million investment is expected to "
            "create a regional hub for cloud and AI compute capacity, officials said."
        ),
        "countries": ["Vietnam"],
        "companies": [],
        "infra": "data_center",
        "days_ago": 5,
    },
]


def get_or_create(db, model, name_field, name_value, **kwargs):
    obj = db.query(model).filter(getattr(model, name_field) == name_value).first()
    if obj:
        return obj
    obj = model(**{name_field: name_value}, **kwargs)
    db.add(obj)
    db.flush()
    return obj


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        country_objs = {}
        for name, iso2, iso3, region, lat, lon, risk in COUNTRIES:
            c = get_or_create(db, Country, "name", name, iso2=iso2, iso3=iso3, region=region,
                               latitude=lat, longitude=lon, risk_score=risk)
            country_objs[name] = c

        company_objs = {}
        for name, sector, home_country in COMPANIES:
            c = get_or_create(db, Company, "name", name, sector=sector,
                               country_id=country_objs.get(home_country).id if home_country in country_objs else None,
                               description=f"{name} operates in the {sector.lower()} sector.")
            company_objs[name] = c

        for name, category, country_name, lat, lon in INFRA:
            get_or_create(db, Infrastructure, "name", name, category=InfraCategory(category),
                          country_id=country_objs[country_name].id, latitude=lat, longitude=lon,
                          description=f"{name} is tracked under the {category.replace('_', ' ')} category.")

        from app.services.nlp_pipeline import process_article
        from app.services import embeddings as vec

        for a in ARTICLES:
            if db.query(Article).filter_by(url=a["url"]).first():
                continue
            result = process_article(a["text"], a["title"])
            article = Article(
                title=a["title"], url=a["url"], url_hash=str(hash(a["url"])), source=a["source"],
                published_at=datetime.utcnow() - timedelta(days=a["days_ago"]),
                raw_text=a["text"], clean_text=result["clean_text"], summary=result["summary"],
                infra_category=InfraCategory(a["infra"]), geopolitical_topics=result["geopolitical_topics"],
                processed=True,
            )
            for cn in a["countries"]:
                if cn in country_objs:
                    article.countries.append(country_objs[cn])
            for co in a["companies"]:
                if co in company_objs:
                    article.companies.append(company_objs[co])
            db.add(article)
            db.flush()

            db.add(Threat(article_id=article.id, level=ThreatLevel(result["threat_level"]),
                          score=result["threat_score"], factors=result["threat_factors"]))
            if result["investment_amount_usd"]:
                db.add(Investment(article_id=article.id, amount_usd=result["investment_amount_usd"],
                                  description=result["summary"],
                                  company_id=(company_objs[a["companies"][0]].id if a["companies"] else None),
                                  country_id=country_objs[a["countries"][0]].id if a["countries"] else None))
            try:
                vec.upsert_article(article.id, f"{article.title}. {result['clean_text']}",
                                   {"title": article.title, "source": article.source,
                                    "infra_category": a["infra"]})
                article.embedding_id = article.id
            except Exception as e:
                print(f"embedding skipped for {article.title}: {e}")

        db.commit()
        print(f"Seeded {len(COUNTRIES)} countries, {len(COMPANIES)} companies, "
              f"{len(INFRA)} infrastructure assets, {len(ARTICLES)} demo articles.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
