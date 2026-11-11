import React, { useState, useEffect } from 'react';
import { Settings, ShieldCheck, Database, FileText, ShieldAlert, Radio, Send, Camera, MapPin, Phone, Eye, X } from 'lucide-react';
import { api } from '../services/api';
import { getSocket } from '../services/socket';
import { SOSEvent, CitizenReport } from '../types';

const playAlertSound = () => {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.35);
    gain.gain.setValueAtTime(0.35, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.35);
  } catch {}
};

export const AdminDashboard: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [sosList, setSosList] = useState<SOSEvent[]>([]);
  const [reports, setReports] = useState<CitizenReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'sos' | 'reports' | 'alerts' | 'audit'>('sos');
  const [zoomImage, setZoomImage] = useState<string | null>(null);

  const [alertForm, setAlertForm] = useState({
    title: '',
    message: '',
    type: 'GENERAL',
    severity: 'WARNING',
    radiusKm: 25
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [logsRes, sosRes, repRes] = await Promise.all([
        api.getAuditLogs().catch(() => ({ success: true, data: [] })),
        api.getSOSList({ limit: '20' }).catch(() => ({ success: true, data: [] })),
        api.getReports().catch(() => ({ success: true, data: [] }))
      ]);

      if (logsRes.success) setLogs(logsRes.data || []);
      if (sosRes.success) setSosList(sosRes.data || []);
      if (repRes.success) setReports(repRes.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    const socket = getSocket();
    const handleNewSOS = (newSOS: SOSEvent) => {
      playAlertSound();
      setSosList((prev) => [newSOS, ...prev.filter((s) => s.eventId !== newSOS.eventId)]);
    };

    const handleNewReport = (newRep: CitizenReport) => {
      setReports((prev) => {
        if (prev.some((r) => r._id === newRep._id)) return prev;
        return [newRep, ...prev];
      });
    };

    socket.on('sos:new', handleNewSOS);
    socket.on('sos:alert', handleNewSOS);
    socket.on('report:new', handleNewReport);

    return () => {
      socket.off('sos:new', handleNewSOS);
      socket.off('sos:alert', handleNewSOS);
      socket.off('report:new', handleNewReport);
    };
  }, []);

  const handleBroadcastAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!alertForm.title || !alertForm.message) return;
    try {
      await api.createAlert(alertForm);
      setAlertForm({ title: '', message: '', type: 'GENERAL', severity: 'WARNING', radiusKm: 25 });
      alert('Official Emergency Alert broadcasted to all citizens and dashboards!');
    } catch {
      alert('Failed to broadcast alert');
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <Settings className="w-5 h-5 text-slate-700" />
            <span>Admin Command, Audit &amp; Citizen Incident Surveillance</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time SOS dispatch, Cloudinary incident surveillance, tamper-evident audit trail &amp; alert broadcasting
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex bg-slate-100 p-1 rounded-xl text-xs font-bold space-x-1">
          <button
            onClick={() => setActiveTab('sos')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'sos' ? 'bg-red-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Live SOS ({sosList.length})
          </button>
          <button
            onClick={() => setActiveTab('reports')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'reports' ? 'bg-orange-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Incident Photos ({reports.length})
          </button>
          <button
            onClick={() => setActiveTab('alerts')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'alerts' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Broadcast Alert
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'audit' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Audit Log ({logs.length})
          </button>
        </div>
      </div>

      {/* 1. Live SOS Stream */}
      {activeTab === 'sos' && (
        <div className="bg-white p-5 rounded-2xl border-2 border-red-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b pb-2">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-red-600 animate-ping"></span>
              <span>Real-Time Inbound SOS Dispatches (Admin Surveillance)</span>
            </h2>
            <span className="text-xs font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded-full border border-red-200">
              Auto-Refreshing via WebSockets
            </span>
          </div>

          {sosList.length === 0 ? (
            <p className="py-8 text-center text-slate-400 text-xs">No active emergency SOS recorded yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {sosList.map((sos) => (
                <div key={sos._id} className="p-4 rounded-xl border border-red-100 bg-red-50/40 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-red-700 uppercase tracking-wide flex items-center gap-1">
                      <ShieldAlert className="w-4 h-4 text-red-600" />
                      {sos.type} SOS
                    </span>
                    <span className="px-2 py-0.5 rounded bg-red-600 text-white font-bold text-[10px]">
                      {sos.severity}
                    </span>
                  </div>

                  <p className="text-slate-800 font-semibold">{sos.description || 'Emergency SOS signal triggered'}</p>

                  <div className="text-[11px] text-slate-600 space-y-1">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-red-500 shrink-0" />
                      <span className="truncate">{sos.addressText || `${sos.location?.coordinates?.[1]?.toFixed(4)}, ${sos.location?.coordinates?.[0]?.toFixed(4)}`}</span>
                    </div>
                    {sos.userPhone && (
                      <div className="flex items-center gap-1">
                        <Phone className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span>{sos.userPhone} ({sos.userName || 'Citizen'})</span>
                      </div>
                    )}
                  </div>

                  <div className="pt-2 border-t border-red-100 flex items-center justify-between text-[10px]">
                    <span className="text-slate-400">Status: <strong>{sos.status}</strong></span>
                    <span className="font-mono text-slate-500">{new Date(sos.createdAt).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 2. Citizen Incident Photos (Cloudinary) */}
      {activeTab === 'reports' && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b pb-2">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <Camera className="w-4 h-4 text-orange-600" />
              <span>Citizen Incident Reports &amp; Cloudinary Proof Stream</span>
            </h2>
            <span className="text-xs text-slate-500">{reports.length} Total Hazards Reported</span>
          </div>

          {reports.length === 0 ? (
            <p className="py-8 text-center text-slate-400 text-xs">No citizen reports submitted yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {reports.map((rep) => {
                const photoUrl = rep.images?.[0] || rep.mediaUrl;
                return (
                  <div key={rep._id} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-orange-700 uppercase tracking-wider">{rep.type}</span>
                      <span className="px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 font-bold text-[10px]">
                        {rep.verificationStatus}
                      </span>
                    </div>

                    <p className="text-slate-800 line-clamp-2">{rep.description}</p>

                    {/* Cloudinary Image Thumbnail */}
                    {photoUrl ? (
                      <div className="relative group rounded-xl overflow-hidden border border-slate-200 bg-black/5 aspect-video flex items-center justify-center">
                        <img
                          src={photoUrl}
                          alt="Incident verification"
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                        <button
                          type="button"
                          onClick={() => setZoomImage(photoUrl)}
                          className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white gap-1 font-bold text-xs"
                        >
                          <Eye className="w-4 h-4" />
                          <span>Inspect Photo</span>
                        </button>
                      </div>
                    ) : (
                      <div className="p-3 bg-slate-100 rounded-xl text-center text-slate-400 text-[11px]">
                        No image attached
                      </div>
                    )}

                    <div className="pt-2 border-t border-slate-200 text-[10px] text-slate-500 flex justify-between">
                      <span>Reporter: {rep.userName || 'Anonymous Citizen'}</span>
                      <span>{new Date(rep.createdAt).toLocaleTimeString()}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* 3. Broadcast Alert Tab */}
      {activeTab === 'alerts' && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm max-w-xl mx-auto space-y-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
            <Radio className="w-4 h-4 text-indigo-600" />
            <span>Broadcast Official Emergency Alert to Citizens</span>
          </h2>
          <form onSubmit={handleBroadcastAlert} className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-700 font-bold mb-1">Alert Title</label>
              <input
                type="text"
                required
                placeholder="e.g. Flash Flood Alert for Sabarmati River Basin"
                value={alertForm.title}
                onChange={(e) => setAlertForm({ ...alertForm, title: e.target.value })}
                className="w-full border rounded-xl p-2.5"
              />
            </div>
            <div>
              <label className="block text-slate-700 font-bold mb-1">Alert Details &amp; Instructions</label>
              <textarea
                required
                rows={4}
                placeholder="Immediate evacuation advisory and designated assembly points..."
                value={alertForm.message}
                onChange={(e) => setAlertForm({ ...alertForm, message: e.target.value })}
                className="w-full border rounded-xl p-2.5 resize-none"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-700 font-bold mb-1">Alert Severity</label>
                <select
                  value={alertForm.severity}
                  onChange={(e) => setAlertForm({ ...alertForm, severity: e.target.value })}
                  className="w-full border rounded-xl p-2"
                >
                  <option value="WARNING">Warning</option>
                  <option value="CRITICAL">Critical / Life Threat</option>
                  <option value="ADVISORY">Advisory</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-700 font-bold mb-1">Radius (km)</label>
                <input
                  type="number"
                  value={alertForm.radiusKm}
                  onChange={(e) => setAlertForm({ ...alertForm, radiusKm: Number(e.target.value) })}
                  className="w-full border rounded-xl p-2"
                />
              </div>
            </div>
            <button
              type="submit"
              className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl shadow-md shadow-red-200 flex items-center justify-center space-x-2"
            >
              <Send className="w-4 h-4" />
              <span>Broadcast Alert to All Citizen Apps</span>
            </button>
          </form>
        </div>
      )}

      {/* 4. Audit Log */}
      {activeTab === 'audit' && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b pb-2">
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
              <FileText className="w-4 h-4 text-slate-600" />
              <span>Security Audit Trail Log</span>
            </h2>
            <span className="text-xs text-slate-500">{logs.length} logged records</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase text-[10px] border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3">Entity</th>
                  <th className="py-2.5 px-3">User / Device</th>
                  <th className="py-2.5 px-3">IP Address</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-400 font-sans">
                      No audit records recorded yet.
                    </td>
                  </tr>
                ) : (
                  logs.map((l, i) => (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="py-2 px-3 text-slate-500">{new Date(l.timestamp).toLocaleTimeString()}</td>
                      <td className="py-2 px-3 font-bold text-slate-900">{l.action}</td>
                      <td className="py-2 px-3 text-slate-600">{l.entityType} ({l.entityId?.substring(0, 8) || '-'})</td>
                      <td className="py-2 px-3 text-slate-700">{l.userName || l.deviceId || 'System'}</td>
                      <td className="py-2 px-3 text-slate-400">{l.ipAddress || '127.0.0.1'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Cloudinary Lightbox Zoom Modal */}
      {zoomImage && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-[2000] animate-in fade-in">
          <div className="relative max-w-3xl w-full bg-slate-900 rounded-3xl p-3 border border-slate-700 shadow-2xl">
            <button
              onClick={() => setZoomImage(null)}
              className="absolute top-4 right-4 p-2 bg-black/60 hover:bg-black/90 text-white rounded-full z-10"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="max-h-[80vh] overflow-hidden rounded-2xl flex items-center justify-center">
              <img src={zoomImage} alt="Zoomed Incident" className="max-w-full max-h-[75vh] object-contain" />
            </div>
            <p className="text-center text-xs text-slate-400 mt-2">Cloudinary Verified Disaster Incident Photo</p>
          </div>
        </div>
      )}
    </div>
  );
};
