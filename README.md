# VISION_FLOW

**City-Wide AI Engine for Multi-Camera ANPR Trajectory Tracking and Urban Traffic Analytics**

---

## 📌 Project Overview

**VISION_FLOW** is an intelligent urban surveillance and traffic intelligence system designed for the **Smart India Hackathon (SIH)**. The platform provides a city-wide AI engine that combines edge-vision metadata extraction, multi-feature vehicle re-identification, spatio-temporal road graph validation, law enforcement watchlist monitoring, and real-time urban traffic analytics into a unified, interactive operations dashboard.

---

## 🎯 Problem Statement & Solution

### The Problem
Modern municipal CCTV infrastructure in smart cities faces critical limitations:
- **Siloed ANPR Cameras:** Number-plate readers operate as disconnected islands without contextual road-network intelligence.
- **Plate Tampering & Cloned/Ghost Plates:** Criminal elements exploit fake, modified, or cloned registration plates that easily bypass single-point ANPR systems.
- **Occlusion & Plate Damage:** Weather (glare, rain, shadows), dirt, or intentional physical plate obfuscation prevent traditional OCR tracking.
- **Manual Vehicle Re-Identification:** Operators must manually sift through hundreds of asynchronous camera feeds to reconstruct suspect trajectories.
- **Fragmented Traffic Analytics:** Congestion monitoring and corridor optimization are decoupled from vehicle detection feeds.

### The VISION_FLOW Solution
VISION_FLOW introduces a graph-validated multi-camera pipeline that:
1. Enhances degraded edge video feeds and performs high-accuracy ANPR along with RTO compliance checks.
2. Extracts multi-feature visual signatures (color, vehicle type, make/model, damage, stickers) to track vehicles across cameras even without visible plates.
3. Maps camera deployments to a **Spatio-Temporal Directed Road Graph**, verifying whether physical vehicle transitions are mathematically and physically feasible.
4. Detects **ghost/cloned plates** in real time by identifying physically impossible transitions across distant nodes.
5. Equips law enforcement with instant watchlist alerts, evidence forensics, and chronological GIS trajectory reconstruction.
6. Computes actionable city-wide traffic metrics including corridor delays, choke-point heatmaps, and green-corridor management.

---

## ⚡ The Five Core Feature Groups

```
+-------------------------------------------------------------------------------+
|                                 VISION_FLOW                                   |
+-------------------------------------------------------------------------------+
| 1. Smart Edge Vision & Plate Preprocessing                                    |
|    - Image enhancement (contrast, exposure, glare, shadow, rain, blur)        |
|    - High-accuracy ANPR & OCR                                                 |
|    - RTO number-plate compliance (broken, modified, missing plates)          |
|    - Lightweight edge metadata extraction                                     |
+-------------------------------------------------------------------------------+
| 2. Multi-Feature Vehicle Tracking (Re-ID)                                     |
|    - Visual signature extraction: Color, Type, Make/Model, Window Tint        |
|    - Distinctive physical marks, stickers, damage                             |
|    - Cross-camera vehicle association under plate occlusion/absence           |
+-------------------------------------------------------------------------------+
| 3. Spatio-Temporal Graph Engine                                               |
|    - Directed road/camera network graph (Nodes, Weighted Edges)               |
|    - Feasible forward movement & travel-time validation                       |
|    - Automated vehicle trajectory reconstruction                              |
|    - Real-time Ghost / Cloned Plate anomaly detection                         |
+-------------------------------------------------------------------------------+
| 4. Law Enforcement & Safety Operations                                        |
|    - Blacklisted and stolen vehicle monitoring & real-time alerts             |
|    - Search by plate number or visual signature query                         |
|    - Chronological camera-by-camera trajectory with GIS visualization         |
|    - Forensic evidence capture with snapshot audit trail                      |
+-------------------------------------------------------------------------------+
| 5. Urban Traffic Flow & City Analytics                                        |
|    - Real-time traffic density & choke-point detection                       |
|    - Congestion heatmaps & corridor delay analysis                            |
|    - Origin-destination flow insights                                         |
|    - Priority emergency/ambulance corridor intelligence                      |
+-------------------------------------------------------------------------------+
```

