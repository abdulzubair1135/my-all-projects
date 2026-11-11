import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Project, RiskFinding, RiskSeverity } from '../types';
import {
  ShieldAlert,
  Play,
  RefreshCw,
  AlertTriangle,
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
  Search,
  Plus,
  SlidersHorizontal,
  X
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Risks: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [risks, setRisks] = useState<RiskFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filter & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [dismissedRiskIds, setDismissedRiskIds] = useState<string[]>([]);
  const [acknowledgedMsg, setAcknowledgedMsg] = useState<string | null>(null);

  useEffect(() => {
    async function loadProjects() {
      try {
        const prjs = await api.getProjects();
        setProjects(prjs);
        if (prjs.length > 0) {
          setSelectedProjectId(prjs[0].id);
        } else {
          setLoading(false);
        }
      } catch (err: any) {
        console.warn('Failed to load projects', err);
        setLoading(false);
      }
    }
    loadProjects();
  }, []);

  const fetchRisks = async (projId: string) => {
    if (!projId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getProjectRisks(projId);
      setRisks(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch risk radar findings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProjectId) {
      fetchRisks(selectedProjectId);
    }
  }, [selectedProjectId]);

  const handleRunEvaluation = async () => {
    if (!selectedProjectId) return;
    setEvaluating(true);
    try {
      const results = await api.evaluateRisks(selectedProjectId);
      setRisks(results || []);
      setDismissedRiskIds([]);
    } catch (err: any) {
      alert(`Evaluation failed: ${err.message}`);
    } finally {
      setEvaluating(false);
    }
  };

  const handleDismissRisk = (idx: number, title: string) => {
    setDismissedRiskIds(prev => [...prev, `${idx}`]);
    setAcknowledgedMsg(`Risk "${title}" acknowledged and marked as mitigated.`);
    setTimeout(() => setAcknowledgedMsg(null), 3000);
  };

  const getSeverityBadge = (s: RiskSeverity) => {
    switch (s) {
      case 'CRITICAL':
        return <span className="bg-[#B7473C]/15 text-[#B7473C] px-2.5 py-0.5 rounded text-[11px] font-mono font-bold">CRITICAL</span>;
      case 'HIGH':
        return <span className="bg-[#D97706]/15 text-[#D97706] px-2.5 py-0.5 rounded text-[11px] font-mono font-bold">HIGH</span>;
      case 'MEDIUM':
        return <span className="bg-[#56664C]/15 text-[#56664C] px-2.5 py-0.5 rounded text-[11px] font-mono font-semibold">MEDIUM</span>;
      default:
        return <span className="bg-[#E2E0D8] text-[#5A6258] px-2.5 py-0.5 rounded text-[11px] font-mono">LOW</span>;
    }
  };

  const activeRisks = risks.filter((_, idx) => !dismissedRiskIds.includes(`${idx}`));

  const filteredRisks = activeRisks.filter(r => {
    const matchesSearch = !searchQuery.trim() ||
      r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.ruleId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.affectedTaskTitle && r.affectedTaskTitle.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesSeverity = severityFilter === 'ALL' || r.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto select-none">
      {/* Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#292D28] tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-[#56664C]" />
            Deterministic Risk Radar
          </h2>
          <p className="text-sm text-[#78866B]">
            Automated analysis evaluating 6 deterministic mathematical rules without subjective score fabrication.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2.5">
          {projects.length > 0 && (
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  [{p.code}] {p.name}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={() => fetchRisks(selectedProjectId)}
            title="Refresh Findings"
            className="p-2 rounded-xl bg-[#FAFAF7] border border-[#E2E0D8] text-[#5A6258] hover:text-[#292D28] hover:bg-[#EFECE4] transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-[#56664C]' : ''}`} />
          </button>

          <button
            disabled={!selectedProjectId || evaluating}
            onClick={handleRunEvaluation}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 fill-current ${evaluating ? 'animate-spin' : ''}`} />
            <span>{evaluating ? 'Evaluating Rules...' : 'Run Risk Radar'}</span>
          </button>
        </div>
      </div>

      {/* Acknowledged alert */}
      {acknowledgedMsg && (
        <div className="p-3.5 rounded-xl bg-green-50 border border-green-200 text-green-800 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-green-600" />
            <span>{acknowledgedMsg}</span>
          </div>
          <button onClick={() => setAcknowledgedMsg(null)}>
            <X className="w-3.5 h-3.5 text-green-600" />
          </button>
        </div>
      )}

      {error && (
        <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs">
          {error}
        </div>
      )}

      {/* 6 Deterministic Rules Explanation Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { name: 'Overdue Task', id: 'OVERDUE_TASK' },
          { name: 'Deadline Approaching', id: 'DEADLINE_APPROACHING' },
          { name: 'Blocked Task', id: 'BLOCKED_TASK' },
          { name: 'Stalled Progress', id: 'STALLED_PROGRESS' },
          { name: 'Capacity Overload', id: 'CAPACITY_OVERLOAD' },
          { name: 'Project Deadline', id: 'PROJECT_DEADLINE_RISK' },
        ].map((rule) => {
          const matchCount = activeRisks.filter((r) => r.ruleId === rule.id).length;
          return (
            <div
              key={rule.id}
              className={`p-3 rounded-xl border text-left transition-colors ${
                matchCount > 0
                  ? 'bg-red-50/60 border-red-200 text-[#B7473C]'
                  : 'bg-[#FAFAF7] border-[#E2E0D8] text-[#5A6258]'
              }`}
            >
              <div className="text-[10px] uppercase font-semibold font-mono tracking-wider truncate">
                {rule.name}
              </div>
              <div className="text-lg font-bold mt-1 text-[#292D28]">{matchCount}</div>
            </div>
          );
        })}
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#FAFAF7] p-3 rounded-2xl border border-[#E2E0D8]">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#78866B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search risk rule, title, tasks..."
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
          />
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto overflow-x-auto">
          <span className="text-xs font-semibold text-[#78866B] flex items-center gap-1">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            Severity:
          </span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((s) => (
            <button
              key={s}
              onClick={() => setSeverityFilter(s)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                severityFilter === s
                  ? 'bg-[#56664C] text-white'
                  : 'bg-[#EFECE4] text-[#5A6258] hover:text-[#292D28]'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {filteredRisks.length === 0 ? (
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl p-12 text-center space-y-3 shadow-xs">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-[#56664C]/10 text-[#56664C] flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-[#292D28]">All Clear • No Active Risk Findings</h3>
            <p className="text-xs text-[#5A6258] max-w-md mx-auto">
              All tasks and milestones in this project comply with scheduled delivery timelines and dependency constraints.
            </p>
          </div>
        ) : (
          filteredRisks.map((finding, idx) => (
            <div
              key={idx}
              className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl p-6 shadow-xs hover:border-[#56664C] transition-all space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {getSeverityBadge(finding.severity)}
                    <span className="font-mono text-xs font-semibold text-[#78866B]">
                      {finding.ruleId}
                    </span>
                    {finding.affectedTaskTitle && (
                      <span className="text-xs font-bold text-[#292D28] bg-white px-2 py-0.5 rounded-md border border-[#E2E0D8]">
                        Task: {finding.affectedTaskTitle}
                      </span>
                    )}
                  </div>
                  <h3 className="text-base font-bold text-[#292D28]">{finding.title}</h3>
                </div>
                {finding.detectedAt && (
                  <span className="font-mono text-[11px] text-[#78866B]">
                    Detected: {new Date(finding.detectedAt).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                  </span>
                )}
              </div>

              <p className="text-xs text-[#5A6258] leading-relaxed">
                {finding.description}
              </p>

              {finding.recommendedAction && (
                <div className="p-3.5 bg-[#F4F2E9] rounded-xl border border-[#E2E0D8] flex items-start gap-2.5 text-xs">
                  <ArrowRight className="w-4 h-4 text-[#56664C] shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-[#292D28]">Recommended Action: </span>
                    <span className="text-[#5A6258]">{finding.recommendedAction}</span>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="pt-2 flex items-center justify-end gap-2 border-t border-[#E2E0D8]">
                <button
                  onClick={() => handleDismissRisk(idx, finding.title)}
                  className="px-3 py-1.5 rounded-xl border border-[#E2E0D8] bg-white hover:bg-[#EFECE4] text-xs font-semibold text-[#5A6258] transition-colors"
                >
                  Acknowledge & Mitigate
                </button>
                <button
                  onClick={() => navigate(`/tasks?projectId=${selectedProjectId}`)}
                  className="px-3.5 py-1.5 rounded-xl bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors flex items-center gap-1 shadow-xs"
                >
                  <span>Resolve in Task Explorer</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
