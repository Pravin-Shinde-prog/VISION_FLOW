import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Cpu,
  Upload,
  RefreshCw,
  Sparkles,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  ShieldAlert,
  Eye,
  Clock,
  ScanLine,
  Image as ImageIcon,
  Zap
} from 'lucide-react';
import {
  fetchSampleFrames,
  processSampleFrame,
  processUploadedFrame,
} from '../services/api';
import {
  SampleFrameInfo,
  EdgeVisionProcessResponse,
  PreprocessingOptions,
} from '../types/edgeVision';

export const EdgeVisionPage: React.FC = () => {
  const [samples, setSamples] = useState<SampleFrameInfo[]>([]);
  const [selectedSampleId, setSelectedSampleId] = useState<string>('clean_hsrp_day');
  const [activeTab, setActiveTab] = useState<'annotated' | 'edges' | 'crop'>('annotated');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [result, setResult] = useState<EdgeVisionProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Configuration options
  const [showConfig, setShowConfig] = useState<boolean>(false);
  const [enableClahe, setEnableClahe] = useState<boolean>(true);
  const [claheClipLimit, setClaheClipLimit] = useState<number>(2.5);
  const [enableDenoising, setEnableDenoising] = useState<boolean>(true);
  const [enableSharpening, setEnableSharpening] = useState<boolean>(true);
  const [sharpenStrength, setSharpenStrength] = useState<number>(0.5);
  const [enableGlareReduction, setEnableGlareReduction] = useState<boolean>(true);

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

  const runPipelineOnSample = useCallback(async (sampleId: string) => {
    setIsProcessing(true);
    setError(null);
    try {
      const options: PreprocessingOptions = {
        enable_clahe: enableClahe,
        clahe_clip_limit: claheClipLimit,
        enable_denoising: enableDenoising,
        enable_sharpening: enableSharpening,
        sharpen_strength: sharpenStrength,
        enable_glare_reduction: enableGlareReduction,
      };
      const res = await processSampleFrame(sampleId, options);
      setResult(res);
      setSelectedSampleId(sampleId);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Processing failed';
      setError(msg);
    } finally {
      setIsProcessing(false);
    }
  }, [enableClahe, claheClipLimit, enableDenoising, enableSharpening, sharpenStrength, enableGlareReduction]);

  useEffect(() => {
    loadSamples();
    runPipelineOnSample('clean_hsrp_day');
  }, [loadSamples, runPipelineOnSample]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    setError(null);
    try {
      const options: PreprocessingOptions = {
        enable_clahe: enableClahe,
        clahe_clip_limit: claheClipLimit,
        enable_denoising: enableDenoising,
        enable_sharpening: enableSharpening,
        sharpen_strength: sharpenStrength,
        enable_glare_reduction: enableGlareReduction,
      };
      const res = await processUploadedFrame(file, options);
      setResult(res);
      setSelectedSampleId('custom_upload');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload processing failed';
      setError(msg);
    } finally {
      setIsProcessing(false);
    }
  };

  const getConditionColor = (condition: string) => {
    switch (condition) {
      case 'NORMAL':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'PARTIAL':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'DAMAGED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'OCCLUDED':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'UNREADABLE':
      case 'MISSING':
      default:
        return 'bg-red-500/20 text-red-400 border-red-500/40';
    }
  };

  return (
    <div className="space-y-6 text-slate-100">
      {/* Top Banner */}
      <div className="rounded-xl border border-slate-800 bg-gradient-to-r from-[#111827] via-[#131C31] to-[#111827] p-6 lg:p-8 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-blue-500 animate-ping" />
              <span className="text-xs font-mono font-semibold uppercase tracking-widest text-blue-400">
                Stage 8 • Edge Vision &amp; Plate Preprocessing
              </span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold tracking-tight text-white font-mono flex items-center gap-3">
              <Cpu className="w-8 h-8 text-blue-400" />
              <span>Smart Edge Vision Workbench</span>
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              Edge-level image enhancement pipeline for high-density traffic surveillance. Evaluates luminance balance,
              suppresses headlight glare, localizes candidate license plate bounding boxes, and detects physical compliance anomalies.
            </p>
          </div>

          <div className="flex flex-wrap lg:flex-col gap-2.5 shrink-0 font-mono text-xs">
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Zap className="h-4 w-4 text-blue-400" />
              <span>Pipeline: <strong className="text-blue-400">edge_v1.0</strong></span>
            </div>
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Clock className="h-4 w-4 text-emerald-400" />
              <span>Latency: <strong className="text-emerald-400">{result?.processing_latency_ms || 0} ms</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* Scenario Selector & Custom Upload Toolbar */}
      <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col gap-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="text-xs text-slate-400 font-mono flex items-center gap-2">
            <ImageIcon className="w-4 h-4 text-blue-400" />
            <span>Select Test Scenario Frame:</span>
          </div>

          <div className="flex items-center gap-2">
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
              <span>Upload Custom Image</span>
            </button>

            <button
              onClick={() => setShowConfig(!showConfig)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all ${
                showConfig
                  ? 'bg-blue-600/20 text-blue-400 border-blue-500/40'
                  : 'bg-slate-900 text-slate-400 border-slate-800'
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Pipeline Settings</span>
            </button>
          </div>
        </div>

        {/* Preset Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2 pt-1">
          {samples.map((s) => (
            <button
              key={s.sample_id}
              onClick={() => runPipelineOnSample(s.sample_id)}
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

        {/* Expandable Configuration Drawer */}
        {showConfig && (
          <div className="mt-3 p-4 bg-slate-950/80 border border-slate-800 rounded-lg grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs font-sans">
            {/* CLAHE */}
            <div className="space-y-2">
              <label className="flex items-center justify-between text-slate-300">
                <span>CLAHE Equalization</span>
                <input
                  type="checkbox"
                  checked={enableClahe}
                  onChange={(e) => setEnableClahe(e.target.checked)}
                  className="rounded bg-slate-900 text-blue-600 focus:ring-0"
                />
              </label>
              <div className="space-y-1">
                <div className="flex justify-between text-[11px] text-slate-400 font-mono">
                  <span>Clip Limit:</span>
                  <span className="text-blue-400">{claheClipLimit.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="1.0"
                  max="6.0"
                  step="0.5"
                  value={claheClipLimit}
                  onChange={(e) => setClaheClipLimit(parseFloat(e.target.value))}
                  disabled={!enableClahe}
                  className="w-full h-1 bg-slate-800 rounded accent-blue-500"
                />
              </div>
            </div>

            {/* Denoising */}
            <div className="space-y-2">
              <label className="flex items-center justify-between text-slate-300">
                <span>Bilateral Denoising</span>
                <input
                  type="checkbox"
                  checked={enableDenoising}
                  onChange={(e) => setEnableDenoising(e.target.checked)}
                  className="rounded bg-slate-900 text-blue-600 focus:ring-0"
                />
              </label>
              <p className="text-[10px] text-slate-500">Smooths high-frequency sensor noise while keeping character stroke edges intact.</p>
            </div>

            {/* Sharpening */}
            <div className="space-y-2">
              <label className="flex items-center justify-between text-slate-300">
                <span>Unsharp Sharpening</span>
                <input
                  type="checkbox"
                  checked={enableSharpening}
                  onChange={(e) => setEnableSharpening(e.target.checked)}
                  className="rounded bg-slate-900 text-blue-600 focus:ring-0"
                />
              </label>
              <div className="space-y-1">
                <div className="flex justify-between text-[11px] text-slate-400 font-mono">
                  <span>Strength:</span>
                  <span className="text-cyan-400">{sharpenStrength.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="1.5"
                  step="0.1"
                  value={sharpenStrength}
                  onChange={(e) => setSharpenStrength(parseFloat(e.target.value))}
                  disabled={!enableSharpening}
                  className="w-full h-1 bg-slate-800 rounded accent-cyan-500"
                />
              </div>
            </div>

            {/* Glare Suppression */}
            <div className="space-y-2">
              <label className="flex items-center justify-between text-slate-300">
                <span>Glare Suppression</span>
                <input
                  type="checkbox"
                  checked={enableGlareReduction}
                  onChange={(e) => setEnableGlareReduction(e.target.checked)}
                  className="rounded bg-slate-900 text-blue-600 focus:ring-0"
                />
              </label>
              <p className="text-[10px] text-slate-500">Luminance gamma compensation to tame intense specular reflections.</p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Inspection Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Visual Previews (7 cols) */}
        <div className="lg:col-span-7 bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Eye className="w-4 h-4 text-blue-400" />
              <h2 className="text-sm font-bold text-white">Visual Inspection &amp; Candidate Overlays</h2>
            </div>

            {/* Visual View Tabs */}
            <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs font-medium">
              <button
                onClick={() => setActiveTab('annotated')}
                className={`px-3 py-1 rounded-md transition-all ${
                  activeTab === 'annotated'
                    ? 'bg-blue-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Annotated Frame
              </button>
              <button
                onClick={() => setActiveTab('edges')}
                className={`px-3 py-1 rounded-md transition-all ${
                  activeTab === 'edges'
                    ? 'bg-blue-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Vertical Edge Map
              </button>
              <button
                onClick={() => setActiveTab('crop')}
                className={`px-3 py-1 rounded-md transition-all ${
                  activeTab === 'crop'
                    ? 'bg-blue-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Plate Crop ({result?.candidate_plates_count || 0})
              </button>
            </div>
          </div>

          {/* Image Display Area */}
          <div className="relative rounded-lg overflow-hidden bg-slate-950 border border-slate-800 min-h-[340px] flex items-center justify-center">
            {isProcessing ? (
              <div className="flex flex-col items-center gap-2 text-slate-400 py-16 font-mono text-xs">
                <RefreshCw className="w-6 h-6 animate-spin text-blue-400" />
                <span>Executing Edge Preprocessing Pipeline...</span>
              </div>
            ) : activeTab === 'annotated' && result?.enhanced_frame_b64 ? (
              <img
                src={`data:image/jpeg;base64,${result.enhanced_frame_b64}`}
                alt="Enhanced Frame"
                className="w-full h-auto object-contain max-h-[460px]"
              />
            ) : activeTab === 'edges' && result?.edge_representation_b64 ? (
              <img
                src={`data:image/jpeg;base64,${result.edge_representation_b64}`}
                alt="Vertical Gradient Edge Map"
                className="w-full h-auto object-contain max-h-[460px] filter invert"
              />
            ) : activeTab === 'crop' && result?.primary_plate?.cropped_plate_b64 ? (
              <div className="p-6 flex flex-col items-center gap-3">
                <div className="p-2 bg-slate-900 border border-slate-700 rounded-lg shadow-inner">
                  <img
                    src={`data:image/jpeg;base64,${result.primary_plate.cropped_plate_b64}`}
                    alt="Plate Candidate Crop"
                    className="max-h-[140px] w-auto rounded border border-slate-700"
                  />
                </div>
                <div className="font-mono text-xs text-slate-400 flex items-center gap-4">
                  <span>Aspect Ratio: <strong className="text-amber-400">{result.primary_plate.aspect_ratio}</strong></span>
                  <span>BBox: <strong className="text-blue-400">[{result.primary_plate.bbox.join(', ')}]</strong></span>
                </div>
              </div>
            ) : (
              <div className="text-slate-500 text-xs py-16 text-center font-mono">
                No plate candidate localized in current frame.
              </div>
            )}
          </div>

          {/* Bottom frame specs */}
          <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 font-mono pt-1">
            <span>Dimensions: {result?.frame_width || 0}x{result?.frame_height || 0} px</span>
            <span>Candidates Located: {result?.candidate_plates_count || 0}</span>
            <span>Camera Reference: {result?.camera_id || 'CAM_PUN_001'}</span>
          </div>
        </div>

        {/* Right Column: Telemetry, Quality & Compliance (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          {/* Overall Quality Card */}
          <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-400" />
                <span>Image Quality Metrics</span>
              </h3>
              <span className="font-mono text-sm font-bold text-blue-400">
                {Math.round((result?.image_quality?.overall_quality_score || 0) * 100)}%
              </span>
            </div>

            {/* Quality metric progress bars */}
            <div className="space-y-2 text-xs font-sans">
              <div>
                <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                  <span>Luminance Brightness</span>
                  <span>{Math.round((result?.image_quality?.brightness_score || 0) * 100)}%</span>
                </div>
                <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${(result?.image_quality?.brightness_score || 0) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                  <span>Contrast Dynamic Range</span>
                  <span>{Math.round((result?.image_quality?.contrast_score || 0) * 100)}%</span>
                </div>
                <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-500 rounded-full"
                    style={{ width: `${(result?.image_quality?.contrast_score || 0) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                  <span>Laplacian Sharpness / Focus</span>
                  <span>{Math.round((result?.image_quality?.sharpness_score || 0) * 100)}%</span>
                </div>
                <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full"
                    style={{ width: `${(result?.image_quality?.sharpness_score || 0) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                  <span>Specular Glare Index</span>
                  <span className={(result?.image_quality?.glare_score || 0) > 0.4 ? 'text-amber-400 font-bold' : ''}>
                    {Math.round((result?.image_quality?.glare_score || 0) * 100)}%
                  </span>
                </div>
                <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-500 rounded-full"
                    style={{ width: `${(result?.image_quality?.glare_score || 0) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Plate Condition & Physical Integrity */}
          <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <ScanLine className="w-4 h-4 text-cyan-400" />
                <span>Plate State &amp; Readability</span>
              </h3>
              <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getConditionColor(result?.summary_condition || 'NORMAL')}`}>
                {result?.summary_condition || 'NORMAL'}
              </span>
            </div>

            {/* Readability & Quality score */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 block">Readability</span>
                <span className="font-bold text-slate-200">{result?.primary_plate?.readability || 'UNVERIFIED'}</span>
              </div>
              <div className="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 block">Candidate Confidence</span>
                <span className="font-bold text-blue-400">
                  {Math.round((result?.primary_plate?.confidence || 0) * 100)}%
                </span>
              </div>
            </div>

            {/* Compliance Anomaly Flags */}
            <div className="space-y-1.5 pt-1">
              <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block mb-1">
                Plate Anomaly &amp; Compliance Flags:
              </span>

              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                <div className={`p-2 rounded border flex items-center gap-2 ${
                  result?.primary_plate?.anomaly_flags.broken_plate
                    ? 'bg-rose-950/40 border-rose-800 text-rose-300'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400'
                }`}>
                  {result?.primary_plate?.anomaly_flags.broken_plate ? (
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  )}
                  <span>Broken Plate</span>
                </div>

                <div className={`p-2 rounded border flex items-center gap-2 ${
                  result?.primary_plate?.anomaly_flags.damaged_plate
                    ? 'bg-rose-950/40 border-rose-800 text-rose-300'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400'
                }`}>
                  {result?.primary_plate?.anomaly_flags.damaged_plate ? (
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  )}
                  <span>Damaged Plate</span>
                </div>

                <div className={`p-2 rounded border flex items-center gap-2 ${
                  result?.primary_plate?.anomaly_flags.modified_plate
                    ? 'bg-amber-950/40 border-amber-800 text-amber-300'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400'
                }`}>
                  {result?.primary_plate?.anomaly_flags.modified_plate ? (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  )}
                  <span>Modified HSRP</span>
                </div>

                <div className={`p-2 rounded border flex items-center gap-2 ${
                  result?.primary_plate?.anomaly_flags.obscured_plate
                    ? 'bg-purple-950/40 border-purple-800 text-purple-300'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400'
                }`}>
                  {result?.primary_plate?.anomaly_flags.obscured_plate ? (
                    <AlertTriangle className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  )}
                  <span>Mud / Obscured</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