> **Scope Note:** VISION_FLOW is strictly focused on vehicle tracking, ANPR compliance, spatio-temporal validation, and traffic analytics. It does **not** include helmet detection or unrelated traffic violations.

---

## 💡 Prototype Philosophy

VISION_FLOW is being developed as an **engineering prototype for Smart India Hackathon (SIH)**.

- **Realistic Ingestion:** Where live municipal CCTV network access is restricted, the system seamlessly ingests **simulated camera data, prerecorded city traffic video feeds, and synthetic camera event streams**.
- **Real Engineering & Genuine Functionality:** Every button, filter, map route, analytics calculation, and alert trigger is driven by actual underlying application logic. There are **no static mockups or non-functional placeholder buttons**.
- **Edge-Ready Architecture:** Edge cameras conceptually process raw video and emit lightweight JSON metadata payloads to the central backend, reflecting enterprise smart-city IoT deployments.

---

## 🛠️ Planned Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React, Vite, TypeScript, Tailwind CSS, Lucide Icons |
| **Visualization & GIS** | Leaflet / OpenStreetMap / Google Maps Platform, Recharts |
| **Backend API** | Python, FastAPI, Uvicorn, WebSockets |
| **Database & GIS Store** | PostgreSQL, PostGIS, SQLAlchemy / asyncpg |
| **Computer Vision & AI** | Python, OpenCV, YOLO (Object Detection), PaddleOCR (ANPR) |
| **Graph & Validation** | NetworkX / Custom Spatio-Temporal Graph Algorithms |
| **Dev Environment** | Linux / WSL Ubuntu, VS Code, Git, GitHub |

---

## 🏛️ High-Level System Architecture

```
[ City CCTV / Prerecorded Feeds / Video Simulator ]
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│        1. SMART EDGE VISION & OCR PIPELINE              │
│  - Glare/Rain/Blur Correction & Enhancement             │
│  - Vehicle & Plate Bounding Box Detection (YOLO)        │
│  - ANPR & RTO Plate Compliance Engine (PaddleOCR)       │
│  - Visual Signature Extraction (Color/Type/Features)    │
└────────────────────────────┬────────────────────────────┘
                             │ Lightweight Metadata Payload (JSON)
                             ▼
┌─────────────────────────────────────────────────────────┐
│        2. FASTAPI BACKEND & EVENT INGESTION             │
│  - REST & WebSocket Ingestion Handlers                  │
│  - PostGIS Spatio-Temporal Persistence                  │
└──────────────┬───────────────────────────┬──────────────┘
               │                           │
               ▼                           ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ 3. SPATIO-TEMPORAL ENGINE   │ │ 4. LAW ENFORCEMENT & ALERTS │
│ - Directed Road Graph Model │ │ - Watchlist / Stolen Match  │
│ - Feasibility & Time Checks │ │ - High-Priority Push Alerts │
│ - Ghost Plate Anomaly Logic │ │ - Forensic Snapshot Trail   │
│ - Trajectory Reconstruction │ └──────────────┬──────────────┘
└──────────────┬──────────────┘                │
               │                               │
               ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ 5. TRAFFIC ANALYTICS ENGINE │ │ 6. UNIFIED WEB DASHBOARD    │
│ - Density & Choke Points    │ │ - Live Multi-Camera Monitor │
│ - Corridor Delay Heatmaps   │ │ - Interactive GIS Map View  │
│ - Emergency Green Corridor  │ │ - Vehicle Search & Trajectory│
└──────────────┬──────────────┘ │ - Traffic Analytics Charts  │
               │                └─────────────────────────────┘
               └───────────────────────────────▲
```

