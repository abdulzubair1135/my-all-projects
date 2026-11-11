import React, { useState } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { api } from '../../services/api';
import {
  Sparkles,
  Gamepad2,
  Layers,
  Presentation,
  FileText,
  BarChart3,
  X,
  ArrowRight,
  CheckCircle,
  Cpu,
  Palette,
  Volume2,
  ShieldCheck,
  Zap
} from 'lucide-react';

const PROJECT_TYPES = [
  { id: 'game', label: '2D / 3D Game', icon: Gamepad2, desc: 'Arcade action, space combat, platformer, or puzzle' },
  { id: 'webapp', label: 'Interactive Web App', icon: Layers, desc: 'Full-stack responsive application with state machine' },
  { id: 'presentation', label: 'Interactive PPT / Slides', icon: Presentation, desc: 'Slide deck studio with animations and PNG/PDF export' },
  { id: 'report', label: 'Whitepaper / Report', icon: FileText, desc: 'Technical research documentation with visual charts' },
  { id: 'dashboard', label: 'Analytics Dashboard', icon: BarChart3, desc: 'Real-time telemetry, charts, and metrics viewer' }
];

const UI_STYLES = [
  { id: 'retro', label: 'Retro 8-Bit Arcade', desc: 'Chiptune vibe, CRT scanlines, neon pixel styling' },
  { id: 'cyberpunk', label: 'Cyberpunk Neon Glass', desc: 'Glowing magenta/cyan borders, dark glassmorphism' },
  { id: 'bento', label: 'Minimalist Bento-Grid', desc: 'Clean, modern card-based layout like Apple / Linear' },
  { id: 'saas', label: 'Enterprise Corporate SaaS', desc: 'Polished, accessible light/dark theme, clean typography' }
];

const GAME_ENGINES = [
  { id: 'godot_csharp', label: 'Godot 4.x (C#)', desc: 'Type-safe C# scripts (.NET 8), scenes, and custom shaders' },
  { id: 'html5_canvas', label: 'HTML5 Canvas / JS', desc: '100% in-browser 60FPS playable with zero installation' },
  { id: 'cpp_raylib', label: 'C++ (Raylib / SDL2)', desc: 'High-performance native binary with CMake build pipeline' },
  { id: 'godot_gdscript', label: 'Godot 4.x (GDScript)', desc: 'Node graph architecture with GDScript controller nodes' }
];

