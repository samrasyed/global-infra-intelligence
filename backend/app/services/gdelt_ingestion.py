"""
Near-real-time article ingestion via the public GDELT DOC 2.0 API.

GDELT's DOC endpoint can return recent article metadata for keyword queries
without an API key. We use it as a live source alongside RSS, then hand saved
articles to the existing NLP/vector pipeline.
"""
import logging
import os
from datetime import datetime

import httpx
from dateutil import parser as dateparser
from sqlalchemy.orm import Session

from app.models import Article
from app.services.rss_ingestion import url_hash

logger = logging.getLogger("gciip.gdelt")

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
DEFAULT_GDELT_QUERY = (
    "(infrastructure OR \"power grid\" OR port OR railway OR airport OR "
    "\"undersea cable\" OR semiconductor OR \"data center\" OR LNG OR pipeline OR "
    "\"critical minerals\" OR \"rare earth\") "
    "(attack OR disruption OR investment OR acquisition OR sanction OR cyber OR security)"
)


def gdelt_enabled() -> bool:
    return os.getenv("GDELT_ENABLED", "false").lower() == "true"


def _parse_seen_date(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return dateparser.parse(value).replace(tzinfo=None)
    except Exception:
        return datetime.utcnow()


def poll_gdelt(
    db: Session,
    query: str | None = None,
    lookback_minutes: int | None = None,
    max_records: int | None = None,
) -> int:
    query = query or os.getenv("GDELT_QUERY", DEFAULT_GDELT_QUERY)
    lookback_minutes = max(15, lookback_minutes or int(os.getenv("GDELT_LOOKBACK_MINUTES", "15")))
    max_records = max(1, min(max_records or int(os.getenv("GDELT_MAX_RECORDS", "100")), 250))

    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "sort": "datedesc",
        "timespan": f"{lookback_minutes}min",
        "maxrecords": str(max_records),
    }

    with httpx.Client(timeout=20, follow_redirects=True) as client:
        response = client.get(GDELT_DOC_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    added = 0
    seen_urls = set()
    for item in payload.get("articles", []):
        link = item.get("url")
        title = item.get("title") or "Untitled"
        if not link:
            continue
        if link in seen_urls:
            continue
        uh = url_hash(link)
        if db.query(Article).filter((Article.url_hash == uh) | (Article.url == link)).first():
            continue
        seen_urls.add(link)

        domain = item.get("domain") or "GDELT"
        source_country = item.get("sourceCountry") or item.get("sourcecountry")
        source = f"GDELT: {domain}" if not source_country else f"GDELT: {domain} ({source_country})"

        article = Article(
            title=title,
            url=link,
            url_hash=uh,
            source=source,
            image_url=item.get("socialimage"),
            published_at=_parse_seen_date(item.get("seendate")),
            raw_text=title,
            processed=False,
        )
        db.add(article)
        added += 1

    db.commit()
    return added


def poll_gdelt_if_enabled(db: Session) -> dict:
    if not gdelt_enabled():
        return {"gdelt_enabled": False, "gdelt_articles_added": 0}
    try:
        added = poll_gdelt(db)
        return {"gdelt_enabled": True, "gdelt_articles_added": added}
    except Exception as exc:
        logger.warning("GDELT poll failed: %s", exc)
        return {"gdelt_enabled": True, "gdelt_articles_added": 0, "gdelt_error": str(exc)}
