"""
Free-source RSS ingestion. No paid APIs, no scraping paywalls - only feeds.

Default feed set covers general newswires (which carry most infrastructure
stories) plus Google News topic searches, which is the free equivalent of a
keyword-filtered infrastructure feed.
"""
import hashlib
import logging
import os
from datetime import datetime, timezone

import feedparser
from dateutil import parser as dateparser
from sqlalchemy.orm import Session

from app.models import Article, RSSFeed
from app.services.nlp_pipeline import process_article
from app.services import embeddings as vec

logger = logging.getLogger("gciip.ingestion")

DEFAULT_FEEDS = [
    ("Reuters World", "https://feeds.reuters.com/Reuters/worldNews"),
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("AP Top News", "https://apnews.com/apf-topnews?format=rss"),
    ("UN News", "https://news.un.org/feed/subscribe/en/news/all/rss.xml"),
    ("Google News - Semiconductors", "https://news.google.com/rss/search?q=semiconductor+factory+OR+chip+fab&hl=en-US&gl=US&ceid=US:en"),
    ("Google News - Undersea Cables", "https://news.google.com/rss/search?q=undersea+cable+OR+subsea+cable&hl=en-US&gl=US&ceid=US:en"),
    ("Google News - Ports & Shipping", "https://news.google.com/rss/search?q=port+infrastructure+OR+shipping+terminal&hl=en-US&gl=US&ceid=US:en"),
    ("Google News - Power Grid", "https://news.google.com/rss/search?q=power+grid+OR+electric+utility+attack&hl=en-US&gl=US&ceid=US:en"),
    ("Google News - Rare Earth & Minerals", "https://news.google.com/rss/search?q=rare+earth+mining+OR+critical+minerals&hl=en-US&gl=US&ceid=US:en"),
    ("Google News - Data Centers & AI", "https://news.google.com/rss/search?q=data+center+investment+OR+AI+infrastructure&hl=en-US&gl=US&ceid=US:en"),
]


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def default_feeds_enabled() -> bool:
    return os.getenv("ENABLE_DEFAULT_FEEDS", "true").lower() == "true"


def ensure_default_feeds(db: Session) -> None:
    if not default_feeds_enabled():
        return
    for name, url in DEFAULT_FEEDS:
        if not db.query(RSSFeed).filter_by(url=url).first():
            db.add(RSSFeed(name=name, url=url, active=True))
    db.commit()


def _parse_date(entry) -> datetime:
    for key in ("published", "updated"):
        if getattr(entry, key, None):
            try:
                return dateparser.parse(entry[key]).astimezone(timezone.utc).replace(tzinfo=None)
            except Exception:
                pass
    return datetime.utcnow()


def poll_feed(db: Session, feed: RSSFeed, limit: int = 25) -> int:
    """Fetch one feed, store new articles (raw, un-processed). Returns count added."""
    parsed = feedparser.parse(feed.url)
    added = 0
    seen_urls = set()
    for entry in parsed.entries[:limit]:
        link = getattr(entry, "link", None)
        if not link:
            continue
        if link in seen_urls:
            continue
        uh = url_hash(link)
        if db.query(Article).filter((Article.url_hash == uh) | (Article.url == link)).first():
            continue  # dedup
        seen_urls.add(link)

        summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        image_url = None
        media = getattr(entry, "media_content", None) or getattr(entry, "media_thumbnail", None)
        if media:
            image_url = media[0].get("url")

        article = Article(
            title=getattr(entry, "title", "Untitled"),
            url=link,
            url_hash=uh,
            source=feed.name,
            image_url=image_url,
            published_at=_parse_date(entry),
            raw_text=summary,
            processed=False,
        )
        db.add(article)
        added += 1
    feed.last_polled_at = datetime.utcnow()
    db.commit()
    return added


def poll_all_feeds(db: Session) -> dict:
    ensure_default_feeds(db)
    feeds = db.query(RSSFeed).filter_by(active=True).all()
    total = 0
    for feed in feeds:
        try:
            total += poll_feed(db, feed)
        except Exception as e:  # a single bad feed should never kill the run
            logger.warning("feed poll failed: %s (%s)", feed.name, e)
    return {"feeds_polled": len(feeds), "articles_added": total}


def process_unprocessed(db: Session, limit: int = 50) -> int:
    """Run the NLP pipeline over articles that haven't been processed yet."""
    pending = db.query(Article).filter_by(processed=False).limit(limit).all()
    for article in pending:
        result = process_article(article.raw_text or "", article.title or "")
        article.clean_text = result["clean_text"]
        article.summary = result["summary"]
        article.infra_category = result["infra_category"]
        article.geopolitical_topics = result["geopolitical_topics"]
        article.processed = True

        try:
            vec.upsert_article(
                article.id,
                f"{article.title}. {result['clean_text']}",
                {"title": article.title, "source": article.source or "", "infra_category": result["infra_category"]},
            )
            article.embedding_id = article.id
        except Exception as e:
            logger.warning("embedding failed for %s: %s", article.id, e)

        from app.models import Threat, Investment
        db.add(Threat(
            article_id=article.id,
            level=result["threat_level"],
            score=result["threat_score"],
            factors=result["threat_factors"],
        ))
        if result["investment_amount_usd"]:
            db.add(Investment(article_id=article.id, amount_usd=result["investment_amount_usd"],
                               description=result["summary"]))
    db.commit()
    return len(pending)