export function ProjectWizardModal({ isOpen, onClose }) {
  const { loadProjects, selectProject, startAgent } = useAppStore();

  const [step, setStep] = useState(1);
  const [projectName, setProjectName] = useState('');
  const [projectType, setProjectType] = useState('game');
  const [uiStyle, setUiStyle] = useState('retro');
  const [gameEngine, setGameEngine] = useState('godot_csharp');
  const [autonomousAssets, setAutonomousAssets] = useState(true);
  const [autonomousSound, setAutonomousSound] = useState(true);
  const [qualityTier, setQualityTier] = useState('AAA_PRODUCTION');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleCreateAndLaunch = async () => {
    if (!projectName.trim()) return;
    setIsSubmitting(true);
    try {
      const cleanSlug = projectName.trim().toLowerCase().replace(/[^a-z0-9]+/g, '_');
      const engineLabel = projectType === 'game' ? gameEngine : 'React 18 + Vite';
      const prompt = `Build a complete, production-grade ${projectType.toUpperCase()} named "${projectName}". ` +
        `Style: ${uiStyle}. Engine/Stack: ${engineLabel}. ` +
        `Autonomous Assets: 2D pixel art sprites (${autonomousAssets ? 'YES' : 'NO'}), ` +
        `Sound FX (${autonomousSound ? 'YES' : 'NO'}). Quality Tier: ${qualityTier}.`;

      // 1. Create project in backend
      const project = await api.createProject(cleanSlug, prompt);

      // 2. Register profile in persistent memory
      try {
        await fetch(`/api/projects/${project.id}/memory`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project_name: projectName,
            project_type: projectType,
            ui_style: uiStyle,
            game_engine: engineLabel,
            asset_strategy: autonomousAssets ? 'Autonomous Procedural Pixel Art & SFX' : 'Standard SVG',
            quality_tier: qualityTier,
            notes: prompt
          })
        });
      } catch (e) {}

      // 3. Reload projects and select new project
      await loadProjects();
      selectProject(project.id);

      // 4. Start agent mission
      startAgent(project.id, prompt);
      onClose();
    } catch (err) {
      alert('Error creating project: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="relative w-full max-w-3xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 shadow-md">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-black tracking-wide text-white">
                Project Specification Wizard
              </h2>
              <p className="text-xs text-slate-400">
                Configure Project Type, UI Theme, Engine, and Autonomous 2D Assets
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Wizard Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Step 1: Project Name & Type */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              Project Title & Name
            </label>
            <input
              type="text"
              placeholder="e.g. Retro 8-Bit Space Arcade"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 transition"
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              Select Target Category
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {PROJECT_TYPES.map((t) => {
                const Icon = t.icon;
                const isSel = projectType === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => setProjectType(t.id)}
                    className={`p-3.5 rounded-xl border text-left transition flex flex-col justify-between ${
                      isSel
                        ? 'bg-cyan-500/20 border-cyan-500 text-cyan-200 shadow-md shadow-cyan-500/10'
                        : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <Icon className={`w-5 h-5 ${isSel ? 'text-cyan-400' : 'text-slate-400'}`} />
                      {isSel && <CheckCircle className="w-4 h-4 text-cyan-400" />}
                    </div>
                    <div className="font-bold text-sm text-slate-100">{t.label}</div>
                    <div className="text-[11px] text-slate-400 mt-1 leading-tight">{t.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Step 2: UI Style & Theme */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
              <Palette className="w-4 h-4 text-purple-400" /> UI Design System & Aesthetic
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {UI_STYLES.map((s) => {
                const isSel = uiStyle === s.id;
                return (
                  <button
                    key={s.id}
                    onClick={() => setUiStyle(s.id)}
                    className={`p-3 rounded-xl border text-left transition flex items-center justify-between ${
                      isSel
                        ? 'bg-purple-500/20 border-purple-500 text-purple-200 shadow-md shadow-purple-500/10'
                        : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                    }`}
                  >
                    <div>
                      <div className="font-bold text-sm text-slate-100">{s.label}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{s.desc}</div>
                    </div>
                    {isSel && <CheckCircle className="w-4 h-4 text-purple-400 shrink-0 ml-2" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Step 3: Game Engine (If Game is selected) */}
          {projectType === 'game' && (
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-emerald-400" /> Game Stack & Engine
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {GAME_ENGINES.map((eng) => {
                  const isSel = gameEngine === eng.id;
                  return (
                    <button
                      key={eng.id}
                      onClick={() => setGameEngine(eng.id)}
                      className={`p-3 rounded-xl border text-left transition flex items-center justify-between ${
                        isSel
                          ? 'bg-emerald-500/20 border-emerald-500 text-emerald-200 shadow-md shadow-emerald-500/10'
                          : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                      }`}
                    >
                      <div>
                        <div className="font-bold text-sm text-slate-100">{eng.label}</div>
                        <div className="text-[11px] text-slate-400 mt-0.5">{eng.desc}</div>
                      </div>
                      {isSel && <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 ml-2" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Step 4: Autonomous Assets & Sound */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-amber-400" /> Autonomous Assets & Generation Pipeline
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <label className="flex items-center gap-3 p-3 bg-slate-950/60 border border-slate-800 rounded-xl cursor-pointer hover:border-slate-700">
                <input
                  type="checkbox"
                  checked={autonomousAssets}
                  onChange={(e) => setAutonomousAssets(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded"
                />
                <div>
                  <span className="text-sm font-bold text-slate-200 block">Autonomous 2D Sprites & Textures</span>
                  <span className="text-[11px] text-slate-400">Generates custom pixel art / PNG sprites directly</span>
                </div>
              </label>

              <label className="flex items-center gap-3 p-3 bg-slate-950/60 border border-slate-800 rounded-xl cursor-pointer hover:border-slate-700">
                <input
                  type="checkbox"
                  checked={autonomousSound}
                  onChange={(e) => setAutonomousSound(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded"
                />
                <div>
                  <span className="text-sm font-bold text-slate-200 block">Procedural 8-Bit Sound FX</span>
                  <span className="text-[11px] text-slate-400">Synthesizes retro chiptune WAV laser/explosion audio</span>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Footer Buttons */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-950/60">
          <div className="text-xs text-slate-500 font-mono">
            Memory Ledger: SQLite Synced
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold rounded-xl text-slate-400 hover:text-white transition"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateAndLaunch}
              disabled={isSubmitting || !projectName.trim()}
              className={`flex items-center gap-2 px-6 py-2.5 text-xs font-bold rounded-xl transition-all shadow-lg ${
                !projectName.trim() || isSubmitting
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-cyan-500/25'
              }`}
            >
              {isSubmitting ? 'Architecting...' : 'Launch Project Build'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
