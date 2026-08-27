# VISION_FLOW — System Architecture & Data Flow Specification

## 1. Executive Architecture Summary

**VISION_FLOW** is designed as a distributed, event-driven urban intelligence platform. It decouples high-throughput video processing at the edge from centralized spatio-temporal graph analysis, law enforcement alerts, and city-wide traffic intelligence.

The architecture ensures that whether the system receives simulated synthetic camera events, prerecorded traffic video clips, or real-time RTSP streams from physical edge cameras, the core ingestion, graph validation, analytics, and visualization layers function uniformly without modification.

---

## 2. End-to-End Data Flow

```
+-----------------------------------------------------------------------------------+
| 1. VIDEO SOURCE LAYER                                                             |
|    - Prerecorded Multi-Angle Traffic Video Clips (Demo/Prototype)                 |
|    - Synthetic Event Stream Generator (Load Testing / Edge Case Simulation)       |
|    - Future: Physical RTSP/H.264 City CCTV Cameras                                |
+-----------------------------------------+-----------------------------------------+
                                          | Raw Frames / Video Stream
                                          v
+-----------------------------------------------------------------------------------+
| 2. SMART EDGE VISION & PREPROCESSING (Conceptual Edge Node / Ingestion Service)   |
|    - Dynamic Contrast & Exposure Normalization (CLAHE, Gamma Correction)          |
|    - Glare, Shadow, Rain & Motion Blur Mitigation                                  |
|    - Vehicle & License Plate Detection (YOLO)                                     |
|    - Optical Character Recognition & RTO Plate Format Validation (PaddleOCR)       |
|    - Visual Feature Extraction (Color, Vehicle Type, Visual Signatures)           |
+-----------------------------------------+-----------------------------------------+
                                          | Lightweight Detection Event (JSON)
                                          v
+-----------------------------------------------------------------------------------+
| 3. INGESTION & CENTRAL BACKEND LAYER (FastAPI + Asynchronous Workers)            |
|    - Event Receiver API (REST / WebSockets / MQTT Gateway)                        |
|    - Schema Validation & Timestamp Synchronization                                |
|    - PostGIS Spatial & Relational Persistence                                     |
+-------------------+-----------------------------------+---------------------------+
                    |                                   |
                    v                                   v
+-----------------------------------+   +-------------------------------------------+
| 4. SPATIO-TEMPORAL GRAPH ENGINE   |   | 5. LAW ENFORCEMENT & SAFETY ENGINE        |
|    - Directed Camera Road Graph   |   |    - Watchlist / Blacklist Matching       |
|    - Feasibility & Time Bounds    |   |    - Stolen Vehicle Alert Dispatcher      |
|    - Multi-Feature Vehicle Re-ID  |   |    - Real-Time WebSocket Push Alerts      |
|    - Trajectory Reconstruction    |   |    - Forensic Audit Trail & Snapshots     |
|    - Ghost/Cloned Plate Anomaly   |   +---------------------+---------------------+
+-------------------+---------------+                         |
                    |                                         |
                    +-------------------+                     |
                                        v                     v
+-----------------------------------------------------------------------------------+
| 6. URBAN TRAFFIC ANALYTICS ENGINE                                                 |
|    - Road Segment Vehicle Counts & Density Heatmaps                               |
|    - Choke-Point Detection & Average Speed Estimation                             |
|    - Corridor Travel Delay Metrics & Origin-Destination Patterns                  |
|    - Emergency Green Corridor Flow Optimization                                   |
+-----------------------------------------+-----------------------------------------+
                                          | Aggregated Metrics & Live Push Streams
                                          v
+-----------------------------------------------------------------------------------+
| 7. WEB DASHBOARD & GIS INTERACTION LAYER (React + Vite + TypeScript + Tailwind)   |
|    - Real-Time Multi-Camera Grid & Feed Playback                                  |
|    - Interactive Spatio-Temporal GIS Map (Leaflet / Google Maps)                  |
|    - Plate & Visual Signature Trajectory Query Tool                               |
|    - High-Priority Law Enforcement Incident Console                               |
|    - City Traffic Operations Analytics Dashboard (Recharts)                       |
+-----------------------------------------------------------------------------------+
```

---

## 3. Interaction Matrix of the Five Core Feature Groups

The five core feature groups operate cooperatively to form an intelligent feedback loop:

