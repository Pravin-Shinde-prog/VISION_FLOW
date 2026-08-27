# VISION_FLOW — Scripts & Automation Utilities

This directory contains automation utilities, developer toolchains, simulation drivers, and dataset preparation scripts for **VISION_FLOW**.

---

## 🛠️ Planned Scripts (To be created in respective roadmap stages)

1. **`simulate_events.py` (Stage 16):**
   - Emits synthetic detection events into the backend over WebSockets or HTTP to test the Spatio-Temporal Graph Engine and Dashboard live UI.

2. **`inject_anomalies.py` (Stage 12 & 16):**
   - Injects controlled edge cases such as ghost/cloned plate sightings, impossible speed transitions, and stolen vehicle watchlist hits for SIH jury presentations.

3. **`generate_city_graph.py` (Stage 6 & 11):**
   - Generates and seeds the directed camera network graph, computing topological distances and minimum travel time thresholds for a given city map.

4. **`download_sample_media.sh` (Stage 7 & 8):**
   - Downloads standardized, open-source sample traffic video clips and test images into `data/sample_videos/`.

---

## 🔒 Stage 1 Status Note

In accordance with **Stage 1: Foundation**, no operational execution scripts have been added yet. Scripts will be introduced alongside their corresponding backend and simulation stages.
