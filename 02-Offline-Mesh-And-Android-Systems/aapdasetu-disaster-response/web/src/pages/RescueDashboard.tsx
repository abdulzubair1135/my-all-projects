import React, { useState, useEffect } from 'react';
import { Radio, MapPin, Users, HeartPulse, Navigation, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { SOSEvent, RescueTeam } from '../types';
import { api } from '../services/api';
import { getSocket } from '../services/socket';

export const RescueDashboard: React.FC = () => {
  const [assignedList, setAssignedList] = useState<SOSEvent[]>([]);
  const [teams, setTeams] = useState<RescueTeam[]>([]);
  const [selectedTeamId, setSelectedTeamId] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sosRes, teamsRes] = await Promise.all([
        api.getSOSList({ status: '' }),
        api.getRescueTeams()
      ]);

      if (teamsRes.success && teamsRes.data?.length > 0) {
        setTeams(teamsRes.data);
        if (!selectedTeamId) setSelectedTeamId(teamsRes.data[0]._id);
      }

      if (sosRes.success) {
        const relevant = (sosRes.data as SOSEvent[]).filter(
          (s) => ['ASSIGNED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED'].includes(s.status)
        );
        setAssignedList(relevant);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    const socket = getSocket();
    const handleUpdate = () => loadData();

    socket.on('sos:assigned', handleUpdate);
    socket.on('sos:status_changed', handleUpdate);
    socket.on('sos:new', handleUpdate);

    return () => {
      socket.off('sos:assigned', handleUpdate);
      socket.off('sos:status_changed', handleUpdate);
      socket.off('sos:new', handleUpdate);
    };
  }, [selectedTeamId]);

  const updateStatus = async (eventId: string, newStatus: string) => {
    try {
      await api.updateSOSStatus(eventId, newStatus);
      loadData();
    } catch (err) {
      alert('Failed to update status');
    }
  };

  const currentTeam = teams.find((t) => t._id === selectedTeamId) || teams[0];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header with Team Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <Radio className="w-5 h-5 text-indigo-600 animate-pulse" />
            <span>Rescue Field Operations Terminal</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Tactical dispatch terminal for NDRF, SDRF, and Emergency Response Units
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <label className="text-xs font-bold text-slate-600">Active Unit:</label>
          <select
            value={selectedTeamId}
            onChange={(e) => setSelectedTeamId(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {teams.map((t) => (
              <option key={t._id} value={t._id}>
                {t.name} ({t.teamType})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Team Status Card */}
      {currentTeam && (
        <div className="p-4 bg-indigo-50/70 border border-indigo-100 rounded-2xl flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">
              {currentTeam.teamType.substring(0, 3)}
            </div>
            <div>
              <div className="font-bold text-sm text-indigo-950">{currentTeam.name}</div>
              <div className="text-xs text-indigo-700">Vehicle: {currentTeam.vehicle} • Personnel: {currentTeam.membersCount} crew</div>
            </div>
          </div>

          <div className="flex items-center space-x-4 text-xs font-semibold">
            <div>
              <span className="text-slate-500 mr-1">Status:</span>
              <span className="px-2.5 py-1 rounded-full bg-indigo-600 text-white font-mono text-[11px]">
                {currentTeam.status}
              </span>
            </div>
            <div>
              <span className="text-slate-500 mr-1">Emergency Dispatch:</span>
              <span className="text-slate-800">{currentTeam.contactNumber}</span>
            </div>
          </div>
        </div>
      )}

      {/* Active Assignments Feed */}
      <div className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700">
          Dispatched Incident Queue ({assignedList.length} active)
        </h2>

        {assignedList.length === 0 ? (
          <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 text-slate-400">
            <CheckCircle2 className="w-12 h-12 mx-auto text-emerald-500 mb-2" />
            <h3 className="font-bold text-slate-700 text-base">No pending rescue dispatches</h3>
            <p className="text-xs text-slate-500 mt-1">All assigned incidents are resolved or currently standby.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {assignedList.map((sos) => {
              const [lng, lat] = sos.location?.coordinates || [0, 0];
              const navUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;

              return (
                <div
                  key={sos.eventId}
                  className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col justify-between"
                >
                  <div className="p-5 space-y-3">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="w-3 h-3 rounded-full bg-red-600 animate-ping" />
                        <span className="font-bold text-sm text-slate-900">{sos.type} EMERGENCY</span>
                      </div>
                      <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                        sos.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                      }`}>
                        {sos.severity}
                      </span>
                    </div>

                    {/* Stats & Victim */}
                    <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-3 rounded-xl">
                      <div className="flex items-center space-x-2 text-slate-700">
                        <Users className="w-4 h-4 text-blue-500" />
                        <span><strong>{sos.peopleCount}</strong> People Affected</span>
                      </div>
                      <div className="flex items-center space-x-2 text-red-600">
                        <HeartPulse className="w-4 h-4 text-red-500" />
                        <span><strong>{sos.injuredCount}</strong> Injured</span>
                      </div>
                    </div>

                    {/* Description */}
                    {sos.description && (
                      <p className="text-xs text-slate-600 italic bg-amber-50/70 p-2.5 rounded-xl border border-amber-200/50">
                        &ldquo;{sos.description}&rdquo;
                      </p>
                    )}

                    {/* GPS Coordinates & Navigation */}
                    <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                      <div className="flex items-center space-x-1.5 text-xs text-slate-600 font-mono">
                        <MapPin className="w-4 h-4 text-red-500" />
                        <span>{lat.toFixed(5)}, {lng.toFixed(5)}</span>
                      </div>
                      <a
                        href={navUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="px-3 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-xs font-bold transition flex items-center space-x-1"
                      >
                        <Navigation className="w-3.5 h-3.5" />
                        <span>Navigate</span>
                      </a>
                    </div>
                  </div>

                  {/* Operational Progression Buttons */}
                  <div className="bg-slate-50 p-3 border-t border-slate-200 flex items-center justify-between gap-2">
                    <span className="text-[11px] font-bold text-slate-500 uppercase">Stage: {sos.status}</span>
                    <div className="flex items-center space-x-1.5">
                      {sos.status === 'ASSIGNED' && (
                        <button
                          onClick={() => updateStatus(sos.eventId, 'ACCEPTED')}
                          className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition"
                        >
                          Accept
                        </button>
                      )}
                      {(sos.status === 'ASSIGNED' || sos.status === 'ACCEPTED') && (
                        <button
                          onClick={() => updateStatus(sos.eventId, 'EN_ROUTE')}
                          className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-bold transition"
                        >
                          En Route
                        </button>
                      )}
                      {sos.status === 'EN_ROUTE' && (
                        <button
                          onClick={() => updateStatus(sos.eventId, 'ARRIVED')}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition"
                        >
                          Arrived On Scene
                        </button>
                      )}
                      {sos.status === 'ARRIVED' && (
                        <button
                          onClick={() => updateStatus(sos.eventId, 'RESOLVED')}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition flex items-center space-x-1"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Mark Resolved</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
