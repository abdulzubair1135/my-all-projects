import React, { useRef } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { Bot, CheckCircle2, AlertTriangle, XCircle, PauseCircle, Activity, Settings as SettingsIcon, Archive, Zap, Sparkles } from 'lucide-react';
import { ReviewRatingWidget } from '../agent/ReviewRatingWidget';

export function Header() {
  const { agentStatus, health, isConnected, approvalMode, setCommandPaletteOpen, setTemplateGalleryOpen, setProjectWizardOpen, previewUrl, previewPort, activeProject, selectedProvider } = useAppStore();
  const [chromeNotice, setChromeNotice] = React.useState('');
  const [zipNotice, setZipNotice] = React.useState('');
  const zipInputRef = useRef(null);

  const handleExportZip = () => {
    if (!activeProject) {
      alert('Please select or create a project first.');
      return;
    }
    window.location.href = `/api/projects/${activeProject.id}/zip`;
  };

  const handleImportZip = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !activeProject) return;
    setZipNotice('Extracting ZIP...');
    try {
      const formData = new FormData();
      formData.append('zip', file);
      formData.append('projectId', activeProject.id);
      const res = await fetch('/api/uploads/zip', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) {
        setZipNotice(`✅ Extracted ${data.totalExtracted || 0} files! ${data.checkpointCreated ? '(checkpoint created)' : ''}`);
        useAppStore.getState().refreshFileTree?.();
      } else {
        setZipNotice(`❌ ${data.error}`);
      }
    } catch (err) {
      setZipNotice(`❌ ${err.message}`);
    }
    setTimeout(() => setZipNotice(''), 5000);
    e.target.value = '';
  };

  const handleWatchLiveChrome = async () => {
    try {
      setChromeNotice('Opening Chromium Window...');
      const res = await fetch('/api/browser/show', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: selectedProvider || 'gemini_web' })
      });
      const data = await res.json();
      if (data.launched) {
        setChromeNotice('Chromium window opened! Check taskbar.');
      } else {
        setChromeNotice('Chromium brought to front!');
      }
      setTimeout(() => setChromeNotice(''), 4000);
    } catch (err) {
      setChromeNotice('Error launching browser');
      setTimeout(() => setChromeNotice(''), 3000);
    }
  };

  const getStatusBadge = () => {
    switch (agentStatus) {
      case 'RUNNING':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            RUNNING
          </span>
        );
      case 'PAUSED':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
            <PauseCircle className="w-3.5 h-3.5" />
            PAUSED
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            COMPLETED
          </span>
        );
      case 'FAILED':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
            <XCircle className="w-3.5 h-3.5" />
            FAILED
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-800 text-slate-400 border border-slate-700">
            IDLE
          </span>
        );
    }
  };

  return (
    <header className="h-12 bg-ide-sidebar border-b border-ide-border flex items-center justify-between px-4 select-none shrink-0">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 font-bold text-sm tracking-wide text-white">
          <Bot className="w-5 h-5 text-ide-accent" />
          <span>Autonomous Web-Agent IDE</span>
          <span className="text-[10px] font-normal text-ide-muted bg-ide-panel border border-ide-border rounded px-1.5 py-0.5 ml-1">v2.0</span>
        </div>
        <div className="h-4 w-px bg-ide-border" />
        {getStatusBadge()}
        <span className="text-xs px-2 py-0.5 rounded bg-ide-hover border border-ide-border text-ide-muted font-mono">
          MODE: {approvalMode}
        </span>
        <a
          href={previewUrl || "http://localhost:5174"}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-all cursor-pointer"
          title={`Open Live Generated App on Port ${previewPort || 5174}`}
        >
          <span>🌐</span>
          <span>Open Live App ({previewPort || 5174})</span>
        </a>

        <div className="relative flex items-center">
          <button
            onClick={handleWatchLiveChrome}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/30 shadow-sm transition-all cursor-pointer"
            title="Open or bring real-time Chromium Browser window to the front"
          >
            <span>👁️</span>
            <span>Watch Live Chrome</span>
          </button>
          {chromeNotice && (
            <span className="absolute left-0 -bottom-6 z-50 bg-cyan-950 text-cyan-300 border border-cyan-500/50 text-[11px] px-2 py-0.5 rounded shadow-lg whitespace-nowrap animate-fade-in font-mono">
              {chromeNotice}
            </span>
          )}
        </div>

        {/* ── Templates (Section 65) ── */}
        <button
          onClick={() => setTemplateGalleryOpen(true)}
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-indigo-950/80 hover:bg-indigo-900 text-indigo-300 border border-indigo-500/40 shadow-sm transition-all cursor-pointer"
          title="Browse Section 65 Autonomous Project Templates"
        >
          <Zap className="w-3.5 h-3.5 text-indigo-400" />
          <span>Templates</span>
        </button>

        {/* ── Autonomous Spec Wizard ── */}
        <button
          onClick={() => setProjectWizardOpen(true)}
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-gradient-to-r from-amber-500/20 to-orange-500/20 hover:from-amber-500/30 hover:to-orange-500/30 text-amber-300 border border-amber-500/40 shadow-sm transition-all cursor-pointer"
          title="Interactive Spec Clarification Wizard (Game, Web, PPT, Asset & Engine Settings)"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
          <span>New Spec / Wizard</span>
        </button>

        <button
          onClick={handleExportZip}
          disabled={!activeProject}
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-500/30 shadow-sm transition-all cursor-pointer disabled:opacity-50"
          title="Download Complete Project Source Code as a Clean ZIP Archive"
        >
          <span>📦</span>
          <span>Export ZIP</span>
        </button>

        {/* ── Import ZIP ── */}
        <div className="relative flex items-center">
          <button
            onClick={() => zipInputRef.current?.click()}
            disabled={!activeProject}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-slate-800 hover:bg-slate-700 text-green-300 border border-green-500/30 shadow-sm transition-all cursor-pointer disabled:opacity-50"
            title="Import a ZIP file — extract into current project workspace"
          >
            <Archive className="w-3.5 h-3.5" />
            <span>Import ZIP</span>
          </button>
          <input
            ref={zipInputRef}
            type="file"
            accept=".zip"
            className="hidden"
            onChange={handleImportZip}
          />
          {zipNotice && (
            <span className="absolute left-0 -bottom-6 z-50 bg-green-950 text-green-300 border border-green-500/50 text-[11px] px-2 py-0.5 rounded shadow-lg whitespace-nowrap animate-fade-in font-mono max-w-xs">
              {zipNotice}
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Health Indicators */}
        <div className="flex items-center gap-3 text-xs text-ide-muted">
          <div className="flex items-center gap-1.5" title="Backend Controller Status">
            <span className={`w-2 h-2 rounded-full ${health.backend ? 'bg-emerald-400' : 'bg-rose-500'}`} />
            <span>Backend</span>
          </div>
          <div className="flex items-center gap-1.5" title="Browser Automation Status">
            <span className={`w-2 h-2 rounded-full ${health.browser ? 'bg-emerald-400' : 'bg-rose-500'}`} />
            <span>Browser</span>
          </div>
          <div className="flex items-center gap-1.5" title="LLM Provider Status">
            <span className={`w-2 h-2 rounded-full ${health.llm ? 'bg-emerald-400' : 'bg-rose-500'}`} />
            <span>LLM</span>
          </div>
          <div className="flex items-center gap-1.5" title="WebSocket Live Sync">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-rose-500'}`} />
            <span>Sync</span>
          </div>
        </div>

        <div className="h-4 w-px bg-ide-border" />

        {/* Human Feedback & AI Emotion Widget */}
        <ReviewRatingWidget />

        <div className="h-4 w-px bg-ide-border" />

        <button
          onClick={() => setCommandPaletteOpen(true)}
          className="px-2.5 py-1 text-xs rounded bg-ide-panel border border-ide-border text-ide-text hover:bg-ide-hover hover:text-white flex items-center gap-1.5 transition-colors"
        >
          <span>⌘K / Ctrl+P</span>
        </button>
      </div>
    </header>
  );
}
