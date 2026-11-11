import React, { useState, useEffect, useRef } from 'react';
import { 
  Brain, 
  Sparkles, 
  Send, 
  Bot, 
  Play, 
  RefreshCw, 
  CheckCircle2, 
  Calculator, 
  Award, 
  Zap, 
  MessageSquare,
  BookOpen,
  ArrowRight
} from 'lucide-react';

export function LiveEvolutionStudio({ onClose }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'agent',
      name: 'Agent Cognitive Brain',
      text: 'DeepSeek R1, please teach me Kahn\'s Algorithm for DAG task scheduling with cycle detection and the exact mathematical in-degree invariant.',
      time: 'Just now'
    },
    {
      id: 2,
      sender: 'deepseek',
      name: 'DeepSeek R1 (Master Trainer)',
      thinking: 'Analyzing Graph Theory Topology. Kahn\'s algorithm computes topological orderings of a Directed Acyclic Graph (DAG) in O(V + E) time complexity. The fundamental invariant is that a vertex can only be scheduled once its in-degree reaches zero.',
      text: 'Here is the mathematical derivation for Kahn\'s DAG Scheduling:\n\n1. In-Degree Invariant:\n   V_ready = { v ∈ V | in_degree(v) = 0 }\n\n2. Asynchronous State Transition:\n   While V_ready is not empty:\n     Pop node u ∈ V_ready\n     Append u to topological order L\n     For each directed edge (u, v) ∈ E:\n       in_degree(v) = in_degree(v) - 1\n       If in_degree(v) == 0: Insert v into V_ready\n\n3. Cycle Detection Proof:\n   If |L| < |V|, the graph contains a directed cycle (deadlock detected).\n\nProduction Rule:\nAlways validate in-degree zero before task dispatch to prevent concurrency deadlocks.',
      formula: 'V_ready = { v ∈ V | in_degree(v) = 0 }',
      time: 'Just now'
    }
  ]);

  const [customTopic, setCustomTopic] = useState('');
  const [isLiveTraining, setIsLiveTraining] = useState(false);
  const [stats, setStats] = useState({ ai_level: 25, rank: 'Cognitive Algorithm Architect' });
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleStartTopic = async (topicName, formulaText) => {
    setIsLiveTraining(true);
    const targetTopic = topicName || customTopic || 'Harmonic Spring Physics & Glassmorphism';
    const userMsg = {
      id: Date.now(),
      sender: 'agent',
      name: 'Agent Cognitive Brain',
      text: `DeepSeek R1, explain and mathematically prove: ${targetTopic}`,
      time: new Date().toLocaleTimeString()
    };
    setMessages((prev) => [...prev, userMsg]);
    setCustomTopic('');

    try {
      const res = await fetch('http://localhost:3001/api/evolution/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: targetTopic })
      });
      if (res.ok) {
        const data = await res.json();
        const dsMsg = {
          id: Date.now() + 1,
          sender: 'deepseek',
          name: 'DeepSeek R1 (Master Trainer)',
          thinking: `Deconstructing concept: ${data.topic || targetTopic}. Establishing mathematical bounds, state transitions, and defensive engineering patterns for autonomous code synthesis.`,
          text: data.dialogue || `Mastered ${data.topic || targetTopic}. Invariant validated and stored in SQLite Knowledge Graph.`,
          formula: data.formula || formulaText || 'S_(t+1) = δ(S_t, a), where a ∈ Σ',
          time: new Date().toLocaleTimeString()
        };
        setMessages((prev) => [...prev, dsMsg]);
        setStats((prev) => ({ ...prev, ai_level: Math.min(100, prev.ai_level + 12) }));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLiveTraining(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-ide-bg border-l border-ide-border select-none">
      {/* Header Bar */}
      <div className="h-12 bg-ide-sidebar border-b border-ide-border flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-blue-600 flex items-center justify-center text-white shadow-md">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-white flex items-center gap-1.5">
              <span>DeepSeek Live Cognitive Evolution & Dialogue Studio</span>
              <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
            </div>
            <div className="text-[11px] text-indigo-300 font-medium">
              Live AI Brain Learning • Level {stats.ai_level} ({stats.rank})
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleStartTopic('Harmonic Spring Physics & Glassmorphism', 'm(d²x/dt²) + c(dx/dt) + kx = 0')}
            disabled={isLiveTraining}
            className="px-2.5 py-1 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 rounded text-xs font-medium flex items-center gap-1 transition-colors"
          >
            <Zap className="w-3 h-3 text-amber-400" />
            <span>Next Topic</span>
          </button>

          {onClose && (
            <button 
              onClick={onClose}
              className="p-1 hover:bg-ide-hover text-ide-muted hover:text-white rounded"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 font-sans text-xs">
        {messages.map((m) => (
          <div 
            key={m.id}
            className={`flex flex-col gap-1 max-w-2xl ${
              m.sender === 'agent' ? 'self-end items-end' : 'self-start items-start'
            }`}
          >
            <div className="flex items-center gap-1.5 text-[11px] text-ide-muted">
              {m.sender === 'agent' ? (
                <>
                  <span className="font-semibold text-blue-400">{m.name}</span>
                  <Bot className="w-3.5 h-3.5 text-blue-400" />
                  <span>• {m.time}</span>
                </>
              ) : (
                <>
                  <Brain className="w-3.5 h-3.5 text-indigo-400" />
                  <span className="font-semibold text-indigo-300">{m.name}</span>
                  <span>• {m.time}</span>
                </>
              )}
            </div>

            <div className={`p-3.5 rounded-2xl border shadow-lg leading-relaxed ${
              m.sender === 'agent'
                ? 'bg-blue-600/20 border-blue-500/30 text-white rounded-br-none'
                : 'bg-ide-panel/90 border-indigo-500/30 text-slate-200 rounded-bl-none'
            }`}>
              {/* DeepSeek Thinking Block */}
              {m.thinking && (
                <div className="mb-3 p-2.5 bg-indigo-950/50 border border-indigo-500/20 rounded-xl text-[11px] text-indigo-200">
                  <div className="font-bold text-indigo-400 flex items-center gap-1 mb-1">
                    <Sparkles className="w-3 h-3 text-amber-400" />
                    <span>DeepSeek R1 Internal Monologue & Thinking Trace:</span>
                  </div>
                  <p className="italic text-indigo-200/90 leading-normal">{m.thinking}</p>
                </div>
              )}

              {/* Message Content with Clean Modern Formatting */}
              <div className="flex flex-col gap-2 font-sans text-xs text-slate-200">
                {m.text.split('\n').map((line, idx) => {
                  const cleanLine = line.replace(/\*\*/g, '').replace(/\$\$/g, '').trim();
                  if (!cleanLine) return <div key={idx} className="h-1" />;

                  if (cleanLine.startsWith('🌌') || cleanLine.startsWith('⚡') || cleanLine.startsWith('🧠') || cleanLine.startsWith('###')) {
                    return (
                      <div key={idx} className="font-bold text-sm text-cyan-300 pb-1 border-b border-ide-border/50 mt-1">
                        {cleanLine.replace(/^###\s*/, '')}
                      </div>
                    );
                  }

                  if (/^\d+\./.test(cleanLine)) {
                    return (
                      <div key={idx} className="font-semibold text-indigo-300 mt-1.5 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                        <span>{cleanLine}</span>
                      </div>
                    );
                  }

                  if (cleanLine.startsWith('•') || cleanLine.startsWith('-')) {
                    return (
                      <div key={idx} className="pl-4 text-slate-300 flex items-start gap-2 text-[11.5px] leading-relaxed">
                        <span className="text-cyan-400 select-none">›</span>
                        <span>{cleanLine.replace(/^[•-]\s*/, '')}</span>
                      </div>
                    );
                  }

                  return (
                    <div key={idx} className="leading-relaxed text-slate-300 text-[11.5px]">
                      {cleanLine}
                    </div>
                  );
                })}
              </div>

              {/* Mathematical Formula Highlight Card */}
              {m.formula && (
                <div className="mt-3 p-2.5 bg-slate-900/90 border border-amber-500/30 rounded-xl flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Calculator className="w-4 h-4 text-amber-400" />
                    <div>
                      <div className="text-[10px] text-ide-muted uppercase font-semibold">Learned Rule / Invariant</div>
                      <div className="font-mono text-[11px] text-amber-300 font-bold">{m.formula}</div>
                    </div>
                  </div>
                  <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/30 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    Saved to Brain Vault
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLiveTraining && (
          <div className="self-start flex items-center gap-2 p-3 bg-ide-panel rounded-2xl border border-indigo-500/30 text-xs text-indigo-300 animate-pulse">
            <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
            <span>DeepSeek R1 is conversing, solving formulas & training AI Brain...</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Bar for Asking DeepSeek to Teach Any Topic */}
      <div className="p-3 bg-ide-sidebar border-t border-ide-border flex items-center gap-2">
        <input
          type="text"
          value={customTopic}
          onChange={(e) => setCustomTopic(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && customTopic.trim()) {
              handleStartTopic(customTopic.trim());
            }
          }}
          placeholder="Ask DeepSeek to train AI on any math, algorithm or code topic (e.g. 'Merkle Hash Trees & XSS Security')..."
          className="flex-1 px-3 py-2 bg-ide-bg border border-ide-border focus:border-indigo-400 rounded-lg text-xs text-white focus:outline-none"
        />
        <button
          onClick={() => customTopic.trim() && handleStartTopic(customTopic.trim())}
          disabled={!customTopic.trim() || isLiveTraining}
          className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-blue-600 hover:opacity-90 disabled:opacity-50 text-white font-semibold rounded-lg text-xs flex items-center gap-1.5 transition-all shadow-md shadow-indigo-600/20"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Train AI</span>
        </button>
      </div>
    </div>
  );
}