---

## 📁 Repository Structure

```
VISION_FLOW/
├── frontend/             # React + Vite + TypeScript web dashboard
├── backend/              # FastAPI Python server, services, and APIs
├── docs/                 # Architecture, specifications, and development roadmaps
│   ├── architecture.md   # Deep-dive architecture and data flow document
│   └── roadmap.md        # 18-stage development roadmap
├── data/                 # Sample media, GIS files, and synthetic event data
│   ├── sample_videos/    # Prerecorded traffic video clips for prototype demo
│   ├── synthetic_events/ # Generated telemetry event streams for graph testing
│   └── geo/              # GeoJSON road networks, camera coordinates, GIS data
├── scripts/              # Helper utilities, event generators, and data scripts
├── .gitignore            # Comprehensive ignore configuration
└── README.md             # Project overview and system guide
```

---

## 🗺️ Planned Development Stages

Development is structured into 18 controlled stages:

1. **Stage 1: Foundation** *(Current)* — Workspace structure, `.gitignore`, system architecture, and roadmap.
2. **Stage 2: Git/GitHub** — Version control setup and repository governance.
3. **Stage 3: Frontend Shell** — React + TypeScript + Tailwind UI skeleton and navigation layout.
4. **Stage 4: Backend Foundation** — FastAPI app structure, modular routers, health endpoints, CORS.
5. **Stage 5: Database/PostGIS** — Spatial database schema, models, migrations, and test seeds.
6. **Stage 6: GIS/Camera Network** — Map rendering, camera placement, road network overlay.
7. **Stage 7: Edge Vision & Image Preprocessing** — Glare/shadow/rain filtering, image enhancement.
8. **Stage 8: ANPR/OCR** — Number plate extraction, OCR reader, RTO compliance anomaly detector.
9. **Stage 9: Vehicle Visual Signature** — Color, type, make, and attribute extraction for Re-ID.
10. **Stage 10: Multi-Camera Tracking** — Cross-camera identity linking and correlation.
11. **Stage 11: Spatio-Temporal Graph** — Directed camera graph, edge weights, travel time feasibility.
12. **Stage 12: Ghost/Cloned Plate Detection** — Impossible transition detection & alert generator.
13. **Stage 13: Law Enforcement/Watchlist** — Blacklist queries, stolen vehicle alerts, audit trails.
14. **Stage 14: Traffic Analytics** — Density calculation, choke points, corridor speed and delay.
15. **Stage 15: Dashboard Integration** — Real-time WebSocket event streaming to UI.
16. **Stage 17: Testing & Polish** — End-to-end integration tests and UI refinement.
17. **Stage 18: GitHub Finalization & SIH Demo Preparation** — Demo script, scenario datasets, documentation.

---

## 🔮 Future Real-Camera Integration Concept

While the hackathon prototype executes on prerecorded traffic videos and synthetic telemetry feeds, the system is architected for zero-refactor real-world deployment:

- **Standardized Edge Metadata Protocol:** The backend consumes normalized JSON detection events (`camera_id`, `timestamp`, `plate_number`, `vehicle_type`, `vehicle_color`, `signature_vector`, `snapshot_ref`).
- **Protocol Agnostic Ingestion:** Physical edge smart cameras or edge AI gateways (NVIDIA Jetson, Intel OpenVINO devices) can push payloads over MQTT, WebSockets, or HTTPS REST without modifying the Spatio-Temporal Graph Engine or Analytics services.
- **RTSP Stream Direct Binding:** The dashboard layout supports plugging live RTSP / HLS video endpoints directly into the camera monitoring grid when city feeds are provisioned.

---

## 💻 Environment & Compatibility

- **Primary OS:** Linux (Ubuntu under WSL2)
- **Editor:** Visual Studio Code
- **Version Control:** Git

---

*VISION_FLOW — Smart India Hackathon (SIH)*
