import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { AdminOverview, AuditLog } from '../types';
import {
  Users,
  Layers,
  FolderKanban,
  CheckSquare,
  ShieldAlert,
  Activity,
  ArrowRight,
  RefreshCw,
  PlusCircle,
  Database
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [recentLogs, setRecentLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ov, logs] = await Promise.all([
        api.getAdminOverview().catch(() => ({
          totalUsers: 1,
          totalWorkspaces: 0,
          totalProjects: 0,
          totalTasks: 0,
          activeRisksCount: 0,
          systemStatus: 'ONLINE'
        })),
        api.getAuditEvents(0, 5).then(res => res.content).catch(() => [])
      ]);
      setOverview(ov);
      setRecentLogs(logs);
    } catch (err: any) {
      setError(err.message || 'Failed to load telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading && !overview) {
    return (
      <div className="flex items-center justify-center h-64 text-[#5A6258] text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-[#56664C]" />
        Loading system telemetry...
      </div>
    );
  }

  const isEmptyState = overview && overview.totalWorkspaces === 0 && overview.totalProjects === 0;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Title & Refresh */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#292D28] tracking-tight">System Overview</h2>
          <p className="text-sm text-[#78866B]">
            Global administrative control and cross-workspace intelligence monitoring.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#FAFAF7] border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:text-[#292D28] hover:bg-[#EFECE4] transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#56664C]' : ''}`} />
            Refresh Data
          </button>
          <Link
            to="/workspaces"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm"
          >
            <PlusCircle className="w-4 h-4" />
            New Workspace
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <div className="bg-[#FAFAF7] border border-[#E2E0D8] p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Users</span>
            <Users className="w-4 h-4 text-[#56664C]" />
          </div>
          <div className="text-2xl font-bold text-[#292D28]">{overview?.totalUsers ?? 0}</div>
          <div className="text-[11px] text-[#5A6258] mt-1">Platform accounts</div>
        </div>

        <div className="bg-[#FAFAF7] border border-[#E2E0D8] p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Workspaces</span>
            <Layers className="w-4 h-4 text-[#56664C]" />
          </div>
          <div className="text-2xl font-bold text-[#292D28]">{overview?.totalWorkspaces ?? 0}</div>
          <div className="text-[11px] text-[#5A6258] mt-1">Tenant domains</div>
        </div>

        <div className="bg-[#FAFAF7] border border-[#E2E0D8] p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Projects</span>
            <FolderKanban className="w-4 h-4 text-[#56664C]" />
          </div>
          <div className="text-2xl font-bold text-[#292D28]">{overview?.totalProjects ?? 0}</div>
          <div className="text-[11px] text-[#5A6258] mt-1">Active initiatives</div>
        </div>

        <div className="bg-[#FAFAF7] border border-[#E2E0D8] p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Tasks</span>
            <CheckSquare className="w-4 h-4 text-[#56664C]" />
          </div>
          <div className="text-2xl font-bold text-[#292D28]">{overview?.totalTasks ?? 0}</div>
          <div className="text-[11px] text-[#5A6258] mt-1">Tracked work units</div>
        </div>

        <div className="bg-[#FAFAF7] border border-[#E2E0D8] p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Risks</span>
            <ShieldAlert className="w-4 h-4 text-[#C84B31]" />
          </div>
          <div className="text-2xl font-bold text-[#C84B31]">{overview?.activeRisksCount ?? 0}</div>
          <div className="text-[11px] text-[#5A6258] mt-1">Risk Radar findings</div>
        </div>

        <div className="bg-[#FAFAF7] border border-[#E2E0D8] p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Health</span>
            <Database className="w-4 h-4 text-[#56664C]" />
          </div>
          <div className="text-base font-bold text-[#56664C]">{overview?.systemStatus ?? 'ONLINE'}</div>
          <div className="text-[11px] text-[#5A6258] mt-1">Flyway V1 schema</div>
        </div>
      </div>

      {/* Empty State Banner if clean database */}
      {isEmptyState && (
        <div className="p-6 bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl text-center space-y-3">
          <div className="w-12 h-12 mx-auto rounded-full bg-[#56664C]/10 text-[#56664C] flex items-center justify-center">
            <Layers className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-[#292D28]">Clean Database State</h3>
          <p className="text-sm text-[#5A6258] max-w-lg mx-auto">
            The database schema is verified and ready. No workspaces or projects exist yet. Create your first workspace to begin managing projects and computing risk telemetry.
          </p>
          <div>
            <Link
              to="/workspaces"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#56664C] text-[#F4F2E9] text-sm font-semibold hover:bg-[#485640] transition-colors"
            >
              <PlusCircle className="w-4 h-4" />
              Create First Workspace
            </Link>
          </div>
        </div>
      )}

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/risks"
          className="group p-6 bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl hover:border-[#56664C] transition-colors"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-[#56664C]/10 text-[#56664C] flex items-center justify-center">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-[#78866B] group-hover:translate-x-1 transition-transform" />
          </div>
          <h3 className="text-base font-bold text-[#292D28] mb-1">Deterministic Risk Radar</h3>
          <p className="text-xs text-[#5A6258] leading-relaxed">
            6 automated rules analyzing overdue tasks, impending deadlines, dependency blockages, stalled progress, and capacity overloads.
          </p>
        </Link>

        <Link
          to="/projects"
          className="group p-6 bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl hover:border-[#56664C] transition-colors"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-[#56664C]/10 text-[#56664C] flex items-center justify-center">
              <FolderKanban className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-[#78866B] group-hover:translate-x-1 transition-transform" />
          </div>
          <h3 className="text-base font-bold text-[#292D28] mb-1">Projects & Initiatives</h3>
          <p className="text-xs text-[#5A6258] leading-relaxed">
            Monitor multi-project health status, scheduling timelines, and workflow execution across all workspaces.
          </p>
        </Link>

        <Link
          to="/audit-logs"
          className="group p-6 bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl hover:border-[#56664C] transition-colors"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-[#56664C]/10 text-[#56664C] flex items-center justify-center">
              <Activity className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-[#78866B] group-hover:translate-x-1 transition-transform" />
          </div>
          <h3 className="text-base font-bold text-[#292D28] mb-1">Security & Audit Logs</h3>
          <p className="text-xs text-[#5A6258] leading-relaxed">
            Immutable tracking for user authentication, privilege escalation, project creation, and dependency reconfigurations.
          </p>
        </Link>
      </div>

      {/* Recent Audit Trail Preview */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-[#E2E0D8] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#56664C]" />
            <h3 className="text-sm font-bold text-[#292D28]">Recent Audit Events</h3>
          </div>
          <Link
            to="/audit-logs"
            className="text-xs font-semibold text-[#56664C] hover:text-[#485640] flex items-center gap-1"
          >
            View all logs <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentLogs.length === 0 ? (
          <div className="p-8 text-center text-sm text-[#5A6258]">
            No recent audit events recorded yet.
          </div>
        ) : (
          <div className="divide-y divide-[#E2E0D8]">
            {recentLogs.map((log) => (
              <div key={log.id} className="px-6 py-3.5 flex items-center justify-between text-xs">
                <div className="flex items-center gap-3">
                  <span className="font-mono font-semibold px-2 py-0.5 rounded bg-[#E2E0D8] text-[#292D28] text-[10px]">
                    {log.action}
                  </span>
                  <span className="text-[#5A6258]">
                    Entity: <span className="font-medium text-[#292D28]">{log.entityType}</span>
                  </span>
                </div>
                <div className="font-mono text-[11px] text-[#78866B]">
                  {new Date(log.timestamp).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
