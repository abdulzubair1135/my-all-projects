import React, { useState, useEffect } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { api } from '../../services/api';
import {
  Layers,
  Smartphone,
  Wrench,
  Camera,
  Gamepad2,
  Server,
  BarChart3,
  FileText,
  Presentation,
  Sparkles,
  ShieldAlert,
  Cpu,
  Rocket,
  Search,
  X,
  CheckCircle,
  ArrowRight,
  Zap
} from 'lucide-react';

const ICON_MAP = {
  Layers,
  Smartphone,
  Wrench,
  Camera,
  Gamepad2,
  Server,
  BarChart3,
  FileText,
  Presentation,
  Sparkles,
  ShieldAlert,
  Cpu,
  Rocket
};

export function TemplateGalleryModal({ isOpen, onClose }) {
  const { loadProjects, selectProject } = useAppStore();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [instantiating, setInstantiating] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [activeTemplate, setActiveTemplate] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchTemplates();
    }
  }, [isOpen]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const data = await api.getTemplates();
      setTemplates(data || []);
      if (data && data.length > 0) {
        setActiveTemplate(data[0]);
        setProjectName(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load templates:', err);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['All', ...new Set(templates.map((t) => t.category))];

  const filtered = templates.filter((t) => {
    const matchesCategory = selectedCategory === 'All' || t.category === selectedCategory;
    const matchesSearch =
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.tech_stack?.some((s) => s.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const handleSelectTemplate = (t) => {
    setActiveTemplate(t);
    setProjectName(t.id);
  };

  const handleLaunch = async () => {
    if (!activeTemplate) return;
    setInstantiating(activeTemplate.id);
    try {
      const res = await api.instantiateTemplate(activeTemplate.id, projectName.trim() || activeTemplate.id);
      if (res.success && res.project) {
        await loadProjects();
        selectProject(res.project.id);
        onClose();
      }
    } catch (err) {
      alert(`Failed to instantiate template: ${err.message}`);
    } finally {
      setInstantiating(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-6 select-none font-sans">
      <div className="bg-ide-panel border border-ide-border rounded-xl w-full max-w-5xl h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-ide-border flex items-center justify-between bg-ide-sidebar">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">
                Autonomous Mission Template Gallery
              </h2>
              <p className="text-[11px] text-ide-muted">
                Section 65 Production Blueprints — Choose an autonomous software-engineering mission
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-ide-muted hover:text-white rounded-lg hover:bg-ide-bg transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Filter Bar */}
        <div className="px-6 py-3 border-b border-ide-border bg-ide-sidebar/50 flex items-center justify-between gap-4">
          <div className="flex items-center gap-1.5 overflow-x-auto py-1 scrollbar-none">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-colors shrink-0 ${
                  selectedCategory === cat
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-ide-panel text-ide-muted hover:text-white border border-ide-border hover:border-ide-muted/50'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="relative w-64 shrink-0">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-ide-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search templates or tech..."
              className="w-full bg-ide-bg border border-ide-border rounded-lg pl-8 pr-3 py-1 text-xs text-white placeholder-ide-muted focus:outline-none focus:border-indigo-500 font-sans"
            />
          </div>
        </div>

        {/* Content Body: Left grid, Right preview */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left list of templates */}
          <div className="w-7/12 border-r border-ide-border overflow-y-auto p-4 grid grid-cols-2 gap-3">
            {filtered.map((tmpl) => {
              const IconComp = ICON_MAP[tmpl.icon] || Layers;
              const isSelected = activeTemplate?.id === tmpl.id;
              return (
                <div
                  key={tmpl.id}
                  onClick={() => handleSelectTemplate(tmpl)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition-all flex flex-col justify-between text-xs ${
                    isSelected
                      ? 'bg-indigo-950/40 border-indigo-500 shadow-md ring-1 ring-indigo-500/50'
                      : 'bg-ide-panel/60 border-ide-border hover:border-ide-muted/60 hover:bg-ide-panel'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className={`p-1.5 rounded ${isSelected ? 'bg-indigo-600 text-white' : 'bg-ide-bg text-indigo-400 border border-ide-border'}`}>
                        <IconComp className="w-4 h-4" />
                      </div>
                      <span className="font-semibold text-white truncate text-[12px]">{tmpl.title}</span>
                    </div>
                    {tmpl.badge && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-medium uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        {tmpl.badge}
                      </span>
                    )}
                  </div>

                  <p className="text-[11px] text-ide-muted mt-2 line-clamp-2 leading-relaxed">
                    {tmpl.description}
                  </p>

                  <div className="flex flex-wrap gap-1 mt-3">
                    {tmpl.tech_stack?.slice(0, 3).map((st) => (
                      <span key={st} className="px-1.5 py-0.5 rounded bg-ide-bg text-[10px] text-ide-muted border border-ide-border font-mono">
                        {st}
                      </span>
                    ))}
                    {tmpl.tech_stack?.length > 3 && (
                      <span className="text-[10px] text-ide-muted px-1 py-0.5">+{tmpl.tech_stack.length - 3}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right inspection & launch pane */}
          {activeTemplate ? (
            <div className="w-5/12 p-6 flex flex-col justify-between overflow-y-auto bg-ide-sidebar/30">
              <div className="flex flex-col gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 font-semibold">
                      {activeTemplate.category}
                    </span>
                    <span className="text-xs text-ide-muted font-mono">{activeTemplate.id}</span>
                  </div>
                  <h3 className="text-lg font-bold text-white mt-1.5">{activeTemplate.title}</h3>
                  <p className="text-xs text-ide-muted mt-1 leading-relaxed">{activeTemplate.description}</p>
                </div>

                {/* Tech Stack */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-[11px] font-semibold text-ide-text uppercase tracking-wider">
                    Engineered Toolchain
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {activeTemplate.tech_stack?.map((t) => (
                      <span key={t} className="px-2 py-0.5 rounded bg-ide-bg border border-ide-border text-xs text-indigo-300 font-mono">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Acceptance Criteria */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-[11px] font-semibold text-ide-text uppercase tracking-wider">
                    Acceptance Criteria (Section 30)
                  </span>
                  <div className="flex flex-col gap-1.5 bg-ide-panel/80 p-3 rounded-lg border border-ide-border">
                    {activeTemplate.acceptance_criteria?.map((crit, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-ide-text">
                        <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                        <span className="leading-snug">{crit}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Mission Prompt Preview */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-[11px] font-semibold text-ide-text uppercase tracking-wider">
                    Autonomous Mission Prompt
                  </span>
                  <div className="bg-ide-bg p-2.5 rounded border border-ide-border text-[11px] text-ide-muted font-mono leading-relaxed">
                    "{activeTemplate.prompt}"
                  </div>
                </div>
              </div>

              {/* Bottom Action Footer */}
              <div className="pt-4 border-t border-ide-border flex flex-col gap-2.5 mt-4">
                <div className="flex flex-col gap-1">
                  <label className="text-[11px] text-ide-muted font-medium">Workspace Folder Name</label>
                  <input
                    type="text"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="project_name"
                    className="w-full bg-ide-bg border border-ide-border rounded px-2.5 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <button
                  onClick={handleLaunch}
                  disabled={instantiating === activeTemplate.id}
                  className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg"
                >
                  <span>{instantiating ? 'Creating Project & Workspace...' : 'Launch Mission Blueprint'}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ) : (
            <div className="w-5/12 flex items-center justify-center text-xs text-ide-muted p-6">
              Select a template to inspect details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
