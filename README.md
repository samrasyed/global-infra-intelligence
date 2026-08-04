# GCIIP — Global Critical Infrastructure Intelligence Platform

GCIIP is an AI-powered intelligence platform that monitors and structures global threats, investments, and incidents related to critical infrastructure (e.g., semiconductors, ports, power grids, undersea cables, and rare earths) by analyzing unstructured news feeds in real-time.

---

## 🚀 Key Features

* **Executive Overview Dashboard**: Tracks real-time KPIs (articles ingested, threat events, investments tracked, and average threat score) with interactive analytics charts.
* **Country Risk Map**: A dynamic, interactive choropleth map that shades country boundaries based on their active geopolitical risk score (0-100) and overlays exact coordinate markers for key infrastructure assets (like ports and cable landing stations).
* **Intelligence Feed**: Chronological stream of all processed articles, showing the extracted countries, involved companies, threat level badges, and the exact hashtag keywords (e.g., `#undersea_cable`, `#semiconductor`) that matched.
* **Continuous Ingestion Pipeline**: Ingestion scheduler that polls global RSS newswires, Google News targeted search feeds, GDELT Doc 2.0 API, and NewsData.io every 10 minutes to process incoming articles.
* **Entity Extraction & Classification**: A lightweight, robust Python `spaCy` pipeline that processes raw text, filters boilerplates, classifies the infrastructure category, and scores threats on the fly.

---

## 🛠️ Tech Stack

* **Backend**: FastAPI (Python), SQLAlchemy, SQLite (for local dev) / PostgreSQL (for prod), APScheduler, spaCy (NLP parsing).
* **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts (visualizations), React-Leaflet (interactive map).

---

## 💻 Local Setup & Quick Start

### 1. Backend

Make sure you have Python 3.10+ installed.

```bash
cd backend
python -m venv venv

# On macOS/Linux:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Create a `.env` file in the `backend/` directory:
```ini
ENABLE_DEFAULT_FEEDS=true
ENABLE_SCHEDULER=true
INGEST_INTERVAL_MINUTES=10
GDELT_ENABLED=true
NEWSDATA_ENABLED=true
NEWSDATA_API_KEY=your_newsdata_api_key_here
NEWSDATA_QUERY=infrastructure
NEWSDATA_LANGUAGE=en
```

To seed the database with initial demo data so the charts are not empty, run:
```bash
python -m app.seed_data
```

Start the FastAPI backend server:
```bash
python -m uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: http://localhost:8000/docs

---

### 2. Frontend

Make sure you have Node.js installed.

```bash
cd frontend
npm install
```

Create a `.env.local` file in the `frontend/` directory:
```ini
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Start the Next.js development server:
```bash
npm run dev
```
Open your browser and navigate to: http://localhost:3000

---

## 🌐 Production Deployment Guide

To deploy the platform properly in production, use the following configurations:

### Part 1: Backend on Render
1. Create a new **Web Service** on Render pointing to your GitHub repository.
2. Configure settings:
   * **Root Directory**: `backend`
   * **Language**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. In **Environment Variables**, add:
   * `NEWSDATA_API_KEY` = `your_newsdata_api_key_here`
   * `ENABLE_DEFAULT_FEEDS` = `true`
   * `GDELT_ENABLED` = `true`
   * `ENABLE_SCHEDULER` = `true`
   * `INGEST_INTERVAL_MINUTES` = `10`
   * `DATABASE_URL` = `sqlite:////data/gciip.db`
4. In **Advanced settings**, scroll to **Disks** and click **Add Disk**:
   * **Name**: `db-storage`
   * **Mount Path**: `/data`
   * **Size**: `1 GiB`
5. Deploy and copy your backend URL (e.g., `https://gciip-api.onrender.com`).

### Part 2: Frontend on Vercel
1. Create a new project on Vercel pointing to your GitHub repository.
2. Configure settings:
   * **Root Directory**: `frontend`
   * **Framework Preset**: `Next.js`
3. Add **Environment Variable**:
   * `NEXT_PUBLIC_API_BASE_URL` = `https://gciip-api.onrender.com` (Your Render backend URL)
4. Deploy the project.
