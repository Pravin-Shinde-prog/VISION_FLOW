# VISION_FLOW — Frontend Dashboard

This directory will contain the interactive web dashboard for **VISION_FLOW**.

---

## 🛠️ Planned Technology Stack

- **Framework:** React 18+
- **Build Tool:** Vite
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Mapping / GIS:** Leaflet / OpenStreetMap and/or Google Maps Platform
- **Data Visualization & Charts:** Recharts
- **Real-Time Communication:** Native WebSockets / Socket.io Client
- **State Management:** React Context / Zustand / TanStack Query (as required in Stage 3)

---

## 📁 Target Directory Structure (To be scaffolded in Stage 3)

```
frontend/
├── public/                 # Static assets, map markers, favicons
├── src/
│   ├── assets/             # Images, logos, UI iconography
│   ├── components/         # Reusable UI components (Modals, Tables, Cards, Badges)
│   │   ├── common/         # Buttons, dropdowns, search inputs, status chips
│   │   ├── layout/         # Header, Sidebar, View Switcher, Notification Bar
│   │   ├── map/            # GIS Map Canvas, Camera Markers, Route Polylines
│   │   ├── feeds/          # Live Multi-Camera Grid & Video Playback Cards
│   │   ├── alerts/         # Law Enforcement Incident Ticker & Alert Banners
│   │   └── analytics/      # Traffic Density Charts, Choke-Point Visualizers
│   ├── views/              # Primary application views
│   │   ├── LiveMonitorView.tsx     # Multi-camera live streams & instant detections
│   │   ├── GisTrackingView.tsx     # Interactive city map & vehicle route replay
│   │   ├── VehicleSearchView.tsx   # Plate search, visual signature & history filter
│   │   ├── AlertsView.tsx          # Law enforcement watchlist & ghost plate alerts
│   │   └── TrafficAnalyticsView.tsx# Choke points, corridor delays & heatmaps
│   ├── services/           # API client, WebSocket managers, simulation connectors
│   ├── hooks/              # Custom React hooks (useCameraStream, useAlerts, useMap)
│   ├── types/              # TypeScript interfaces (DetectionEvent, CameraNode, Alert)
│   ├── utils/              # Formatters, coordinate converters, math helpers
│   ├── App.tsx             # Root application component
│   └── main.tsx            # Vite React entrypoint
├── index.html              # HTML shell
├── package.json            # Node dependencies
├── tailwind.config.js      # Tailwind styling configuration
├── tsconfig.json           # TypeScript compiler configuration
└── vite.config.ts          # Vite build configuration
```

---

## 🔒 Stage 1 Status Note

In accordance with **Stage 1: Foundation**, no frontend dependencies or UI components have been installed or scaffolded yet. The complete frontend shell will be initialized in **Stage 3: Frontend Shell**.
