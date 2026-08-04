from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RSSFeed
from app.services.gdelt_ingestion import poll_gdelt_if_enabled
from app.services.newsdata_ingestion import poll_newsdata_if_enabled
from app.services.rss_ingestion import DEFAULT_FEEDS, poll_all_feeds, process_unprocessed, ensure_default_feeds

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/ingest/run")
def run_ingestion_now(db: Session = Depends(get_db)):
    """Manually trigger one ingestion + processing cycle (the scheduler also
    runs this on the configured interval)."""
    stats = poll_all_feeds(db)
    gdelt_stats = poll_gdelt_if_enabled(db)
    newsdata_stats = poll_newsdata_if_enabled(db)
    processed = process_unprocessed(db)
    return {**stats, **gdelt_stats, **newsdata_stats, "articles_processed": processed}


@router.get("/feeds")
def list_feeds(db: Session = Depends(get_db)):
    ensure_default_feeds(db)
    feeds = db.query(RSSFeed).all()
    return [{"id": f.id, "name": f.name, "url": f.url, "active": f.active,
             "last_polled_at": f.last_polled_at} for f in feeds]


@router.post("/feeds")
def add_feed(name: str, url: str, db: Session = Depends(get_db)):
    feed = RSSFeed(name=name, url=url, active=True)
    db.add(feed)
    db.commit()
    return {"id": feed.id, "name": feed.name, "url": feed.url}


@router.patch("/feeds/defaults/deactivate")
def deactivate_default_feeds(db: Session = Depends(get_db)):
    default_urls = {url for _, url in DEFAULT_FEEDS}
    feeds = db.query(RSSFeed).filter(RSSFeed.url.in_(default_urls)).all()
    for feed in feeds:
        feed.active = False
    db.commit()
    return {"deactivated": len(feeds)}


@router.patch("/feeds/{feed_id}/toggle")
def toggle_feed(feed_id: str, db: Session = Depends(get_db)):
    feed = db.query(RSSFeed).filter_by(id=feed_id).first()
    if feed:
        feed.active = not feed.active
        db.commit()
    return {"id": feed_id, "active": feed.active if feed else None}
