import React, { useState, useEffect } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { api } from '../../services/api';
import { 
  Camera, 
  Smartphone, 
  CheckCircle2, 
  AlertTriangle, 
  Play, 
  RefreshCw, 
  FlaskConical, 
  Eye, 
  ExternalLink,
  ShieldCheck,
  Cpu,
  Layers,
  RotateCcw,
  History,
  BookmarkPlus
} from 'lucide-react';

export function QAPanel() {
  const { activeProject, previewUrl } = useAppStore();
  const [qaUrl, setQaUrl] = useState(previewUrl || 'http://localhost:5174');
  const [isInspecting, setIsInspecting] = useState(false);
  const [qaReport, setQaReport] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);

  // Checkpoint & Rollback state (Sections 50 & 51)
  const [checkpoints, setCheckpoints] = useState([]);
  const [newCpDesc, setNewCpDesc] = useState('');
  const [isCreatingCp, setIsCreatingCp] = useState(false);
  const [rollingBackId, setRollingBackId] = useState(null);

  // Android state
  const [devices, setDevices] = useState([]);
  const [adbLoading, setAdbLoading] = useState(false);
  const [adbError, setAdbError] = useState(null);
  const [capturingDevice, setCapturingDevice] = useState(null);

  // Test scaffolding state
  const [scaffolding, setScaffolding] = useState(false);
  const [scaffoldMsg, setScaffoldMsg] = useState(null);

  useEffect(() => {
    if (activeProject) {
      loadSnapshots();
      loadCheckpoints();
    }
    loadDevices();
  }, [activeProject]);

  const loadCheckpoints = async () => {
    if (!activeProject) return;
    try {
      const res = await api.getCheckpoints(activeProject.id);
      setCheckpoints(res.checkpoints || []);
    } catch (e) {
      console.warn('Failed to load checkpoints:', e);
    }
  };

  const loadSnapshots = async () => {
    if (!activeProject) return;
    try {
      const res = await api.getSnapshots(activeProject.id);
      setSnapshots(res.snapshots || []);
    } catch (e) {
      console.warn('Failed to load snapshots:', e);
    }
  };

  const loadDevices = async () => {
    setAdbLoading(true);
    setAdbError(null);
    try {
      const res = await api.getAndroidDevices();
      if (res.available) {
        setDevices(res.devices || []);
      } else {
        setDevices([]);
        setAdbError(res.error || 'ADB not found on PATH');
      }
    } catch (err) {
      setAdbError(err.message);
    } finally {
      setAdbLoading(false);
    }
  };

  const handleRunQA = async () => {
    if (!activeProject) return;
    setIsInspecting(true);
    setQaReport(null);
    try {
      const res = await api.runVisualQA(activeProject.id, qaUrl);
      if (res.success && res.report) {
        setQaReport(res.report);
      }
      await loadSnapshots();
    } catch (err) {
      setQaReport({ passed: false, error: err.message });
    } finally {
      setIsInspecting(false);
    }
  };

  const handleCaptureAndroid = async (serial) => {
    if (!activeProject) return;
    setCapturingDevice(serial);
    try {
      await api.takeAndroidScreenshot(activeProject.id, serial);
      await loadSnapshots();
    } catch (err) {
      alert(`Android screenshot failed: ${err.message}`);
    } finally {
      setCapturingDevice(null);
    }
  };

  const handleScaffoldTests = async () => {
    if (!activeProject) return;
    setScaffolding(true);
    setScaffoldMsg(null);
    try {
      const res = await api.scaffoldTests(activeProject.id);
      setScaffoldMsg(res.message);
      // Run the test
      await api.runCommand(activeProject.id, res.testCommand || 'npm test', 'test');
    } catch (err) {
      setScaffoldMsg(`Scaffold failed: ${err.message}`);
    } finally {
      setScaffolding(false);
    }
  };

  const handleCreateCheckpoint = async (e) => {
    e?.preventDefault();
    if (!activeProject || !newCpDesc.trim()) return;
    setIsCreatingCp(true);
    try {
      await api.createCheckpoint(activeProject.id, newCpDesc.trim(), 'MANUAL');
      setNewCpDesc('');
      await loadCheckpoints();
    } catch (err) {
      alert(`Failed to create checkpoint: ${err.message}`);
    } finally {
      setIsCreatingCp(false);
    }
  };

  const handleRollback = async (checkpointId) => {
    if (!activeProject) return;
    if (!confirm(`Are you sure you want to rollback workspace files to checkpoint ${checkpointId}? Any unsaved changes will be reverted.`)) return;
    setRollingBackId(checkpointId);
    try {
      const res = await api.rollbackCheckpoint(activeProject.id, checkpointId);
      if (res.success) {
        alert(`Successfully restored ${res.restored_count} files from checkpoint ${checkpointId}!`);
        useAppStore.getState().refreshFileTree?.();
      } else {
        alert(`Rollback failed: ${res.error || res.raw}`);
      }
    } catch (err) {
      alert(`Rollback failed: ${err.message}`);
    } finally {
      setRollingBackId(null);
    }
  };

  return (
    <div className="flex flex-col h-full bg-ide-sidebar overflow-y-auto p-3 gap-4 text-xs font-sans select-none">
      {/* Section 1: Automated Visual QA */}
      <div className="flex flex-col gap-2 bg-ide-panel/70 border border-ide-border rounded-lg p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 font-semibold text-white">
            <Camera className="w-3.5 h-3.5 text-indigo-400" />
            <span>Visual QA Inspector</span>
          </div>
          <button
            onClick={handleRunQA}
            disabled={isInspecting || !activeProject}
            className="flex items-center gap-1 px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded text-[11px] font-medium transition-colors shadow-sm"
          >
            {isInspecting ? (
              <RefreshCw className="w-3 h-3 animate-spin" />
            ) : (
              <Play className="w-3 h-3 fill-current" />
            )}
            <span>{isInspecting ? 'Inspecting...' : 'Inspect Live UI'}</span>
          </button>
        </div>

        <div className="flex items-center gap-1.5 mt-1">
          <input
            type="text"
            value={qaUrl}
            onChange={(e) => setQaUrl(e.target.value)}
            placeholder="http://localhost:5174"
            className="flex-1 bg-ide-bg border border-ide-border rounded px-2 py-1 text-[11px] text-ide-text focus:outline-none focus:border-indigo-500 font-mono"
          />
        </div>

        {qaReport && (
          <div className={`mt-2 p-2.5 rounded border text-[11px] flex flex-col gap-1.5 ${
            qaReport.passed 
              ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300' 
              : 'bg-rose-950/40 border-rose-800/60 text-rose-300'
          }`}>
            <div className="flex items-center justify-between font-semibold">
              <div className="flex items-center gap-1.5">
                {qaReport.passed ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                )}
                <span>{qaReport.passed ? 'Visual QA Passed' : 'Visual Issues Detected'}</span>
              </div>
              <span className="text-[10px] opacity-80">{qaReport.title || 'Page loaded'}</span>
            </div>

            {qaReport.has_react_error && (
              <div className="text-[10px] text-rose-400 font-medium">
                ⚠️ Unhandled React Error Overlay / Crash detected on page.
              </div>
            )}

            {qaReport.console_errors && qaReport.console_errors.length > 0 && (
              <div className="flex flex-col gap-1 mt-1 text-[10px] bg-black/40 p-1.5 rounded font-mono">
                <span className="font-semibold text-rose-300">Console Errors ({qaReport.console_errors.length}):</span>
                {qaReport.console_errors.slice(0, 3).map((err, i) => (
                  <div key={i} className="text-rose-400 truncate">• {err}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Section 2: Automated Test Scaffolder */}
      <div className="flex flex-col gap-2 bg-ide-panel/70 border border-ide-border rounded-lg p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 font-semibold text-white">
            <FlaskConical className="w-3.5 h-3.5 text-emerald-400" />
            <span>Test Suite Scaffolding</span>
          </div>
          <button
            onClick={handleScaffoldTests}
            disabled={scaffolding || !activeProject}
            className="flex items-center gap-1 px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded text-[11px] font-medium transition-colors shadow-sm"
          >
            {scaffolding ? <RefreshCw className="w-3 h-3 animate-spin" /> : <ShieldCheck className="w-3 h-3" />}
            <span>{scaffolding ? 'Scaffolding...' : 'Scaffold Vitest'}</span>
          </button>
        </div>
        <p className="text-[11px] text-ide-muted leading-relaxed">
          1-click generates Vitest smoke tests, configuration, and wires <code className="text-emerald-400 font-mono">npm test</code> into package.json.
        </p>
        {scaffoldMsg && (
          <div className="p-2 bg-emerald-950/40 border border-emerald-800/60 rounded text-[11px] text-emerald-300 font-medium">
            {scaffoldMsg}
          </div>
        )}
      </div>

      {/* Section 3: Android ADB Devices */}
      <div className="flex flex-col gap-2 bg-ide-panel/70 border border-ide-border rounded-lg p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 font-semibold text-white">
            <Smartphone className="w-3.5 h-3.5 text-amber-400" />
            <span>Android ADB Devices ({devices.length})</span>
          </div>
          <button
            onClick={loadDevices}
            disabled={adbLoading}
            className="p-1 hover:bg-ide-bg rounded text-ide-muted hover:text-white transition-colors"
            title="Refresh ADB Devices"
          >
            <RefreshCw className={`w-3 h-3 ${adbLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {adbError ? (
          <div className="text-[11px] text-amber-400/80 bg-amber-950/30 border border-amber-900/50 p-2 rounded">
            {adbError.includes('not recognized') ? 'ADB not found on PATH. Connect emulator or phone to activate.' : adbError}
          </div>
        ) : devices.length === 0 ? (
          <div className="text-[11px] text-ide-muted italic py-1">
            No active Android devices connected via ADB.
          </div>
        ) : (
          <div className="flex flex-col gap-1.5">
            {devices.map((dev) => (
              <div key={dev.serial} className="flex items-center justify-between p-2 rounded bg-ide-bg border border-ide-border">
                <div className="flex flex-col">
                  <span className="font-mono font-medium text-white text-[11px]">{dev.serial}</span>
                  <span className="text-[10px] text-ide-muted">{dev.state}</span>
                </div>
                <button
                  onClick={() => handleCaptureAndroid(dev.serial)}
                  disabled={capturingDevice === dev.serial || !activeProject}
                  className="flex items-center gap-1 px-2 py-0.5 bg-amber-600/80 hover:bg-amber-600 text-white rounded text-[10px] transition-colors"
                >
                  <Camera className="w-2.5 h-2.5" />
                  <span>{capturingDevice === dev.serial ? 'Capturing...' : 'Capture'}</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Section 4: Visual QA & Snapshot Gallery */}
      <div className="flex flex-col gap-2 bg-ide-panel/70 border border-ide-border rounded-lg p-3 flex-1 min-h-[160px]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 font-semibold text-white">
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>Captured Snapshots ({snapshots.length})</span>
          </div>
          <button
            onClick={loadSnapshots}
            className="p-1 hover:bg-ide-bg rounded text-ide-muted hover:text-white transition-colors"
            title="Refresh Snapshots"
          >
            <RefreshCw className="w-3 h-3" />
          </button>
        </div>

        {snapshots.length === 0 ? (
          <div className="text-[11px] text-ide-muted italic py-4 text-center">
            No snapshots captured yet. Click "Inspect Live UI" or "Capture" to record visual state.
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2 mt-1 overflow-y-auto max-h-56 pr-1">
            {snapshots.map((snap) => (
              <div
                key={snap.filename}
                onClick={() => setSelectedSnapshot(snap)}
                className="group relative rounded border border-ide-border bg-ide-bg overflow-hidden cursor-pointer hover:border-indigo-500 transition-all"
              >
                <img
                  src={snap.url}
                  alt={snap.filename}
                  className="w-full h-20 object-cover object-top group-hover:scale-105 transition-transform duration-200"
                  loading="lazy"
                />
                <div className="p-1 bg-ide-panel/90 flex flex-col truncate">
                  <span className="text-[9px] font-mono text-ide-muted truncate">{snap.filename}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Section 5: Checkpoints & Atomic Rollback (Sections 50 & 51) */}
      <div className="flex flex-col gap-2 bg-ide-panel/70 border border-ide-border rounded-lg p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 font-semibold text-white">
            <History className="w-3.5 h-3.5 text-purple-400" />
            <span>Checkpoints & Rollback ({checkpoints.length})</span>
          </div>
          <button
            onClick={loadCheckpoints}
            className="p-1 hover:bg-ide-bg rounded text-ide-muted hover:text-white transition-colors"
            title="Refresh Checkpoints"
          >
            <RefreshCw className="w-3 h-3" />
          </button>
        </div>

        {/* Create Manual Checkpoint */}
        <form onSubmit={handleCreateCheckpoint} className="flex gap-1.5 mt-1">
          <input
            type="text"
            value={newCpDesc}
            onChange={(e) => setNewCpDesc(e.target.value)}
            placeholder="Checkpoint description..."
            className="flex-1 bg-ide-bg border border-ide-border rounded px-2 py-1 text-[11px] text-white focus:outline-none focus:border-purple-500 font-sans"
          />
          <button
            type="submit"
            disabled={isCreatingCp || !newCpDesc.trim() || !activeProject}
            className="px-2.5 py-1 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded text-[11px] font-medium flex items-center gap-1 transition-colors shadow-sm"
          >
            <BookmarkPlus className="w-3 h-3" />
            <span>{isCreatingCp ? 'Saving...' : 'Save'}</span>
          </button>
        </form>

        {checkpoints.length === 0 ? (
          <div className="text-[11px] text-ide-muted italic py-2 text-center">
            No checkpoints recorded yet. Automatic checkpoints are created during mission turns.
          </div>
        ) : (
          <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto pr-1 mt-1">
            {checkpoints.map((cp) => (
              <div key={cp.id} className="p-2 rounded bg-ide-bg border border-ide-border flex items-center justify-between gap-2 text-xs">
                <div className="flex flex-col truncate">
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-white truncate text-[11px]">{cp.description}</span>
                    <span className="px-1 py-0.2 rounded text-[9px] font-mono bg-purple-950 text-purple-300 border border-purple-800">
                      {cp.stage || 'CP'}
                    </span>
                  </div>
                  <span className="text-[10px] text-ide-muted font-mono truncate">
                    {cp.id} • {cp.files_count || 0} files • {cp.timestamp ? new Date(cp.timestamp).toLocaleTimeString() : ''}
                  </span>
                </div>
                <button
                  onClick={() => handleRollback(cp.id)}
                  disabled={rollingBackId === cp.id}
                  className="px-2 py-1 bg-rose-950/60 hover:bg-rose-900 text-rose-300 border border-rose-800 rounded text-[10px] font-medium flex items-center gap-1 shrink-0 transition-colors"
                  title="Rollback all workspace files to this checkpoint"
                >
                  <RotateCcw className={`w-2.5 h-2.5 ${rollingBackId === cp.id ? 'animate-spin' : ''}`} />
                  <span>{rollingBackId === cp.id ? 'Reverting...' : 'Rollback'}</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal for full snapshot preview */}
      {selectedSnapshot && (
        <div 
          className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-6 backdrop-blur-sm"
          onClick={() => setSelectedSnapshot(null)}
        >
          <div 
            className="relative max-w-4xl max-h-[85vh] bg-ide-panel border border-ide-border rounded-xl shadow-2xl overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-ide-border bg-ide-sidebar">
              <span className="font-mono text-xs text-white font-medium">{selectedSnapshot.filename}</span>
              <button
                onClick={() => setSelectedSnapshot(null)}
                className="text-ide-muted hover:text-white text-xs px-2 py-1 rounded hover:bg-ide-bg"
              >
                ✕ Close
              </button>
            </div>
            <div className="overflow-auto p-4 flex items-center justify-center bg-black/50">
              <img
                src={selectedSnapshot.url}
                alt={selectedSnapshot.filename}
                className="max-h-[70vh] rounded shadow border border-ide-border object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
