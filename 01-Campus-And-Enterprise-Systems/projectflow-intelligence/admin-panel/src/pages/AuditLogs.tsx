import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { AuditLog } from '../types';
import {
  Activity,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Search,
  Filter,
  Download,
  Eye,
  X,
  Shield,
  FileSpreadsheet
} from 'lucide-react';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [page, setPage] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [totalElements, setTotalElements] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [actionCategory, setActionCategory] = useState('ALL');

  // Inspect Modal
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);

  const fetchLogs = async (p: number) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await api.getAuditEvents(p, 25, searchQuery, actionCategory);
      setLogs(resp.content || []);
      setTotalPages(resp.totalPages || 1);
      setTotalElements(resp.totalElements || 0);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit logs');
      setLogs([]);
      setTotalElements(0);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs(page);
  }, [page, actionCategory]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0);
    fetchLogs(0);
  };

  const handleExportCSV = () => {
    if (logs.length === 0) return;
    const headers = ['Timestamp', 'Action', 'Target Entity', 'Entity ID', 'Actor Email', 'Details'];
    const rows = logs.map((l) => [
      `"${new Date(l.timestamp).toISOString()}"`,
      `"${l.action || ''}"`,
      `"${l.entityType || ''}"`,
      `"${l.entityId || ''}"`,
      `"${l.actorEmail || l.actorId || ''}"`,
      `"${(l.details || l.metadata || '').replace(/"/g, '""')}"`
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `ProjectFlow-AuditTrail-${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportJSON = () => {
    if (logs.length === 0) return;
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(logs, null, 2))}`;
    const link = document.createElement('a');
    link.setAttribute('href', jsonString);
    link.setAttribute('download', `ProjectFlow-AuditTrail-${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Title & Top Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#292D28] tracking-tight flex items-center gap-2.5">
            <Shield className="w-6 h-6 text-[#56664C]" />
            Security & Audit Trail
          </h2>
          <p className="text-sm text-[#78866B]">
            Cryptographically timestamped telemetry of system events, role escalations, and state mutations.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleExportCSV}
            disabled={logs.length === 0}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#FAFAF7] border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:text-[#292D28] hover:bg-[#EFECE4] transition-colors disabled:opacity-40"
            title="Download CSV report"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-700" />
            CSV
          </button>
          <button
            onClick={handleExportJSON}
            disabled={logs.length === 0}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#FAFAF7] border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:text-[#292D28] hover:bg-[#EFECE4] transition-colors disabled:opacity-40"
            title="Download raw JSON data"
          >
            <Download className="w-3.5 h-3.5 text-[#56664C]" />
            JSON
          </button>
          <button
            onClick={() => fetchLogs(page)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh Logs
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
          {error}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-[#78866B] absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by actor, action, entity, or payload..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs text-[#292D28] focus:outline-none focus:border-[#56664C] focus:ring-1 focus:ring-[#56664C]"
          />
        </form>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-[#5A6258] font-semibold">
            <Filter className="w-3.5 h-3.5 text-[#78866B]" />
            Action Domain:
            <select
              value={actionCategory}
              onChange={(e) => {
                setActionCategory(e.target.value);
                setPage(0);
              }}
              className="px-2.5 py-1.5 bg-white border border-[#E2E0D8] rounded-lg text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
            >
              <option value="ALL">All Actions</option>
              <option value="USER">User & Permissions</option>
              <option value="PROJECT">Projects</option>
              <option value="TASK">Tasks & Status</option>
              <option value="RELEASE">App Releases</option>
              <option value="BROADCAST">Push Broadcast</option>
              <option value="SETTINGS">System Settings</option>
              <option value="AUTH">Authentication</option>
            </select>
          </div>

          <div className="text-xs font-medium text-[#78866B] pl-2">
            {totalElements} total entries recorded
          </div>
        </div>
      </div>

      {/* Audit Table */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F4F2E9] border-b border-[#E2E0D8] text-[#5A6258] font-semibold uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3.5">Timestamp</th>
                <th className="px-6 py-3.5">Action Domain</th>
                <th className="px-6 py-3.5">Target Entity</th>
                <th className="px-6 py-3.5">Actor</th>
                <th className="px-6 py-3.5">Payload Preview</th>
                <th className="px-6 py-3.5 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E0D8] text-[#292D28]">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-[#5A6258]">
                    <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-[#E2E0D8] text-[#56664C] flex items-center justify-center">
                      <Activity className="w-5 h-5" />
                    </div>
                    No audit records found matching criteria.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-[#F4F2E9]/60 transition-colors">
                    <td className="px-6 py-4 font-mono text-[11px] text-[#78866B] whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-mono text-[11px] font-bold px-2 py-0.5 rounded bg-[#56664C]/10 text-[#56664C] border border-[#56664C]/20">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-[#292D28]">{log.entityType || 'SYSTEM'}</div>
                      {log.entityId && (
                        <div className="font-mono text-[10px] text-[#78866B] truncate max-w-xs">
                          {log.entityId}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 font-mono text-[11px] text-[#292D28]">
                      {log.actorEmail || log.actorId || 'system@projectflow.io'}
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-mono text-[10px] text-[#5A6258] bg-white px-2 py-1 rounded border border-[#E2E0D8] inline-block max-w-xs truncate">
                        {log.details || log.metadata || '{}'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => setSelectedLog(log)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-[#E2E0D8] bg-white hover:bg-[#EFECE4] text-[#56664C] font-semibold text-xs transition-colors"
                      >
                        <Eye className="w-3 h-3" />
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-6 py-4 border-t border-[#E2E0D8] flex items-center justify-between text-xs text-[#5A6258]">
          <div>
            Showing page <span className="font-semibold text-[#292D28]">{page + 1}</span> of{' '}
            <span className="font-semibold text-[#292D28]">{totalPages}</span> ({totalElements} total entries)
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              className="p-1.5 rounded-lg border border-[#E2E0D8] hover:bg-[#EFECE4] disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
              className="p-1.5 rounded-lg border border-[#E2E0D8] hover:bg-[#EFECE4] disabled:opacity-40"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Inspect Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl max-w-lg w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-[#292D28] flex items-center gap-2">
                <Activity className="w-4 h-4 text-[#56664C]" />
                Audit Event Inspector
              </h3>
              <button onClick={() => setSelectedLog(null)} className="text-[#5A6258] hover:text-[#292D28]">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3 p-3 bg-white border border-[#E2E0D8] rounded-lg">
                <div>
                  <span className="text-[#78866B] block">Event ID:</span>
                  <span className="font-mono font-semibold text-[#292D28] break-all">{selectedLog.id}</span>
                </div>
                <div>
                  <span className="text-[#78866B] block">Timestamp:</span>
                  <span className="font-mono text-[#292D28]">{new Date(selectedLog.timestamp).toISOString()}</span>
                </div>
                <div>
                  <span className="text-[#78866B] block">Action:</span>
                  <span className="font-mono font-bold text-[#56664C]">{selectedLog.action}</span>
                </div>
                <div>
                  <span className="text-[#78866B] block">Actor:</span>
                  <span className="font-mono text-[#292D28]">{selectedLog.actorEmail || selectedLog.actorId || 'SYSTEM'}</span>
                </div>
              </div>

              <div>
                <span className="text-[#78866B] font-semibold uppercase tracking-wider block mb-1">
                  Payload / Details
                </span>
                <pre className="p-3 bg-[#1C1917] text-emerald-400 rounded-lg font-mono text-[11px] overflow-x-auto max-h-60 leading-relaxed">
                  {(() => {
                    try {
                      const parsed = JSON.parse(selectedLog.details || selectedLog.metadata || '{}');
                      return JSON.stringify(parsed, null, 2);
                    } catch {
                      return selectedLog.details || selectedLog.metadata || 'No additional payload';
                    }
                  })()}
                </pre>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-1.5 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640]"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