| Feature Group | Primary Inputs | Core Transformation | Output To Downstream Components |
| :--- | :--- | :--- | :--- |
| **1. Smart Edge Vision & Plate Preprocessing** | Raw video feed / frames | Image enhancement, YOLO detection, ANPR OCR, plate anomaly checks | Lightweight JSON detection event $\to$ Backend Ingestion |
| **2. Multi-Feature Vehicle Tracking (Re-ID)** | Detection event + cropped vehicle image | Extracts color, type, make, window tint, stickers, damage signature | Vehicle Association Engine & Spatio-Temporal Engine |
| **3. Spatio-Temporal Graph Engine** | Consecutive detection events for a vehicle ID / signature | Compares observed transition time $(\Delta t)$ vs shortest path $t_{min}$ on directed camera graph | Validated Trajectory $\to$ Dashboard; Ghost Plate Anomaly $\to$ Law Enforcement |
| **4. Law Enforcement & Safety Operations** | Ingested plate numbers, visual signatures, and graph anomalies | Matches against stolen/blacklisted databases; aggregates forensic snapshots | Instant Push Alerts $\to$ Web Dashboard; GIS Trajectory View |
| **5. Urban Traffic Flow & Analytics** | Aggregated vehicle counts, timestamps, and camera edge transitions | Computes segment density, choke points, average corridor speeds, bottleneck zones | Heatmaps, Corridor Delay Charts, Emergency Green Corridors $\to$ Web Dashboard |

---

## 4. Edge-to-Cloud Metadata Contract

Edge nodes do not transmit heavy continuous video streams across city networks. Instead, edge nodes process video locally and emit lightweight detection event payloads.

### JSON Payload Schema:
```json
{
  "event_id": "evt_984f2b1a-6d33-4f28-b80c-08246d87e14a",
  "camera_id": "CAM_DEL_042",
  "timestamp": "2026-08-27T10:15:30.450Z",
  "frame_sequence": 14205,
  "detection": {
    "plate": {
      "number": "DL01AB1234",
      "confidence": 0.964,
      "is_valid_format": true,
      "anomaly_flags": {
        "is_broken": false,
        "is_non_standard": false,
        "is_modified": false,
        "is_missing": false
      },
      "bbox": [540, 680, 710, 735]
    },
    "vehicle": {
      "type": "SUV",
      "color": "Dark Blue",
      "color_confidence": 0.91,
      "make_model_estimate": "Hyundai Creta",
      "features": {
        "tinted_windows": true,
        "roof_rails": true,
        "stickers_detected": false,
        "visible_damage": false
      },
      "visual_embedding": [-0.042, 0.185, -0.091, 0.724, "... 128-dim vector ..."],
      "bbox": [320, 310, 940, 810]
    }
  },
  "snapshot_ref": "/media/snapshots/20260827/CAM_DEL_042_evt984f2b1a.jpg"
}
```

---

## 5. Spatio-Temporal Graph Engine Mathematical Formulation

The physical city road and camera deployment is modeled as a **Directed Attributed Graph** $G = (V, E)$:

- **$V$ (Vertices):** Set of ANPR camera nodes $\{v_1, v_2, \dots, v_n\}$, each having spatial coordinates $(\text{lat}_i, \text{lon}_i)$ and field-of-view vector $\vec{\theta}_i$.
- **$E$ (Edges):** Set of directed road segments $(v_i, v_j)$ where vehicles can directly travel from camera $v_i$ to camera $v_j$ without passing other intermediate ANPR cameras.
- **Edge Attributes:** Each directed edge $e_{ij} = (v_i, v_j)$ is characterized by:
  - $d_{ij}$: Physical road distance (meters/km).
  - $v_{\max, ij}$: Legal/practical maximum speed limit $(\text{km/h})$.
  - $t_{\min, ij}$: Minimum physically feasible travel time:
    $$t_{\min, ij} = \frac{d_{ij}}{v_{\max, ij} + \delta_{\text{tolerance}}}$$
  - $t_{\text{avg}, ij}(t)$: Historical/real-time expected travel time factoring in congestion.

### Feasible Trajectory & Ghost Plate Detection Logic:

Suppose vehicle detection $D_1 = (v_A, t_1)$ with license plate $P$ is recorded, followed by detection $D_2 = (v_B, t_2)$ with the same license plate $P$, where $t_2 > t_1$.

