import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import articles, dashboard, countries, companies, map_infra, search, chat, admin

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="GCIIP - Global Critical Infrastructure Intelligence Platform API",
    version="1.0.0",
    description="AI-powered ingestion, extraction, and analytics API for critical-infrastructure news intelligence.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(dashboard.router)
app.include_router(countries.router)
app.include_router(companies.router)
app.include_router(map_infra.router)
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed if database is empty (ideal for free tier cloud environments)
    from app.database import SessionLocal
    from app.models import Country
    db = SessionLocal()
    try:
        if db.query(Country).count() == 0:
            logging.info("Empty database detected. Running auto-seeding...")
            from app.seed_data import seed
            seed()
    except Exception as e:
        logging.error("Startup auto-seeding failed: %s", e)
    finally:
        db.close()

    if os.getenv("ENABLE_SCHEDULER", "true").lower() == "true":
        from app.services.scheduler import start_scheduler
        start_scheduler()


@app.get("/")
def root():
    return {
        "service": "gciip-api",
        "status": "ok",
        "frontend": "http://127.0.0.1:3000",
        "docs": "http://127.0.0.1:8000/docs",
        "health": "http://127.0.0.1:8000/api/health",
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "gciip-api"}
