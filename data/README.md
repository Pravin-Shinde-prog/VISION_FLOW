# VISION_FLOW — Data Directory

This directory houses datasets, geographic road models, synthetic telemetry events, and sample video clips used for local development, testing, and SIH demonstrations.

---

## 📁 Subdirectory Breakdown

### 1. `sample_videos/`
- **Purpose:** Stores sample traffic video recordings (MP4/AVI) representing multi-camera road corridors for demo playback.
- **Git Policy:** Binary video files (`*.mp4`, `*.avi`, etc.) are ignored via root `.gitignore` to maintain a lightweight repository. Sample reference manifests or download instructions will be documented here.

### 2. `synthetic_events/`
- **Purpose:** Contains structured JSON event traces representing continuous multi-camera vehicle sightings across the city road graph.
- **Use Cases:** Load testing, reproducible simulation of ghost plate scenarios, ambulance priority corridors, and complex vehicle tracking without requiring live GPU feeds.

### 3. `geo/`
- **Purpose:** Stores GIS metadata including:
  - GeoJSON files of urban road networks and junctions.
  - Camera placement coordinates (Latitude, Longitude, Direction angle).
  - Precalculated road segment distances and normal traversal times.

---

## 🔒 Data & Media Guidelines

- Do not commit large binary model checkpoints (`*.pt`, `*.onnx`) or multi-gigabyte video dumps to Git.
- Always provide reproducible generator scripts in `scripts/` to generate or fetch required test datasets.
