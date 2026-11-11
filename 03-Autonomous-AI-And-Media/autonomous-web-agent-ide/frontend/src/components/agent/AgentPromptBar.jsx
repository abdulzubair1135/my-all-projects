import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import {
  Play, Pause, Square, Send, Sparkles, Bot, MessageSquarePlus,
  Paperclip, Package, X, Image, Zap, Archive, GitBranch,
  FlaskConical, Hammer, Download, Activity
} from 'lucide-react';
import { api } from '../../services/api';

// Quick action shortcuts
const QUICK_ACTIONS = [
  { label: 'ZIP All', icon: Archive, shortcut: 'zip all', color: 'text-amber-400 border-amber-500/30 hover:bg-amber-500/10' },
  { label: 'Run Tests', icon: FlaskConical, shortcut: 'run tests', color: 'text-green-400 border-green-500/30 hover:bg-green-500/10' },
  { label: 'Build', icon: Hammer, shortcut: 'build app', color: 'text-blue-400 border-blue-500/30 hover:bg-blue-500/10' },
  { label: 'Git Status', icon: GitBranch, shortcut: 'git status', color: 'text-purple-400 border-purple-500/30 hover:bg-purple-500/10' },
  { label: 'Inspect', icon: Zap, shortcut: 'inspect project', color: 'text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/10' },
  { label: 'Doctor', icon: Activity, shortcut: 'doctor', color: 'text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10' },
  { label: 'Install Deps', icon: Package, shortcut: 'install deps', color: 'text-rose-400 border-rose-500/30 hover:bg-rose-500/10' },
];

