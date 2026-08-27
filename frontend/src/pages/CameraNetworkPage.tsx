import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Video,
  Activity,
  AlertTriangle,
  Radio,
  Share2,
  RefreshCw,
  Search,
  Filter,
  Maximize2,
  Map as MapIcon,
  Compass,
  AlertCircle,
  Eye,
  EyeOff,
  Sun,
  Moon,
  ListFilter
} from 'lucide-react';
import { Camera, RoadEdge, CameraListResponse, RoadEdgeListResponse } from '../types/camera';
import { fetchCameras, fetchRoadEdges } from '../services/api';
import { CameraMap } from '../components/map/CameraMap';
import { CameraDetailPanel } from '../components/map/CameraDetailPanel';

export const CameraNetworkPage: React.FC = () => {
  // Data state
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [roadEdges, setRoadEdges] = useState<RoadEdge[]>([]);
  const [summaryCounts, setSummaryCounts] = useState({
    total: 0,
    online: 0,
    warning: 0,
    offline: 0,
    edges: 0,
  });

  // UI & filter state
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sectorFilter, setSectorFilter] = useState<string>('all');
  const [showEdges, setShowEdges] = useState<boolean>(true);
  const [mapTheme, setMapTheme] = useState<'dark' | 'standard'>('dark');
  const [showSidebarList, setShowSidebarList] = useState<boolean>(true);

  // Load cameras and road edges from FastAPI backend
  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [cameraRes, edgeRes]: [CameraListResponse, RoadEdgeListResponse] = await Promise.all([
        fetchCameras(),
        fetchRoadEdges(true),
      ]);

      setCameras(cameraRes.items);
      setRoadEdges(edgeRes.items);
      setSummaryCounts({
        total: cameraRes.total,
        online: cameraRes.online_count,
        warning: cameraRes.warning_count,
        offline: cameraRes.offline_count,
        edges: edgeRes.total,
      });

      // Auto-select first camera if none selected
      if (cameraRes.items.length > 0 && !selectedCamera) {
        setSelectedCamera(cameraRes.items[0]);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to connect to backend';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [selectedCamera]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Extract unique sectors for filter dropdown
  const uniqueSectors = useMemo(() => {
    const set = new Set<string>();
    cameras.forEach((c) => {
      if (c.sector) set.add(c.sector);
    });
    return Array.from(set).sort();
  }, [cameras]);

  // Filter cameras based on search and selection
  const filteredCameras = useMemo(() => {
    return cameras.filter((cam) => {
      const matchesSearch =
        searchQuery.trim() === '' ||
        cam.camera_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        cam.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (cam.road_name && cam.road_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (cam.sector && cam.sector.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesStatus =
        statusFilter === 'all' ||
        (statusFilter === 'online' && (cam.status === 'active' || cam.status === 'online')) ||
        (statusFilter === 'warning' && cam.status === 'warning') ||
        (statusFilter === 'offline' && (cam.status === 'offline' || cam.status === 'maintenance'));

      const matchesSector = sectorFilter === 'all' || cam.sector === sectorFilter;

      return matchesSearch && matchesStatus && matchesSector;
    });
  }, [cameras, searchQuery, statusFilter, sectorFilter]);

  const handleSelectConnected = (camCode: string) => {
    const found = cameras.find((c) => c.camera_id === camCode);
    if (found) {
      setSelectedCamera(found);
    }
  };

  return (
    <div className="flex flex-col gap-5 p-6 min-h-[calc(100vh-4rem)] max-w-[1700px] mx-auto text-slate-100">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-500/30">
              <Video className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                GIS Camera Network & Spatial Topology
                <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  LIVE GIS
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-0.5">
                City-wide ANPR/CCTV sensor nodes, topological directed road graph, and hardware telemetry (Pune, India).
              </p>
            </div>
          </div>
        </div>

        {/* Header Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setMapTheme(mapTheme === 'dark' ? 'standard' : 'dark')}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 transition-all"
            title="Toggle map tile color scheme"
          >
            {mapTheme === 'dark' ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-cyan-400" />}
            <span>{mapTheme === 'dark' ? 'Light Tiles' : 'Dark Tiles'}</span>
          </button>

          <button
            onClick={() => setShowEdges(!showEdges)}
            className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border transition-all ${
              showEdges
                ? 'bg-blue-600/20 text-blue-300 border-blue-500/40'
                : 'bg-slate-900 text-slate-400 border-slate-700 hover:bg-slate-800'
            }`}
            title="Toggle directed road connection polylines"
          >
            {showEdges ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            <span>Directed Graph</span>
          </button>

          <button
            onClick={() => setShowSidebarList(!showSidebarList)}
            className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border transition-all ${
              showSidebarList
                ? 'bg-blue-600/20 text-blue-300 border-blue-500/40'
                : 'bg-slate-900 text-slate-400 border-slate-700 hover:bg-slate-800'
            }`}
            title="Toggle camera directory panel"
          >
            <ListFilter className="w-3.5 h-3.5" />
            <span>Node Directory</span>
          </button>

          <button
            onClick={loadData}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20 disabled:opacity-50 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Network Telemetry Summary Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        {/* Total Cameras */}
        <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-xs text-slate-400 font-medium">Total Cameras</span>
            <div className="text-2xl font-bold text-slate-100 font-mono mt-0.5">
              {summaryCounts.total}
            </div>
          </div>
          <div className="p-2.5 bg-blue-600/10 text-blue-400 rounded-lg border border-blue-500/20">
            <Video className="w-5 h-5" />
          </div>
        </div>

        {/* Online / Active */}
        <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-xs text-slate-400 font-medium">Online Cameras</span>
            <div className="text-2xl font-bold text-emerald-400 font-mono mt-0.5">
              {summaryCounts.online}
            </div>
          </div>
          <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-lg border border-emerald-500/20">
            <Activity className="w-5 h-5" />
          </div>
        </div>

        {/* Warning / Degraded */}
        <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-xs text-slate-400 font-medium">Warning State</span>
            <div className="text-2xl font-bold text-amber-400 font-mono mt-0.5">
              {summaryCounts.warning}
            </div>
          </div>
          <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-lg border border-amber-500/20">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        {/* Offline */}
        <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-xs text-slate-400 font-medium">Offline</span>
            <div className="text-2xl font-bold text-rose-400 font-mono mt-0.5">
              {summaryCounts.offline}
            </div>
          </div>
          <div className="p-2.5 bg-rose-500/10 text-rose-400 rounded-lg border border-rose-500/20">
            <Radio className="w-5 h-5" />
          </div>
        </div>

        {/* Road Edges */}
        <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-4 flex items-center justify-between shadow-sm col-span-2 sm:col-span-1">
          <div>
            <span className="text-xs text-slate-400 font-medium">Road Connections</span>
            <div className="text-2xl font-bold text-cyan-400 font-mono mt-0.5">
              {summaryCounts.edges}
            </div>
          </div>
          <div className="p-2.5 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20">
            <Share2 className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-3.5 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 shadow-sm">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by Camera ID, junction, road, or sector..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3.5 py-1.5 bg-slate-900 border border-slate-700/80 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors font-sans"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-slate-200"
            >
              Clear
            </button>
          )}
        </div>

        {/* Status & Sector Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Status Tabs */}
          <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                statusFilter === 'all' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({summaryCounts.total})
            </button>
            <button
              onClick={() => setStatusFilter('online')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                statusFilter === 'online' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Online ({summaryCounts.online})
            </button>
            <button
              onClick={() => setStatusFilter('warning')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                statusFilter === 'warning' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Warning ({summaryCounts.warning})
            </button>
            <button
              onClick={() => setStatusFilter('offline')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                statusFilter === 'offline' ? 'bg-rose-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Offline ({summaryCounts.offline})
            </button>
          </div>

          {/* Sector Dropdown */}
          <div className="flex items-center gap-1.5 bg-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-800 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={sectorFilter}
              onChange={(e) => setSectorFilter(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer pr-2"
            >
              <option value="all" className="bg-slate-900 text-slate-200">
                All Sectors ({uniqueSectors.length})
              </option>
              {uniqueSectors.map((sec) => (
                <option key={sec} value={sec} className="bg-slate-900 text-slate-200">
                  {sec}
                </option>
              ))}
            </select>
          </div>

          {/* Reset Map Bounds */}
          <button
            onClick={() => setSelectedCamera(null)}
            className="flex items-center gap-1 px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg text-xs text-slate-300 transition-colors"
            title="Reset focus to fit all camera nodes"
          >
            <Maximize2 className="w-3.5 h-3.5 text-blue-400" />
            <span>Fit All</span>
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            <div>
              <span className="font-semibold">Backend Connection Error: </span>
              {error}
            </div>
          </div>
          <button
            onClick={loadData}
            className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Main Map & Directory Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 flex-1 min-h-[580px]">
        {/* Left Side / Collapsible Node Directory */}
        {showSidebarList && (
          <div className="lg:col-span-4 bg-[#0D1525] border border-slate-800 rounded-xl p-4 flex flex-col gap-3 max-h-[640px] overflow-hidden">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Compass className="w-4 h-4 text-blue-400" />
                Network Node Directory ({filteredCameras.length})
              </span>
              <span className="text-[11px] font-mono text-slate-500">Pune Network</span>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {filteredCameras.map((camera) => {
                const isSelected = selectedCamera?.camera_id === camera.camera_id;
                const status = camera.status.toLowerCase();

                let statusDot = 'bg-emerald-400';
                if (status === 'warning') statusDot = 'bg-amber-400';
                if (status === 'offline' || status === 'maintenance') statusDot = 'bg-rose-400';

                return (
                  <div
                    key={camera.camera_id}
                    onClick={() => setSelectedCamera(camera)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-blue-950/40 border-blue-500 shadow-md shadow-blue-500/10'
                        : 'bg-slate-900/60 border-slate-800 hover:bg-slate-800/80 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${statusDot}`} />
                        <span className="font-mono text-xs font-bold text-blue-400">
                          {camera.camera_id}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono uppercase text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                        {camera.sector || 'Sector'}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-slate-200 mt-1 truncate">
                      {camera.name}
                    </div>
                    <div className="text-[11px] text-slate-400 truncate mt-0.5">
                      {camera.road_name || 'Corridor Link'}
                    </div>
                  </div>
                );
              })}

              {filteredCameras.length === 0 && !isLoading && (
                <div className="py-12 text-center text-slate-500 text-xs">
                  No cameras match the current search or filters.
                </div>
              )}
            </div>
          </div>
        )}

        {/* Right Side: Leaflet Map Canvas with Detail Panel Overlay */}
        <div className={`${showSidebarList ? 'lg:col-span-8' : 'lg:col-span-12'} relative bg-[#0D1525] border border-slate-800 rounded-xl overflow-hidden min-h-[580px]`}>
          {isLoading && cameras.length === 0 ? (
            <div className="w-full h-full flex flex-col items-center justify-center gap-3 text-slate-400 min-h-[580px]">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              <span className="text-sm font-medium">Loading GIS Camera Network...</span>
            </div>
          ) : (
            <>
              <CameraMap
                cameras={filteredCameras}
                roadEdges={roadEdges}
                selectedCamera={selectedCamera}
                onSelectCamera={(cam) => setSelectedCamera(cam)}
                showEdges={showEdges}
                mapTheme={mapTheme}
              />

              {/* Floating Camera Detail Panel */}
              {selectedCamera && (
                <div className="absolute top-4 right-4 z-[400] w-full max-w-sm">
                  <CameraDetailPanel
                    camera={selectedCamera}
                    roadEdges={roadEdges}
                    onClose={() => setSelectedCamera(null)}
                    onSelectConnectedCamera={handleSelectConnected}
                  />
                </div>
              )}
            </>
          )}

          {/* Map Footer Bar */}
          <div className="absolute bottom-3 left-3 z-[400] bg-slate-950/90 border border-slate-800 backdrop-blur px-3 py-1.5 rounded-lg text-[11px] text-slate-400 flex items-center gap-3 shadow-lg font-mono">
            <span className="flex items-center gap-1 text-slate-300">
              <MapIcon className="w-3.5 h-3.5 text-blue-400" />
              Pune Metropolitan Area
            </span>
            <span className="text-slate-600">|</span>
            <span>SRID 4326</span>
            <span className="text-slate-600">|</span>
            <span className="text-cyan-300">{roadEdges.length} Directed Links</span>
          </div>
        </div>
      </div>
    </div>
  );
};
