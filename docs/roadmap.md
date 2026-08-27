# VISION_FLOW — 18-Stage Development Roadmap

This document outlines the step-by-step implementation strategy for **VISION_FLOW** (Smart India Hackathon). Each stage is self-contained, testable, and builds progressively upon prior stages.

---

## 🗺️ Roadmap Overview

| Stage | Title | Focus Area | Status |
| :---: | :--- | :--- | :---: |
| **Stage 1** | **Foundation & Architecture** | Project structure, .gitignore, docs, directory blueprints | **In Progress / Current** |
| **Stage 2** | **Git & GitHub Strategy** | Branching model, repo hygiene, commit conventions | Upcoming |
| **Stage 3** | **Frontend Shell** | React + Vite + TypeScript + Tailwind layout & navigation | Upcoming |
| **Stage 4** | **Backend Foundation** | FastAPI app, modular routers, health check, CORS | Upcoming |
| **Stage 5** | **Database & PostGIS** | Spatial database schema, models, migrations, seed data | Upcoming |
| **Stage 6** | **GIS & Camera Network** | Map rendering, camera nodes, road network overlays | Upcoming |
| **Stage 7** | **Edge Vision & Preprocessing** | Image enhancement, glare/shadow/rain/blur mitigation | Upcoming |
| **Stage 8** | **ANPR & OCR Pipeline** | License plate detection, OCR reader, RTO compliance checks | Upcoming |
| **Stage 9** | **Vehicle Visual Signature** | Color, type, make, and attribute extraction for Re-ID | Upcoming |
| **Stage 10**| **Multi-Camera Tracking** | Cross-camera association under occluded/missing plates | Upcoming |
| **Stage 11**| **Spatio-Temporal Graph** | Directed graph model, edge travel times, path validity | Upcoming |
| **Stage 12**| **Ghost/Cloned Plate Detection** | Impossible transition detection, evidence collection | Upcoming |
| **Stage 13**| **Law Enforcement & Watchlist** | Blacklist queries, stolen vehicle alerts, audit trails | Upcoming |
| **Stage 14**| **Urban Traffic Analytics** | Density, choke points, corridor delays, congestion heatmaps | Upcoming |
| **Stage 15**| **Dashboard Integration** | Real-time WebSocket event feeds, integrated UI views | Upcoming |
| **Stage 16**| **Simulation & Demo Engine** | Synthetic scenario generator, anomaly injector for SIH | Upcoming |
| **Stage 17**| **Testing & Polish** | End-to-end testing, error handling, performance tuning | Upcoming |
| **Stage 18**| **SIH Finalization & Demo Prep** | Demo scripts, presentation assets, final documentation | Upcoming |

---

## 📋 Detailed Stage Breakdown

### Stage 1: Foundation (Current Stage)
- **Goal:** Establish clean workspace structure, robust `.gitignore`, comprehensive root `README.md`, deep-dive `architecture.md`, and this `roadmap.md`.
- **Deliverables:** Verified directory hierarchy (`frontend/`, `backend/`, `docs/`, `data/`, `scripts/`), ignore rules, architectural documentation.
- **Verification:** Clean directory tree, no unnecessary dependencies, no premature implementations.

### Stage 2: Git / GitHub Setup
- **Goal:** Initialize Git tracking, establish clean commit conventions, and create branch protection rules.
- **Deliverables:** Initial commit, branch strategy (`main`, `develop`, feature branches).

### Stage 3: Frontend Shell
- **Goal:** Scaffold React + Vite + TypeScript frontend with Tailwind CSS and responsive sidebar/header navigation.
- **Deliverables:** Navigation shell, responsive layout, dark/light theme, view switcher (Live Feeds, GIS Map, Vehicle Search, Alerts, Traffic Analytics).
- **Verification:** `npm run dev` serves UI cleanly without console errors.

### Stage 4: Backend Foundation
- **Goal:** Initialize FastAPI backend with modular router structure, Pydantic schemas, and CORS middleware.
- **Deliverables:** `main.py`, router stubs (`/api/v1/cameras`, `/api/v1/detections`, `/api/v1/trajectories`, `/api/v1/alerts`, `/api/v1/analytics`), `/health` endpoint.
- **Verification:** `uvicorn` server boots and returns 200 OK on health check.

### Stage 5: Database & PostGIS
- **Goal:** Set up PostgreSQL with PostGIS extension for spatial queries and vehicle event storage.
- **Deliverables:** SQLAlchemy models for Cameras, Detections, Vehicles, Watchlist, Graph Edges; migration scripts; seed data.
- **Verification:** Spatial indexing and point-in-polygon / distance queries execute cleanly.

