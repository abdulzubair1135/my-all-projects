import React, { useState } from 'react';
import { X, CheckCircle2, ShieldAlert, Radio, User, Phone, MapPin, Users, HeartPulse, Send, AlertTriangle } from 'lucide-react';
import { SOSEvent, RescueTeam } from '../types';
import { api } from '../services/api';

interface SOSTriageModalProps {
  sos: SOSEvent;
  rescueTeams: RescueTeam[];
  onClose: () => void;
  onUpdate: () => void;
}

export const SOSTriageModal: React.FC<SOSTriageModalProps> = ({ sos, rescueTeams, onClose, onUpdate }) => {
  const [selectedTeam, setSelectedTeam] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const [lng, lat] = sos.location?.coordinates || [0, 0];

  const handleVerify = async () => {
    setLoading(true);
    try {
      await api.verifySOS(sos.eventId);
      onUpdate();
    } catch (err) {
      alert('Failed to verify SOS');
    } finally {
      setLoading(false);
    }
  };

  const handleAssign = async () => {
    if (!selectedTeam) {
      alert('Please select a rescue team first.');
      return;
    }
    setLoading(true);
    try {
      await api.assignRescueTeam(sos.eventId, selectedTeam, notes);
      onUpdate();
    } catch (err) {
      alert('Failed to assign team');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    setLoading(true);
    try {
      await api.updateSOSStatus(sos.eventId, newStatus, notes);
      onUpdate();
    } catch (err) {
      alert(`Failed to update status to ${newStatus}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full shadow-2xl overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className={`px-6 py-4 flex items-center justify-between text-white ${
          sos.severity === 'CRITICAL' ? 'bg-red-600' : sos.severity === 'HIGH' ? 'bg-amber-600' : 'bg-slate-800'
        }`}>
          <div className="flex items-center space-x-3">
            <ShieldAlert className="w-6 h-6 animate-pulse" />
            <div>
              <h2 className="font-bold text-lg">{sos.type} EMERGENCY SOS</h2>
              <p className="text-xs opacity-90 font-mono">Event ID: {sos.eventId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-full hover:bg-white/20 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          {/* Source Banner */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2">
              <Radio className="w-4 h-4 text-purple-600" />
              <span className="text-xs font-semibold text-slate-700">Network Transport Source:</span>
              <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                sos.source === 'ONLINE' ? 'bg-emerald-100 text-emerald-800' : 'bg-purple-100 text-purple-800'
              }`}>
                {sos.source}
              </span>
            </div>
            {sos.hopCount > 0 && (
              <span className="text-xs text-slate-500 font-mono">
                Hops: <strong>{sos.hopCount}</strong> | Relayed: {sos.relayPath?.join(' ➔ ') || 'N/A'}
              </span>
            )}
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-2">
              <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Victim & Caller</div>
              <div className="flex items-center space-x-2 text-sm text-slate-800 font-medium">
                <User className="w-4 h-4 text-slate-400" />
                <span>{sos.userName || 'Citizen / Anonymous'}</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-slate-800 font-medium">
                <Phone className="w-4 h-4 text-slate-400" />
                <span>{sos.userPhone || 'Not available'}</span>
              </div>
              <div className="text-xs text-slate-500 font-mono">Origin Device: {sos.originDeviceId}</div>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-2">
              <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Casualties & Scale</div>
              <div className="flex items-center space-x-2 text-sm text-slate-800 font-medium">
                <Users className="w-4 h-4 text-blue-500" />
                <span><strong>{sos.peopleCount}</strong> Total People Trapped / Affected</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-red-600 font-medium">
                <HeartPulse className="w-4 h-4 text-red-500" />
                <span><strong>{sos.injuredCount}</strong> Critical / Injured</span>
              </div>
              <div className="text-xs text-slate-500">
                Created: {new Date(sos.createdAt).toLocaleTimeString()} ({new Date(sos.createdAt).toLocaleDateString()})
              </div>
            </div>
          </div>

          {/* GPS Coordinates */}
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
              <MapPin className="w-4 h-4 text-red-500" />
              <span>Real GPS Geolocation</span>
            </div>
            <div className="flex items-center justify-between text-sm font-mono text-slate-800">
              <span>Lat: {lat.toFixed(6)} | Lng: {lng.toFixed(6)}</span>
              <span className="text-xs text-slate-500">Accuracy: ±{sos.locationAccuracy || 10}m</span>
            </div>
            {sos.addressText && (
              <p className="text-xs text-slate-600 mt-1">{sos.addressText}</p>
            )}
          </div>

          {/* Description */}
          {sos.description && (
            <div className="p-3 bg-amber-50/70 border border-amber-200/80 rounded-xl text-xs text-amber-900 leading-relaxed">
              <div className="font-bold mb-1 flex items-center space-x-1">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-700" />
                <span>Victim Situation Description:</span>
              </div>
              &ldquo;{sos.description}&rdquo;
            </div>
          )}

          {/* Current Status Tracker */}
          <div>
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Live Incident Status</div>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-slate-900 text-white rounded-lg text-xs font-bold font-mono">
                {sos.status}
              </span>
              {sos.status === 'RECEIVED' && (
                <button
                  onClick={handleVerify}
                  disabled={loading}
                  className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition flex items-center space-x-1"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Verify Incident</span>
                </button>
              )}
            </div>
          </div>

          {/* Assignment Section */}
          <div className="p-4 bg-slate-100 rounded-xl border border-slate-200 space-y-3">
            <div className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-2">
              <Radio className="w-4 h-4 text-indigo-600" />
              <span>Dispatch Rescue Response Unit</span>
            </div>

            {sos.assignedTeamName ? (
              <div className="text-xs text-emerald-800 font-semibold bg-emerald-100/80 p-2.5 rounded-lg">
                Assigned to: <strong>{sos.assignedTeamName}</strong>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <select
                  value={selectedTeam}
                  onChange={(e) => setSelectedTeam(e.target.value)}
                  className="flex-1 bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">-- Select Available Rescue Unit --</option>
                  {rescueTeams.map((t) => (
                    <option key={t._id} value={t._id}>
                      {t.name} ({t.teamType}) — Status: {t.status}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleAssign}
                  disabled={loading || !selectedTeam}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-xs font-bold transition flex items-center space-x-1"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Dispatch</span>
                </button>
              </div>
            )}

            {/* Quick Status Override */}
            <div className="pt-2 border-t border-slate-200 flex flex-wrap gap-2">
              <span className="text-[11px] text-slate-500 self-center">Progress:</span>
              {['ACCEPTED', 'EN_ROUTE', 'ARRIVED', 'RESOLVED'].map((st) => (
                <button
                  key={st}
                  onClick={() => handleStatusChange(st)}
                  disabled={loading || sos.status === st}
                  className={`px-2.5 py-1 rounded text-[11px] font-bold transition ${
                    sos.status === st
                      ? 'bg-slate-800 text-white cursor-default'
                      : 'bg-white hover:bg-slate-200 text-slate-700 border border-slate-300'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-xs font-semibold transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
