"""
NewsData.io ingestion for original daily news articles.

This is optional and requires a free NewsData.io API key. It normalizes the
Latest endpoint response into the existing Article table, then the normal NLP
pipeline processes the saved rows.
"""
import logging
import os
from datetime import datetime

import httpx
from dateutil import parser as dateparser
from sqlalchemy.orm import Session

from app.models import Article
from app.services.rss_ingestion import url_hash

logger = logging.getLogger("gciip.newsdata")

NEWSDATA_LATEST_URL = "https://newsdata.io/api/1/latest"
DEFAULT_NEWSDATA_QUERY = "infrastructure OR power grid OR port OR semiconductor OR pipeline"


def newsdata_enabled() -> bool:
    return os.getenv("NEWSDATA_ENABLED", "false").lower() == "true"


def _parse_pub_date(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return dateparser.parse(value).replace(tzinfo=None)
    except Exception:
        return datetime.utcnow()


def poll_newsdata(db: Session) -> int:
    api_key = os.getenv("NEWSDATA_API_KEY")
    if not api_key:
        raise RuntimeError("NEWSDATA_API_KEY is not set")

    params = {
        "apikey": api_key,
        "q": os.getenv("NEWSDATA_QUERY", DEFAULT_NEWSDATA_QUERY),
        "language": os.getenv("NEWSDATA_LANGUAGE", "en"),
        "removeduplicate": "1",
    }

    timeframe = os.getenv("NEWSDATA_TIMEFRAME")
    if timeframe:
        params["timeframe"] = timeframe

    country = os.getenv("NEWSDATA_COUNTRY")
    category = os.getenv("NEWSDATA_CATEGORY")
    if country:
        params["country"] = country
    if category:
        params["category"] = category

    with httpx.Client(timeout=20, follow_redirects=True) as client:
        response = client.get(NEWSDATA_LATEST_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    if payload.get("status") not in (None, "success"):
        raise RuntimeError(str(payload))

    added = 0
    seen_urls = set()
    for item in payload.get("results", []):
        link = item.get("link")
        title = item.get("title") or "Untitled"
        if not link:
            continue
        if link in seen_urls:
            continue
        uh = url_hash(link)
        if db.query(Article).filter((Article.url_hash == uh) | (Article.url == link)).first():
            continue
        seen_urls.add(link)

        source_name = item.get("source_name") or item.get("source_id") or "NewsData.io"
        raw_text = item.get("content") or item.get("description") or title

        article = Article(
            title=title,
            url=link,
            url_hash=uh,
            source=f"NewsData: {source_name}",
            image_url=item.get("image_url"),
            published_at=_parse_pub_date(item.get("pubDate")),
            raw_text=raw_text,
            processed=False,
        )
        db.add(article)
        added += 1

    db.commit()
    return added


def poll_newsdata_if_enabled(db: Session) -> dict:
    if not newsdata_enabled():
        return {"newsdata_enabled": False, "newsdata_articles_added": 0}
    try:
        added = poll_newsdata(db)
        return {"newsdata_enabled": True, "newsdata_articles_added": added}
    except Exception as exc:
        logger.warning("NewsData poll failed: %s", exc)
        return {"newsdata_enabled": True, "newsdata_articles_added": 0, "newsdata_error": str(exc)}