export function AgentPromptBar() {
  const {
    agentStatus,
    startAgent,
    pauseAgent,
    resumeAgent,
    stopAgent,
    overrideAgent,
    approvalMode,
    selectedProvider,
    setProvider,
    activeProject,
  } = useAppStore();

  const [prompt, setPrompt] = useState('');
  const [attachedImages, setAttachedImages] = useState([]); // [{name, dataUrl, file}]
  const [attachedZip, setAttachedZip] = useState(null);      // {name, file}
  const [uploadingZip, setUploadingZip] = useState(false);
  const [zipResult, setZipResult] = useState(null);
  const [uploadNotice, setUploadNotice] = useState('');

  const inputRef = useRef(null);
  const imageInputRef = useRef(null);
  const zipInputRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // ── Image attachment ────────────────────────────────────────────────────────

  const handleImageSelect = useCallback((e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    files.forEach((file) => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setAttachedImages((prev) => [
          ...prev.filter((img) => img.name !== file.name),
          { name: file.name, dataUrl: ev.target.result, file, size: file.size },
        ]);
      };
      reader.readAsDataURL(file);
    });
    e.target.value = '';
  }, []);

  const removeImage = useCallback((name) => {
    setAttachedImages((prev) => prev.filter((img) => img.name !== name));
  }, []);

  // ── ZIP attachment ──────────────────────────────────────────────────────────

  const handleZipSelect = useCallback((e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAttachedZip({ name: file.name, file, size: file.size });
    setZipResult(null);
    e.target.value = '';
  }, []);

  const importZip = useCallback(async () => {
    if (!attachedZip || !activeProject) {
      setUploadNotice('Select a project first, then import ZIP.');
      setTimeout(() => setUploadNotice(''), 3000);
      return;
    }
    setUploadingZip(true);
    setUploadNotice('Extracting ZIP...');
    try {
      const formData = new FormData();
      formData.append('zip', attachedZip.file);
      formData.append('projectId', activeProject.id);

      const res = await fetch('/api/uploads/zip', { method: 'POST', body: formData });
      const data = await res.json();

      if (data.success) {
        const count = data.totalExtracted || 0;
        setUploadNotice(`✅ Extracted ${count} files! ${data.checkpointCreated ? '(Git checkpoint created)' : ''}`);
        setZipResult(data);
        setAttachedZip(null);
        // Trigger file tree refresh
        useAppStore.getState().loadFileTree?.();
      } else {
        setUploadNotice(`❌ ZIP Error: ${data.error}`);
      }
    } catch (err) {
      setUploadNotice(`❌ Upload failed: ${err.message}`);
    } finally {
      setUploadingZip(false);
      setTimeout(() => setUploadNotice(''), 5000);
    }
  }, [attachedZip, activeProject]);

  // ── Upload images to backend before starting agent ──────────────────────────

  const uploadImages = useCallback(async () => {
    if (!attachedImages.length || !activeProject) return [];
    try {
      const formData = new FormData();
      formData.append('projectId', activeProject.id);
      attachedImages.forEach((img) => formData.append('images', img.file));

      const res = await fetch('/api/uploads/image', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) {
        return data.uploaded.map((u) => u.fullPath);
      }
    } catch (err) {
      console.error('Image upload error:', err);
    }
    return [];
  }, [attachedImages, activeProject]);

  // ── Submit ──────────────────────────────────────────────────────────────────

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    const text = prompt.trim();
    if (!text && attachedImages.length === 0) return;

    // Upload images first
    let imagePaths = [];
    if (attachedImages.length > 0) {
      imagePaths = await uploadImages();
    }

    if (agentStatus === 'RUNNING') {
      await overrideAgent(text);
    } else {
      await startAgent(text, { imagePaths, zipFile: null });
    }

    setPrompt('');
    setAttachedImages([]);
    setAttachedZip(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleQuickAction = (shortcut) => {
    setPrompt('');
    // Send shortcut directly as prompt
    startAgent(shortcut);
  };

  const isRunning = agentStatus === 'RUNNING';
  const isPaused = agentStatus === 'PAUSED';
  const hasAttachments = attachedImages.length > 0 || attachedZip;

  return (
    <div className="bg-ide-sidebar border-t border-ide-border shrink-0">

      {/* ── Quick Action Row ──────────────────────────────────────────────── */}
      <div className="flex items-center gap-1 px-3 pt-2 pb-1 flex-wrap">
        <span className="text-[10px] text-ide-muted font-mono mr-1">⚡ Quick:</span>
        {QUICK_ACTIONS.map((action) => (
          <button
            key={action.shortcut}
            onClick={() => handleQuickAction(action.shortcut)}
            disabled={isRunning}
            className={`flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium rounded border bg-ide-panel transition-all cursor-pointer disabled:opacity-40 ${action.color}`}
            title={`Send: "${action.shortcut}"`}
          >
            <action.icon className="w-2.5 h-2.5" />
            <span>{action.label}</span>
          </button>
        ))}
      </div>

      {/* ── Attached Images Preview Strip ─────────────────────────────────── */}
      {attachedImages.length > 0 && (
        <div className="flex items-center gap-2 px-3 py-1.5 border-t border-ide-border/50 flex-wrap">
          <span className="text-[10px] text-ide-muted font-mono">📎 Images:</span>
          {attachedImages.map((img) => (
            <div key={img.name} className="relative group flex items-center">
              <img
                src={img.dataUrl}
                alt={img.name}
                className="h-10 w-10 object-cover rounded border border-ide-border"
                title={img.name}
              />
              <button
                onClick={() => removeImage(img.name)}
                className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-rose-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-2 h-2 text-white" />
              </button>
              <span className="ml-1 text-[9px] text-ide-muted max-w-[50px] truncate">{img.name}</span>
            </div>
          ))}
          <span className="text-[10px] text-cyan-400">→ will be sent to {selectedProvider || 'AI'}</span>
        </div>
      )}

      {/* ── ZIP Badge ─────────────────────────────────────────────────────── */}
      {attachedZip && (
        <div className="flex items-center gap-2 px-3 py-1.5 border-t border-ide-border/50">
          <span className="text-[10px] text-ide-muted font-mono">📦 ZIP:</span>
          <div className="flex items-center gap-1.5 bg-amber-500/10 border border-amber-500/30 rounded px-2 py-0.5">
            <Archive className="w-3 h-3 text-amber-400" />
            <span className="text-[10px] text-amber-300 font-mono">{attachedZip.name}</span>
            <span className="text-[10px] text-ide-muted">({(attachedZip.size / 1024).toFixed(0)}KB)</span>
            <button
              onClick={() => setAttachedZip(null)}
              className="text-rose-400 hover:text-rose-300 ml-1"
            >
              <X className="w-2.5 h-2.5" />
            </button>
          </div>
          <button
            onClick={importZip}
            disabled={uploadingZip || !activeProject}
            className="px-2 py-0.5 text-[10px] bg-amber-500 hover:bg-amber-600 text-black font-semibold rounded disabled:opacity-50 transition-colors"
          >
            {uploadingZip ? 'Extracting...' : 'Import Now'}
          </button>
          {!activeProject && (
            <span className="text-[10px] text-rose-400">Select a project first</span>
          )}
        </div>
      )}

      {/* ── Notice Banner ─────────────────────────────────────────────────── */}
      {uploadNotice && (
        <div className="px-3 py-1 bg-cyan-900/30 border-t border-cyan-500/20 text-[10px] text-cyan-300 font-mono">
          {uploadNotice}
        </div>
      )}

      {/* ── Main Input Row ────────────────────────────────────────────────── */}
      <div className="flex items-start gap-2 px-3 py-2">
        {/* Text input */}
        <div className="relative flex-1">
          <textarea
            ref={inputRef}
            rows={2}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isRunning
                ? 'Agent running... type to override/redirect...'
                : attachedImages.length > 0
                ? `Describe what to do with ${attachedImages.length} image(s)... (Ctrl+Enter to start)`
                : "Enter project requirement or command (e.g. 'Build an expense tracker'). Press Ctrl+Enter to start"
            }
            className="w-full px-3 py-2 bg-ide-panel border border-ide-border focus:border-ide-accent rounded text-xs text-white placeholder-ide-muted focus:outline-none resize-none font-sans"
          />
          {/* Attachment buttons inside input */}
          <div className="absolute bottom-2 right-2 flex items-center gap-1">
            {/* Image attach */}
            <button
              onClick={() => imageInputRef.current?.click()}
              className="p-1 rounded text-ide-muted hover:text-white hover:bg-ide-hover transition-colors"
              title="Attach image(s) — send screenshot/UI reference to AI"
            >
              <Image className="w-3.5 h-3.5" />
            </button>
            {/* ZIP attach */}
            <button
              onClick={() => zipInputRef.current?.click()}
              className="p-1 rounded text-ide-muted hover:text-amber-300 hover:bg-amber-500/10 transition-colors"
              title="Import ZIP — extract into current project"
            >
              <Archive className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Hidden file inputs */}
        <input
          ref={imageInputRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={handleImageSelect}
        />
        <input
          ref={zipInputRef}
          type="file"
          accept=".zip"
          className="hidden"
          onChange={handleZipSelect}
        />

        {/* Right controls panel */}
        <div className="flex flex-col gap-1.5 shrink-0">
          <div className="flex items-center gap-1.5">
            {/* AI Provider Selector */}
            <div className="flex items-center bg-ide-panel rounded border border-ide-border p-0.5 text-xs text-ide-muted">
              <Bot className="w-3.5 h-3.5 ml-1 text-ide-accent" />
              <select
                value={selectedProvider || 'deepseek_web'}
                onChange={(e) => setProvider(e.target.value)}
                className="bg-transparent text-white text-xs px-1.5 py-0.5 focus:outline-none cursor-pointer font-medium"
                title="Select AI Provider"
              >
                <option value="deepseek_web" className="bg-ide-panel text-white">🤖 DeepSeek R1 (Default)</option>
                <option value="gemini_web" className="bg-ide-panel text-white">🌐 Google Gemini</option>
                <option value="chatgpt_web" className="bg-ide-panel text-white">✨ ChatGPT Web</option>
                <option value="nemotron" className="bg-ide-panel text-white">⚡ NVIDIA Nemotron 70B</option>
                <option value="smart" className="bg-ide-panel text-white">🧠 Smart Multi-Model</option>
                <option value="mock_provider" className="bg-ide-panel text-white">🔧 Local Simulator</option>
              </select>
            </div>

            {/* Quality Score HUD */}
            <div
              className="flex items-center gap-1 bg-ide-panel rounded border border-amber-500/30 px-2 py-1 text-xs font-semibold text-amber-400"
              title="Code Quality Score"
            >
              <span>🏆</span>
              <span>{useAppStore.getState().qualityScore || 100} pts</span>
            </div>

            {/* Active Role */}
            <div
              className="flex items-center gap-1 bg-ide-panel rounded border border-cyan-500/30 px-2 py-1 text-xs text-cyan-300 font-medium"
              title="Active Agent Role"
            >
              <span>🤖</span>
              <span>{useAppStore.getState().activeRole || 'Multi-Agent Team'}</span>
            </div>

            {/* Action Buttons */}
            {!isRunning && !isPaused ? (
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => {
                    setPrompt('');
                    setAttachedImages([]);
                    setAttachedZip(null);
                    const newName = `project_${Date.now().toString().slice(-4)}`;
                    useAppStore.getState().createProject(newName, '');
                    useAppStore.setState({ terminalLogs: [], tasks: [], openTabs: [], activeTab: null });
                  }}
                  className="px-2.5 py-1.5 bg-ide-panel hover:bg-ide-hover border border-ide-border text-slate-300 hover:text-white rounded text-xs flex items-center gap-1 transition-colors"
                  title="New Project & Conversation"
                >
                  <MessageSquarePlus className="w-3.5 h-3.5 text-ide-accent" />
                  <span>New Convo</span>
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!prompt.trim() && attachedImages.length === 0}
                  className="px-4 py-1.5 bg-ide-accent hover:opacity-90 disabled:opacity-50 text-black font-semibold rounded text-xs flex items-center gap-1.5 transition-all shadow-sm shadow-blue-500/20"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>
                    START
                    {hasAttachments && (
                      <span className="ml-1 bg-black/20 rounded px-1">
                        {attachedImages.length > 0 ? `+${attachedImages.length}📎` : ''}
                      </span>
                    )}
                  </span>
                </button>
              </div>
            ) : isPaused ? (
              <button
                onClick={resumeAgent}
                className="px-4 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded text-xs flex items-center gap-1.5 transition-colors"
              >
                <Play className="w-3.5 h-3.5" />
                <span>RESUME</span>
              </button>
            ) : (
              <div className="flex items-center gap-1">
                <button
                  onClick={handleSubmit}
                  disabled={!prompt.trim()}
                  className="px-3 py-1.5 bg-ide-hover hover:bg-ide-panel border border-ide-border text-white rounded text-xs flex items-center gap-1 transition-colors"
                  title="Override current goal"
                >
                  <Send className="w-3.5 h-3.5 text-ide-accent" />
                  <span>OVERRIDE</span>
                </button>
                <button
                  onClick={pauseAgent}
                  className="px-3 py-1.5 bg-amber-500/20 border border-amber-500/40 text-amber-300 hover:bg-amber-500/30 rounded text-xs flex items-center gap-1 transition-colors"
                >
                  <Pause className="w-3.5 h-3.5" />
                  <span>PAUSE</span>
                </button>
                <button
                  onClick={stopAgent}
                  className="px-3 py-1.5 bg-rose-500/20 border border-rose-500/40 text-rose-300 hover:bg-rose-500/30 rounded text-xs flex items-center gap-1 transition-colors"
                >
                  <Square className="w-3.5 h-3.5" />
                  <span>STOP</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
