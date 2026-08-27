import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Cpu,
  Upload,
  RefreshCw,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Eye,
  Clock,
  ScanLine,
  Image as ImageIcon,
  Zap,
  BarChart3,
  ArrowRight,
  Database,
  ShieldCheck,
} from 'lucide-react';
import {
  fetchSampleFrames,
  processANPRSample,
  processANPRUpload,
  runANPRBenchmark,
} from '../services/api';
import { SampleFrameInfo } from '../types/edgeVision';
import {
  ANPRProcessResponse,
  ANPRBenchmarkResponse,
} from '../types/anpr';

export const EdgeVisionPage: React.FC = () => {
  const [samples, setSamples] = useState<SampleFrameInfo[]>([]);
  const [selectedSampleId, setSelectedSampleId] = useState<string>('clean_hsrp_day');
  const [activeMode, setActiveMode] = useState<'workbench' | 'benchmark'>('workbench');
  const [activeVisualTab, setActiveVisualTab] = useState<'annotated' | 'crop' | 'edges'>('annotated');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [persistToDb, setPersistToDb] = useState<boolean>(false);
  const [result, setResult] = useState<ANPRProcessResponse | null>(null);
  const [benchmarkResult, setBenchmarkResult] = useState<ANPRBenchmarkResponse | null>(null);
  const [isRunningBenchmark, setIsRunningBenchmark] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // File upload ref
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadSamples = useCallback(async () => {
    try {
      const data = await fetchSampleFrames();
      setSamples(data);
    } catch {
      // Non-blocking fallback
    }
  }, []);

  const runPipelineOnSample = useCallback(async (sampleId: string, persist: boolean = false) => {
    setIsProcessing(true);
    setError(null);
    try {
      const res = await processANPRSample(sampleId, persist);
      setResult(res);
      setSelectedSampleId(sampleId);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'ANPR processing failed';
      setError(msg);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  useEffect(() => {
    loadSamples();
    runPipelineOnSample('clean_hsrp_day', false);
  }, [loadSamples, runPipelineOnSample]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    setError(null);
    try {
      const res = await processANPRUpload(file, persistToDb);
      setResult(res);
      setSelectedSampleId('custom_upload');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload processing failed';
      setError(msg);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRunBenchmark = async () => {
    setIsRunningBenchmark(true);
    setError(null);
    try {
      const res = await runANPRBenchmark();
      setBenchmarkResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Benchmark failed';
      setError(msg);
    } finally {
      setIsRunningBenchmark(false);
    }
  };

  const primaryPlate = result?.primary_plate;
  const ocrResult = primaryPlate?.ocr_result;

  return (
    <div className="space-y-6 text-slate-100">
      {/* Top Banner */}
      <div className="rounded-xl border border-slate-800 bg-gradient-to-r from-[#111827] via-[#131C31] to-[#111827] p-6 lg:p-8 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-blue-500 animate-ping" />
              <span className="text-xs font-mono font-semibold uppercase tracking-widest text-blue-400">
                Stage 8 • Edge Vision &amp; License Plate OCR
              </span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold tracking-tight text-white font-mono flex items-center gap-3">
              <Cpu className="w-8 h-8 text-blue-400" />
              <span>Smart Edge Vision &amp; ANPR Workbench</span>
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              End-to-end edge pipeline combining image enhancement, candidate plate localization,
              character stroke recognition, Indian registration positional normalization, and RTO format validation.
            </p>
          </div>

          <div className="flex flex-wrap lg:flex-col gap-2.5 shrink-0 font-mono text-xs">
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Zap className="h-4 w-4 text-blue-400" />
              <span>OCR Engine: <strong className="text-blue-400">ONNX-PP-OCRv4 (CPU)</strong></span>
            </div>
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Clock className="h-4 w-4 text-emerald-400" />
              <span>Total Latency: <strong className="text-emerald-400">{result?.total_latency_ms || 0} ms</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Mode Navigation Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveMode('workbench')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeMode === 'workbench'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <ScanLine className="w-4 h-4" />
            <span>Interactive ANPR Workbench</span>
          </button>

          <button
            onClick={() => {
              setActiveMode('benchmark');
              if (!benchmarkResult) handleRunBenchmark();
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeMode === 'benchmark'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Automated Test Benchmark</span>
          </button>
        </div>

        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
          ANPR / OCR PROTOTYPE
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Mode 1: Interactive ANPR Workbench */}
      {activeMode === 'workbench' && (
        <div className="space-y-6">
          {/* Scenario Selector & Custom Upload Toolbar */}
          <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col gap-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="text-xs text-slate-400 font-mono flex items-center gap-2">
                <ImageIcon className="w-4 h-4 text-blue-400" />
                <span>Select Development Test Scenario:</span>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {/* Database persistence toggle */}
                <label className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 rounded-lg border border-slate-800 text-xs text-slate-300 cursor-pointer hover:border-slate-700">
                  <input
                    type="checkbox"
                    checked={persistToDb}
                    onChange={(e) => setPersistToDb(e.target.checked)}
                    className="rounded bg-slate-950 text-blue-600 focus:ring-0"
                  />
                  <Database className="w-3.5 h-3.5 text-blue-400" />
                  <span>Persist to DB</span>
                </label>

                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isProcessing}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-lg text-xs font-semibold disabled:opacity-50 transition-colors"
                >
                  <Upload className="w-3.5 h-3.5 text-blue-400" />
                  <span>Upload Local Frame</span>
                </button>
              </div>
            </div>

            {/* Scenario Buttons */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2 pt-1">
              {samples.map((s) => (
                <button
                  key={s.sample_id}
                  onClick={() => runPipelineOnSample(s.sample_id, persistToDb)}
                  disabled={isProcessing}
                  className={`p-2.5 rounded-lg text-left border transition-all text-xs flex flex-col gap-1 ${
                    selectedSampleId === s.sample_id
                      ? 'bg-blue-600/20 border-blue-500 text-white shadow-md'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-850 hover:text-slate-200'
                  }`}
                >
                  <span className="font-semibold text-slate-200 truncate">{s.title}</span>
                  <span className="text-[10px] text-slate-500 truncate">{s.category}</span>
                </button>
              ))}
            </div>
          </div>

          {/* End-to-End Pipeline Stage Flow Banner */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
            <div className="flex items-center gap-1.5 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>1. Image Input</span>
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
            <div className="flex items-center gap-1.5 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>2. CLAHE Preprocess</span>
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
            <div className={`flex items-center gap-1.5 ${result?.plate_detected ? 'text-emerald-400' : 'text-amber-400'}`}>
              {result?.plate_detected ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
              <span>3. Plate Region Detect</span>
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
            <div className={`flex items-center gap-1.5 ${ocrResult?.normalized_plate ? 'text-emerald-400' : 'text-rose-400'}`}>
              {ocrResult?.normalized_plate ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
              <span>4. Character OCR</span>
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
            <div className={`flex items-center gap-1.5 ${ocrResult?.format_valid ? 'text-emerald-400' : 'text-amber-400'}`}>
              {ocrResult?.format_valid ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
              <span>5. RTO Validation</span>
            </div>
          </div>

          {/* Visual Workspace & ANPR Inspection Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Visual Frame and Crops (7 cols) */}
            <div className="lg:col-span-7 bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <Eye className="w-4 h-4 text-blue-400" />
                  <h2 className="text-sm font-bold text-white">Visual Camera Frame &amp; Localization</h2>
                </div>

                <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs font-medium">
                  <button
                    onClick={() => setActiveVisualTab('annotated')}
                    className={`px-3 py-1 rounded-md transition-all ${
                      activeVisualTab === 'annotated'
                        ? 'bg-blue-600 text-white shadow'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Annotated Frame
                  </button>
                  <button
                    onClick={() => setActiveVisualTab('crop')}
                    className={`px-3 py-1 rounded-md transition-all ${
                      activeVisualTab === 'crop'
                        ? 'bg-blue-600 text-white shadow'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Plate Crop
                  </button>
                </div>
              </div>

              {/* Display Canvas */}
              <div className="relative rounded-lg overflow-hidden bg-slate-950 border border-slate-800 min-h-[340px] flex items-center justify-center">
                {isProcessing ? (
                  <div className="flex flex-col items-center gap-2 text-slate-400 py-16 font-mono text-xs">
                    <RefreshCw className="w-6 h-6 animate-spin text-blue-400" />
                    <span>Running Edge Preprocessing &amp; OCR Engine...</span>
                  </div>
                ) : activeVisualTab === 'annotated' && result?.annotated_frame_b64 ? (
                  <img
                    src={`data:image/jpeg;base64,${result.annotated_frame_b64}`}
                    alt="Annotated ANPR Frame"
                    className="w-full h-auto object-contain max-h-[460px]"
                  />
                ) : activeVisualTab === 'crop' && primaryPlate?.cropped_plate_b64 ? (
                  <div className="p-6 flex flex-col items-center gap-3">
                    <div className="p-2 bg-slate-900 border border-slate-700 rounded-lg shadow-inner">
                      <img
                        src={`data:image/jpeg;base64,${primaryPlate.cropped_plate_b64}`}
                        alt="Plate Crop"
                        className="max-h-[140px] w-auto rounded border border-slate-700"
                      />
                    </div>
                    <div className="font-mono text-xs text-slate-400 flex items-center gap-4">
                      <span>Aspect Ratio: <strong className="text-amber-400">{primaryPlate.aspect_ratio}</strong></span>
                      <span>BBox: <strong className="text-blue-400">[{primaryPlate.bbox.join(', ')}]</strong></span>
                    </div>
                  </div>
                ) : (
                  <div className="text-slate-500 text-xs py-16 text-center font-mono">
                    No plate candidate located in current frame.
                  </div>
                )}
              </div>

              {/* Latency Telemetry */}
              <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase">Edge Preprocessing</span>
                  <span className="font-bold text-slate-300">{result?.edge_vision_latency_ms || 0} ms</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase">OCR Recognition</span>
                  <span className="font-bold text-blue-400">{result?.ocr_latency_ms || 0} ms</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase">Total Latency</span>
                  <span className="font-bold text-emerald-400">{result?.total_latency_ms || 0} ms</span>
                </div>
              </div>
            </div>

            {/* Right Column: ANPR Reading & Validation Intelligence (5 cols) */}
            <div className="lg:col-span-5 flex flex-col gap-4">
              {/* License Plate Recognition Badge Card */}
              <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-3.5">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <ScanLine className="w-4 h-4 text-amber-400" />
                    <span>Recognized Plate Identity</span>
                  </h3>
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                    ocrResult?.format_valid
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  }`}>
                    {ocrResult?.format_valid ? 'RTO VALID' : 'NON-STANDARD / UNREAD'}
                  </span>
                </div>

                {/* Stylized High-Security Plate Badge */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col items-center justify-center gap-2">
                  {ocrResult?.normalized_plate ? (
                    <div className="inline-flex items-center gap-3 px-4 py-2 rounded-lg bg-slate-900 border-2 border-slate-700 font-mono font-extrabold text-xl text-amber-300 shadow-md">
                      <div className="flex flex-col items-center justify-center px-1.5 py-0.5 rounded bg-blue-600 text-white text-[9px] leading-tight">
                        <span>IND</span>
                      </div>
                      <span className="tracking-widest">{ocrResult.normalized_plate}</span>
                    </div>
                  ) : (
                    <div className="px-4 py-2 rounded-lg bg-rose-950/40 border border-rose-800 text-rose-300 font-mono font-bold text-sm">
                      OCR FAILED / LOW CONFIDENCE
                    </div>
                  )}

                  <div className="text-[11px] font-mono text-slate-400 flex items-center gap-3">
                    <span>Raw OCR: <strong className="text-slate-300">{ocrResult?.raw_text || '—'}</strong></span>
                    <span>Readability: <strong className="text-cyan-400">{ocrResult?.readability || 'UNREADABLE'}</strong></span>
                  </div>
                </div>

                {/* Structured Decomposition (State, District, Series, Number) */}
                <div className="grid grid-cols-4 gap-2 text-center text-xs font-mono">
                  <div className="p-2 bg-slate-900/80 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">State</span>
                    <span className="font-bold text-blue-400">{ocrResult?.components?.state_code || '—'}</span>
                  </div>
                  <div className="p-2 bg-slate-900/80 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">District</span>
                    <span className="font-bold text-slate-200">{ocrResult?.components?.district_code || '—'}</span>
                  </div>
                  <div className="p-2 bg-slate-900/80 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">Series</span>
                    <span className="font-bold text-amber-400">{ocrResult?.components?.series || '—'}</span>
                  </div>
                  <div className="p-2 bg-slate-900/80 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">Number</span>
                    <span className="font-bold text-emerald-400">{ocrResult?.components?.registration_number || '—'}</span>
                  </div>
                </div>

                {/* Confidence Metrics */}
                <div className="space-y-2 pt-1 font-sans text-xs">
                  <div>
                    <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                      <span>OCR Engine Confidence</span>
                      <span className="font-bold text-blue-400">{Math.round((ocrResult?.ocr_confidence || 0) * 100)}%</span>
                    </div>
                    <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${(ocrResult?.ocr_confidence || 0) * 100}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                      <span>Composite Final Confidence</span>
                      <span className="font-bold text-emerald-400">{Math.round((ocrResult?.final_confidence || 0) * 100)}%</span>
                    </div>
                    <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{ width: `${(ocrResult?.final_confidence || 0) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Quality & Anomaly Summary Card */}
              <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Physical Integrity Assessment</span>
                </h3>

                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                  <div className="p-2 rounded bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                    <span className="text-slate-400">Plate Condition:</span>
                    <strong className="text-slate-200">{primaryPlate?.condition || 'MISSING'}</strong>
                  </div>
                  <div className="p-2 rounded bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                    <span className="text-slate-400">Broken Flag:</span>
                    <strong className={primaryPlate?.anomaly_flags.broken_plate ? 'text-rose-400' : 'text-emerald-400'}>
                      {primaryPlate?.anomaly_flags.broken_plate ? 'YES' : 'NO'}
                    </strong>
                  </div>
                  <div className="p-2 rounded bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                    <span className="text-slate-400">Damaged Flag:</span>
                    <strong className={primaryPlate?.anomaly_flags.damaged_plate ? 'text-rose-400' : 'text-emerald-400'}>
                      {primaryPlate?.anomaly_flags.damaged_plate ? 'YES' : 'NO'}
                    </strong>
                  </div>
                  <div className="p-2 rounded bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                    <span className="text-slate-400">Mud / Obscured:</span>
                    <strong className={primaryPlate?.anomaly_flags.obscured_plate ? 'text-amber-400' : 'text-emerald-400'}>
                      {primaryPlate?.anomaly_flags.obscured_plate ? 'YES' : 'NO'}
                    </strong>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mode 2: Automated Test Benchmark */}
      {activeMode === 'benchmark' && (
        <div className="space-y-6">
          <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-400" />
                  <span>Automated ANPR Test Suite Benchmark</span>
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Reproducible evaluation over controlled test scenarios (Daylight HSRP, Headlight Glare, Rain Blur, Damaged, Mud Occlusion).
                </p>
              </div>

              <button
                onClick={handleRunBenchmark}
                disabled={isRunningBenchmark}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-blue-600/20 disabled:opacity-50 transition-all"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isRunningBenchmark ? 'animate-spin' : ''}`} />
                <span>{isRunningBenchmark ? 'Evaluating Scenarios...' : 'Rerun Benchmark'}</span>
              </button>
            </div>

            {/* Benchmark Summary Metrics Grid */}
            {benchmarkResult && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
                <div className="p-3.5 bg-slate-900 rounded-xl border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-bold">Exact Match Rate</span>
                  <span className="text-xl font-extrabold text-blue-400">
                    {Math.round(benchmarkResult.exact_match_rate * 100)}%
                  </span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">
                    ({benchmarkResult.exact_matches}/{benchmarkResult.total_samples} samples)
                  </span>
                </div>

                <div className="p-3.5 bg-slate-900 rounded-xl border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-bold">Normalized Match Rate</span>
                  <span className="text-xl font-extrabold text-emerald-400">
                    {Math.round(benchmarkResult.normalized_match_rate * 100)}%
                  </span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">
                    ({benchmarkResult.normalized_matches}/{benchmarkResult.total_samples} samples)
                  </span>
                </div>

                <div className="p-3.5 bg-slate-900 rounded-xl border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-bold">RTO Validity Rate</span>
                  <span className="text-xl font-extrabold text-cyan-400">
                    {Math.round(benchmarkResult.format_valid_rate * 100)}%
                  </span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">
                    ({benchmarkResult.format_valid_count}/{benchmarkResult.total_samples} samples)
                  </span>
                </div>

                <div className="p-3.5 bg-slate-900 rounded-xl border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-bold">Average Latency</span>
                  <span className="text-xl font-extrabold text-amber-400">
                    {benchmarkResult.average_latency_ms} ms
                  </span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">CPU execution time</span>
                </div>
              </div>
            )}

            {/* Per-Scenario Results Table */}
            <div className="overflow-x-auto rounded-lg border border-slate-800">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900 text-[11px] uppercase tracking-wider text-slate-400 font-mono border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-3.5">Test Scenario</th>
                    <th className="py-3 px-3.5">Category</th>
                    <th className="py-3 px-3.5">Expected Plate</th>
                    <th className="py-3 px-3.5">Raw OCR Extracted</th>
                    <th className="py-3 px-3.5">Normalized Result</th>
                    <th className="py-3 px-3.5">Format Status</th>
                    <th className="py-3 px-3.5">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {benchmarkResult?.results_breakdown.map((row) => (
                    <tr key={row.sample_id} className="hover:bg-slate-900/50">
                      <td className="py-2.5 px-3.5 font-semibold text-slate-200">
                        {row.title}
                      </td>
                      <td className="py-2.5 px-3.5 text-slate-400 font-mono text-[11px]">
                        {row.category}
                      </td>
                      <td className="py-2.5 px-3.5 font-mono text-amber-300 font-bold">
                        {row.expected_plate || '— (Rejection Expected)'}
                      </td>
                      <td className="py-2.5 px-3.5 font-mono text-slate-300">
                        {row.raw_extracted || '—'}
                      </td>
                      <td className="py-2.5 px-3.5 font-mono">
                        {row.normalized_extracted ? (
                          <span className="text-emerald-400 font-bold">{row.normalized_extracted}</span>
                        ) : (
                          <span className="text-slate-500 italic">Unreadable</span>
                        )}
                      </td>
                      <td className="py-2.5 px-3.5">
                        {row.format_valid ? (
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-semibold">
                            VALID
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded bg-slate-900 text-slate-500 border border-slate-800 text-[10px] font-mono">
                            N/A
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 px-3.5 font-mono text-slate-400">
                        {row.latency_ms} ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Disclaimer */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px] text-slate-500 font-mono flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-400 shrink-0" />
              <span>{benchmarkResult?.disclaimer || 'Prototype benchmark on controlled test scenarios — not representative of real-world multi-lane field accuracy.'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