### Stage 6: GIS & Camera Network Model
- **Goal:** Integrate interactive mapping (Leaflet / Google Maps) with camera node placement and road link overlays.
- **Deliverables:** Interactive map component with custom camera markers, status indicators, and road vector layers.
- **Verification:** Map renders camera nodes dynamically fetched from backend API.

### Stage 7: Edge Vision & Image Preprocessing
- **Goal:** Implement computer vision enhancement pipeline for difficult lighting and weather conditions.
- **Deliverables:** OpenCV-based CLAHE contrast adjustment, glare reduction, shadow mitigation, and de-blurring filters.
- **Verification:** Process sample degraded images and verify enhancement quality metrics.

### Stage 8: ANPR & OCR Pipeline
- **Goal:** Number plate localization and character recognition with Indian RTO compliance checks.
- **Deliverables:** Plate detection bounding box model, PaddleOCR character reader, RTO regex / structural anomaly validator (broken, modified, non-standard plates).
- **Verification:** Accurate text recognition on sample test plate images with anomaly flags raised on non-standard plates.

### Stage 9: Vehicle Visual Signature (Re-ID)
- **Goal:** Multi-feature vehicle attribute extraction for cross-camera re-identification.
- **Deliverables:** Vehicle color classifier, vehicle type classifier (Sedan/SUV/Truck/Two-Wheeler), attribute flags (tinted windows, roof rails, damage).
- **Verification:** Signature extraction returns consistent feature vector on identical vehicles.

### Stage 10: Multi-Camera Tracking
- **Goal:** Associate vehicle detections across consecutive camera locations.
- **Deliverables:** Association algorithm combining license plate identity with visual signature similarity for missing/occluded plates.
- **Verification:** Successfully tracks a test vehicle across 3 consecutive camera nodes.

### Stage 11: Spatio-Temporal Graph Engine
- **Goal:** Build the directed road graph model with physical distance, speed limits, and minimum travel time bounds.
- **Deliverables:** Graph builder, shortest path travel time calculator, movement feasibility validator.
- **Verification:** Accurately computes $T_{\min}(A, B)$ and identifies feasible transitions.

### Stage 12: Ghost / Cloned Plate Detection
- **Goal:** Detect physically impossible vehicle transitions and raise high-confidence ghost plate alerts.
- **Deliverables:** Anomaly detection service comparing observed $\Delta t$ against $T_{\min}$; evidence bundle generator with dual snapshot comparisons.
- **Verification:** Synthetic impossible transition triggers immediate `GHOST_PLATE_ALERT` with full forensic evidence.

### Stage 13: Law Enforcement & Watchlist System
- **Goal:** Blacklist and stolen vehicle monitoring, search interface, and real-time alert dispatch.
- **Deliverables:** Watchlist management CRUD, plate search with fuzzy matching, chronological trajectory history viewer with GIS route trail.
- **Verification:** Sighting of a blacklisted plate triggers instant alert and highlights route on map.

### Stage 14: Urban Traffic Flow & Analytics
- **Goal:** Compute city traffic metrics, congestion heatmaps, choke points, and emergency corridor routing.
- **Deliverables:** Aggregation workers for traffic density, speed deviations, bottleneck detection, and Recharts analytics dashboard.
- **Verification:** Accurate density charts and choke point lists rendered from test event stream.

### Stage 15: Dashboard Integration & Real-Time WebSockets
- **Goal:** Connect all frontend views to backend REST and WebSocket event streams.
- **Deliverables:** Real-time event feed, live alert notifications, dynamic camera grid, synchronized GIS trajectory replay.
- **Verification:** Emitted events update map markers, alerts table, and graphs in real time without page refresh.

### Stage 16: Simulation & Demo Engine
- **Goal:** Build an end-to-end scenario player for SIH hackathon demonstrations.
- **Deliverables:** Scenario presets (e.g., "Normal City Flow", "Stolen Vehicle Pursuit", "Ghost Plate Anomaly", "Ambulance Green Corridor").
- **Verification:** One-click demo triggers realistic multi-camera event sequence showcasing all 5 feature groups.

### Stage 17: Testing, Polish & Optimization
- **Goal:** Comprehensive end-to-end verification, performance tuning, UI/UX polish, and error resilience.
- **Deliverables:** Automated integration test suite, response time benchmarks, polished UI with zero dead links.
- **Verification:** All tests passing, smooth 60fps UI performance, zero unhandled errors.

### Stage 18: SIH Finalization & Demo Preparation
- **Goal:** Final packaging, pitch deck alignment, demonstration video recording, and repository documentation.
- **Deliverables:** Completed SIH pitch materials, final user manual, reproducible demo walkthrough.

---

*VISION_FLOW — Development Roadmap*
