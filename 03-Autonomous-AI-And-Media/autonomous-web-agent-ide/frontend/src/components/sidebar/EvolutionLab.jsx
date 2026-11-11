import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Sparkles, 
  Calculator, 
  BookOpen, 
  Award, 
  CheckCircle2, 
  TrendingUp, 
  Layers, 
  ShieldCheck, 
  RefreshCw,
  SearchCode,
  MessageSquare
} from 'lucide-react';
import { LiveEvolutionStudio } from '../evolution/LiveEvolutionStudio';

export function EvolutionLab() {
  const [stats, setStats] = useState({
    ai_level: 25,
    rank: 'Cognitive Algorithm Architect',
    total_topics_mastered: 4,
    average_mastery: 96,
    recent_lessons: []
  });
  const [isTraining, setIsTraining] = useState(false);
  const [latestSession, setLatestSession] = useState(null);
  const [showLiveStudio, setShowLiveStudio] = useState(false);

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:3001/api/evolution/stats');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (e) {
      // Offline fallback
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleTriggerTraining = async () => {
    setIsTraining(true);
    try {
      const res = await fetch('http://localhost:3001/api/evolution/train', { method: 'POST' });
      if (res.ok) {
        const result = await res.json();
        setLatestSession(result);
        await fetchStats();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-ide-sidebar overflow-y-auto p-3 text-xs">
      {/* Header Badge */}
      <div className="flex items-center justify-between p-2.5 bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-blue-900/40 border border-indigo-500/30 rounded-xl mb-3 shadow-lg">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <div className="font-bold text-white text-xs flex items-center gap-1.5">
              <span>DeepSeek Brain Evolution</span>
              <Sparkles className="w-3 h-3 text-amber-400" />
            </div>
            <div className="text-[11px] text-indigo-300 font-medium">
              Level {stats.ai_level} • {stats.rank}
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-3 bg-ide-panel p-2.5 rounded-lg border border-ide-border">
        <div className="flex justify-between text-[11px] font-semibold text-ide-muted mb-1.5">
          <span>Cognitive Mastery Progress</span>
          <span className="text-cyan-400">{stats.ai_level}%</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
          <div 
            className="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 h-2 rounded-full transition-all duration-500" 
            style={{ width: `${stats.ai_level}%` }}
          />
        </div>
      </div>

      {/* Trigger Daily Training Button */}
      <button
        onClick={handleTriggerTraining}
        disabled={isTraining}
        className="w-full py-2 px-3 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-semibold rounded-lg flex items-center justify-center gap-2 shadow-md shadow-indigo-600/20 mb-2 disabled:opacity-50 transition-all text-xs cursor-pointer"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${isTraining ? 'animate-spin' : ''}`} />
        <span>{isTraining ? 'DeepSeek Training in Progress...' : 'Train With DeepSeek R1 Now'}</span>
      </button>

      {/* Button to Open Live Evolution Chat Studio Modal */}
      <button
        onClick={() => setShowLiveStudio(true)}
        className="w-full py-1.5 px-3 bg-ide-panel hover:bg-ide-hover border border-indigo-500/30 text-indigo-300 font-semibold rounded-lg flex items-center justify-center gap-2 mb-3 transition-colors text-xs cursor-pointer"
      >
        <MessageSquare className="w-3.5 h-3.5 text-amber-400" />
        <span>Watch Live DeepSeek Chat Studio</span>
      </button>

      {/* Modal Popup */}
      {showLiveStudio && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-6">
          <div className="w-full max-w-4xl h-[85vh] bg-ide-bg border border-indigo-500/40 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
            <LiveEvolutionStudio onClose={() => setShowLiveStudio(false)} />
          </div>
        </div>
      )}

      {/* Latest Session Alert */}
      {latestSession && (
        <div className="p-2.5 bg-emerald-950/40 border border-emerald-500/30 rounded-lg mb-3">
          <div className="flex items-center gap-1.5 text-emerald-400 font-semibold text-[11px] mb-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Mastered: {latestSession.topic}</span>
          </div>
          <div className="font-mono text-[10px] bg-slate-900/80 p-1.5 rounded text-amber-300 border border-amber-500/20 mb-1">
            {latestSession.formula}
          </div>
          <p className="text-[11px] text-slate-300 leading-snug">{latestSession.domain}</p>
        </div>
      )}

      {/* Semantic Deep Research Knowledge Graph */}
      <div className="font-semibold text-ide-muted uppercase tracking-wider text-[11px] mb-2 flex items-center gap-1.5">
        <SearchCode className="w-3.5 h-3.5 text-cyan-400" />
        <span>Deep Research Knowledge Graph</span>
      </div>

      <div className="flex flex-col gap-2 mb-3">
        <div className="p-2.5 bg-ide-panel rounded-lg border border-cyan-500/30">
          <div className="flex justify-between items-center mb-1">
            <span className="font-semibold text-cyan-300 text-[11px]">Kahn's DAG Sorter</span>
            <span className="text-[10px] text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded">Comprehended</span>
          </div>
          <p className="text-[10px] text-slate-300 mb-1">
            <strong>Deep Meaning:</strong> Resolves asynchronous task order via in-degree tracking, proving zero cyclic deadlocks in polynomial time.
          </p>
          <div className="font-mono text-[9px] text-amber-300 bg-slate-900/60 p-1 rounded">
            Invariant: V_ready = &#123; v | in_degree(v) == 0 &#125;
          </div>
        </div>

        <div className="p-2.5 bg-ide-panel rounded-lg border border-indigo-500/30">
          <div className="flex justify-between items-center mb-1">
            <span className="font-semibold text-indigo-300 text-[11px]">Deterministic State Reductions</span>
            <span className="text-[10px] text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded">Comprehended</span>
          </div>
          <p className="text-[10px] text-slate-300 mb-1">
            <strong>Deep Meaning:</strong> Pure transition mapping S_(t+1) = &delta;(S_t, a). Guarantees reproducible UI state machines without side-effects.
          </p>
          <div className="font-mono text-[9px] text-indigo-300 bg-slate-900/60 p-1 rounded">
            Formula: S_(t+1) = &delta;(S_t, a), where a &isin; &Sigma;
          </div>
        </div>

        <div className="p-2.5 bg-ide-panel rounded-lg border border-purple-500/30">
          <div className="flex justify-between items-center mb-1">
            <span className="font-semibold text-purple-300 text-[11px]">Underdamped Spring Damping</span>
            <span className="text-[10px] text-purple-400 bg-purple-500/10 px-1.5 py-0.5 rounded">Comprehended</span>
          </div>
          <p className="text-[10px] text-slate-300 mb-1">
            <strong>Deep Meaning:</strong> Physical harmonic oscillator equation m(d&sup2;x/dt&sup2;) + c(dx/dt) + kx = 0 modeling fluid glassmorphic micro-interactions.
          </p>
          <div className="font-mono text-[9px] text-purple-300 bg-slate-900/60 p-1 rounded">
            Ratio: &zeta; = c / (2&radic;(mk)) &lt; 1
          </div>
        </div>
      </div>
    </div>
  );
}
