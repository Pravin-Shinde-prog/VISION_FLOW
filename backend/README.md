# VISION_FLOW — Backend API & Engine Services

This directory will contain the central backend services, REST APIs, WebSocket managers, database persistence, and analytical engines for **VISION_FLOW**.

---

## 🛠️ Planned Technology Stack

- **Framework:** Python 3.10+ / FastAPI
- **ASGI Server:** Uvicorn
- **Data Validation & Schemas:** Pydantic v2
- **Database & Spatial Engine:** PostgreSQL 15+ with PostGIS
- **ORM / Query Layer:** SQLAlchemy (Async) / asyncpg
- **Graph & Algorithms:** NetworkX / Custom Spatio-Temporal Graph Engine
- **Computer Vision & OCR Services:** OpenCV, YOLO (Ultralytics), PaddleOCR
- **Real-Time Streaming:** FastAPI WebSockets

---

## 📁 Target Directory Structure (To be scaffolded in Stage 4 & subsequent stages)

```
backend/
├── app/
│   ├── api/                # API Routers & Endpoints
│   │   ├── v1/
│   │   │   ├── cameras.py      # Camera node registration, status, and metadata
│   │   │   ├── detections.py   # Detection event ingestion and querying
│   │   │   ├── vehicles.py     # Vehicle profiles, visual signatures & search
│   │   │   ├── trajectories.py # Spatio-temporal route reconstruction
│   │   │   ├── alerts.py       # Law enforcement alerts & watchlist hits
│   │   │   ├── analytics.py    # City traffic density, choke points, delay
│   │   │   └── simulation.py   # Demo scenario controls & anomaly injection
│   │   └── router.py           # Primary API v1 router aggregate
│   ├── core/               # Application configuration & security
│   │   ├── config.py           # Settings management (Pydantic BaseSettings)
│   │   ├── logging.py          # Structured logging configuration
│   │   └── security.py         # CORS, authentication & permissions
│   ├── db/                 # Database setup & models
│   │   ├── session.py          # Async engine and session factory
│   │   ├── base.py             # Base model declaration
│   │   └── models/             # SQLAlchemy ORM models
│   │       ├── camera.py       # Camera nodes with PostGIS Point geometry
│   │       ├── detection.py    # Detection events, timestamps & bounding boxes
│   │       ├── vehicle.py      # Known vehicles, visual embeddings & plates
│   │       ├── road_graph.py   # Road edges, distances, speed limits & travel times
│   │       ├── alert.py        # Stolen/ghost plate alerts & forensic snapshots
│   │       └── watchlist.py    # Law enforcement hot-list entries
│   ├── schemas/            # Pydantic request & response schemas
│   │   ├── camera.py
│   │   ├── detection.py
│   │   ├── trajectory.py
│   │   ├── alert.py
│   │   └── analytics.py
│   ├── services/           # Core business logic & intelligence engines
│   │   ├── vision/             # Image preprocessing, enhancement & OCR pipeline
│   │   ├── reid/               # Multi-feature vehicle matching & similarity
│   │   ├── graph/              # Spatio-Temporal Directed Graph & Feasibility Engine
│   │   ├── anomaly/            # Ghost/cloned plate detector & proof generator
│   │   ├── alerts/             # Watchlist matcher & WebSocket notification dispatcher
│   │   ├── analytics/          # Traffic density, choke points & corridor optimizer
│   │   └── simulator/          # Video feeder & synthetic event stream generator
│   └── main.py             # FastAPI entrypoint application
├── tests/                  # Pytest automated test suite
├── alembic/                # Database migration scripts (Stage 5)
├── requirements.txt        # Python package dependencies
└── README.md               # Backend documentation
```

---

## 🔒 Stage 1 Status Note

In accordance with **Stage 1: Foundation**, no backend dependencies, database configurations, or AI model weights have been installed yet. The backend structure and endpoints will be initialized in **Stage 4: Backend Foundation** and expanded in subsequent stages.
