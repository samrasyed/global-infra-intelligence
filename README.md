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