1. **Observed Travel Time:** $\Delta t_{\text{observed}} = t_2 - t_1$.
2. **Shortest Feasible Travel Time:** Let $\mathcal{P}_{AB}$ be the shortest path from $v_A$ to $v_B$ in $G$. The minimum theoretical travel time is:
   $$T_{\min}(v_A, v_B) = \sum_{e_{ij} \in \mathcal{P}_{AB}} t_{\min, ij}$$
3. **Ghost / Cloned Plate Condition:**
   - If $\Delta t_{\text{observed}} < T_{\min}(v_A, v_B)$, the physical movement is **physically impossible**.
   - If no directed path exists from $v_A$ to $v_B$ in graph $G$, the movement violates road directionality or topology.
   - $\implies$ **Trigger `GHOST_PLATE_ALERT`** with evidence:
     - Detection 1 Snapshot + Location + Timestamp
     - Detection 2 Snapshot + Location + Timestamp
     - Required Minimum Time vs Actual Observed Time.

---

## 6. Multi-Feature Vehicle Re-Identification (Re-ID)

When a vehicle passes a camera with a broken, occluded, or deliberately covered license plate, the system falls back to multi-feature matching:

$$\text{Similarity}(V_A, V_B) = w_c \cdot S_{\text{color}}(C_A, C_B) + w_t \cdot S_{\text{type}}(T_A, T_B) + w_e \cdot \text{CosineSim}(\vec{E}_A, \vec{E}_B) + w_f \cdot S_{\text{features}}(F_A, F_B)$$

Where:
- $S_{\text{color}}$: Color space distance.
- $S_{\text{type}}$: Categorical vehicle type match (Sedan, SUV, Truck, Hatchback, Two-Wheeler).
- $\vec{E}$: Deep visual feature embedding vector.
- $S_{\text{features}}$: Physical markings, tint, roof racks, and damage flags.
- $\sum w = 1.0$: Calibrated feature weights.

If $\text{Similarity}(V_A, V_B) \ge \tau_{\text{match}}$, the detection is linked into the active trajectory graph even in the absence of an OCR plate read.

---

## 7. Law Enforcement & Safety Operations

The backend maintains high-speed in-memory indexing of:
- **Hot-Lists / Watchlists:** Stolen vehicles, vehicles involved in active investigations, suspended registrations.
- **Plate Anomaly Feeds:** Non-standard plates, mismatched vehicle types (e.g. plate registered to a hatchback seen on a heavy truck).

When an edge event arrives:
1. Exact match check against active watchlist.
2. Anomaly evaluation from the Spatio-Temporal Graph Engine.
3. If an alert fires, a WebSocket notification with priority level, camera coordinates, plate, and snapshot URL is pushed to the Law Enforcement Console within $< 100 \text{ms}$.

---

## 8. Urban Traffic Flow & City Analytics

The platform computes running window metrics over the camera network:
- **Segment Density:** Number of unique vehicles passing camera $v_i$ per minute.
- **Choke-Point Index:** Ratio of observed travel time to free-flow travel time on edge $e_{ij}$:
  $$\text{ChokeIndex}(e_{ij}) = \frac{t_{\text{observed}, ij}}{t_{\text{freeflow}, ij}}$$
- **Congestion Heatmap:** Spatial interpolation across camera node density scores.
- **Emergency Corridor Optimization:** Predicts arrival times and optimizes signal corridor pathways for ambulances and fire services.

---

## 9. Simulation Adapter vs. Real-Camera Ingestion

To facilitate thorough evaluation and SIH jury demonstrations:

1. **Simulation / Prerecorded Mode:**
   - Reads prerecorded MP4/AVI clips from `data/sample_videos/`.
   - Replays synthetic JSON event series from `data/synthetic_events/`.
   - Injects controllable anomalies (e.g., triggering a ghost plate test by injecting sightings of DL01AB1234 at two opposite city poles 30 seconds apart).
2. **Production / Real-Camera Mode:**
   - Replaces video file reader with standard RTSP / WebRTC stream decoders.
   - Replaces synthetic generator with live Edge Gateway REST / MQTT endpoints.
   - The entire backend, database, graph engine, and frontend dashboard require zero code changes.

---

*VISION_FLOW — Architectural Design Document*
