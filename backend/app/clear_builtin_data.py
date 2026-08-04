"""
Remove built-in demo content from the local development database.

By default this removes:
- seeded demo articles from example-news.test
- threats/investments/events linked to those demo articles
- built-in default RSS feeds

It intentionally keeps reference countries/companies/infrastructure so the UI
can still render filters/maps while live articles are ingested.
"""
from app.database import Base, engine, SessionLocal
from app.models import (
    Article,
    Event,
    Investment,
    RSSFeed,
    Threat,
    article_companies,
    article_countries,
    article_organizations,
)
from app.services.rss_ingestion import DEFAULT_FEEDS


def clear_builtin_data() -> dict:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        demo_articles = db.query(Article).filter(Article.url.like("https://example-news.test/%")).all()
        demo_article_ids = [article.id for article in demo_articles]

        deleted = {
            "demo_articles": len(demo_article_ids),
            "default_feeds": 0,
        }

        if demo_article_ids:
            db.query(Threat).filter(Threat.article_id.in_(demo_article_ids)).delete(synchronize_session=False)
            db.query(Investment).filter(Investment.article_id.in_(demo_article_ids)).delete(synchronize_session=False)
            db.query(Event).filter(Event.article_id.in_(demo_article_ids)).delete(synchronize_session=False)
            db.execute(article_countries.delete().where(article_countries.c.article_id.in_(demo_article_ids)))
            db.execute(article_companies.delete().where(article_companies.c.article_id.in_(demo_article_ids)))
            db.execute(article_organizations.delete().where(article_organizations.c.article_id.in_(demo_article_ids)))
            db.query(Article).filter(Article.id.in_(demo_article_ids)).delete(synchronize_session=False)

        default_urls = [url for _, url in DEFAULT_FEEDS]
        deleted["default_feeds"] = db.query(RSSFeed).filter(RSSFeed.url.in_(default_urls)).delete(
            synchronize_session=False
        )

        db.commit()
        return deleted
    finally:
        db.close()


if __name__ == "__main__":
    result = clear_builtin_data()
    print(f"Removed {result['demo_articles']} demo articles and {result['default_feeds']} default feeds.")
