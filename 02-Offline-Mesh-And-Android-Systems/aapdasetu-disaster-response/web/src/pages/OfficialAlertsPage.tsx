import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Radio,
  MapPin,
  ShieldAlert,
  Flame,
  Waves,
  Wind,
  Plus,
  Clock,
  Send,
  X,
  RefreshCw,
  BellRing
} from 'lucide-react';
import { api } from '../services/api';
import { getSocket } from '../services/socket';
import { Alert, SOSEvent, RescueTeam, Shelter, Hospital, CitizenReport } from '../types';
import { LiveMap } from '../components/LiveMap';

export const OfficialAlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [isMarkingZone, setIsMarkingZone] = useState(false);
  const [previewZone, setPreviewZone] = useState<{ lat: number; lng: number; radiusKm: number } | null>(null);

  // Background map layers
  const [sosList, setSosList] = useState<SOSEvent[]>([]);
  const [rescueTeams, setRescueTeams] = useState<RescueTeam[]>([]);
  const [shelters, setShelters] = useState<Shelter[]>([]);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [reports, setReports] = useState<CitizenReport[]>([]);

  // Alert Form
  const [alertForm, setAlertForm] = useState({
    title: '',
    message: '',
    type: 'FLOOD',
    severity: 'CRITICAL',
    area: 'Sabarmati Riverfront Promenade',
    latitude: 23.0225,
    longitude: 72.5714,
    radiusKm: 15
  });

  const loadAlertsAndMapData = async () => {
    try {
      setLoading(true);
      const [alertRes, sosRes, teamsRes, sheltersRes, hospRes, repRes] = await Promise.all([
        api.getAlerts(),
        api.getSOSList({ limit: '50' }),
        api.getRescueTeams(),
        api.getShelters(),
        api.getHospitals(),
        api.getReports()
      ]);

      if (alertRes.success) setAlerts(alertRes.data || []);
      if (sosRes.success) setSosList(sosRes.data || []);
      if (teamsRes.success) setRescueTeams(teamsRes.data || []);
      if (sheltersRes.success) setShelters(sheltersRes.data || []);
      if (hospRes.success) setHospitals(hospRes.data || []);
      if (repRes.success) setReports(repRes.data || []);
    } catch (err) {
      console.error('Failed to load official alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlertsAndMapData();

    const socket = getSocket();
    const handleNewAlert = (newAlert: Alert) => {
      setAlerts((prev) => [newAlert, ...prev.filter((a) => a._id !== newAlert._id)]);
    };

    socket.on('alert:new', handleNewAlert);
    socket.on('alert:broadcast', handleNewAlert);

    return () => {
      socket.off('alert:new', handleNewAlert);
      socket.off('alert:broadcast', handleNewAlert);
    };
  }, []);

  const handleMapClick = (lat: number, lng: number) => {
    setAlertForm((prev) => ({
      ...prev,
      latitude: lat,
      longitude: lng,
      area: `Ahmedabad Grid Sector (${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E)`
    }));
    setPreviewZone({ lat, lng, radiusKm: alertForm.radiusKm });
    setIsMarkingZone(false);
    setShowAlertModal(true);
  };

  const handlePublishAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!alertForm.title || !alertForm.message) return;

    try {
      const res = await api.createAlert({
        title: alertForm.title,
        message: alertForm.message,
        type: alertForm.type,
        severity: alertForm.severity,
        latitude: alertForm.latitude,
        longitude: alertForm.longitude,
        radiusKm: alertForm.radiusKm,
        source: 'STATE_GOVERNMENT_EOC'
      });

      if (res.success) {
        setShowAlertModal(false);
        setPreviewZone(null);
        setAlertForm({
          title: '',
          message: '',
          type: 'FLOOD',
          severity: 'CRITICAL',
          area: 'Sabarmati Riverfront Promenade',
          latitude: 23.0225,
          longitude: 72.5714,
          radiusKm: 15
        });
        loadAlertsAndMapData();
      }
    } catch (err) {
      console.error('Failed to broadcast alert:', err);
    }
  };

  const activeCount = alerts.filter((a) => a.active).length;
  const criticalCount = alerts.filter((a) => a.active && (a.severity === 'CRITICAL' || a.severity === 'EXTREME')).length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl text-white flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 rounded-full bg-red-600/20 text-red-400 border border-red-500/30 text-[10px] font-black uppercase tracking-wider">
              OFFICIAL BROADCAST SYSTEM
            </span>
            <span className="text-xs text-slate-400 font-mono">Gujarat SEOC &bull; NDMA Grid</span>
          </div>
          <h1 className="text-2xl font-black mt-2 tracking-tight flex items-center gap-2">
            <Radio className="w-6 h-6 text-red-500 animate-pulse" />
            Official Hazard &amp; Danger Zone Command
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Authorize state-wide disaster alerts, pinpoint hazard epicenters directly on the map, and push emergency evacuation warnings to all citizen smartphones and relief teams.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => setIsMarkingZone(!isMarkingZone)}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 shadow-lg ${
              isMarkingZone
                ? 'bg-amber-500 hover:bg-amber-600 text-slate-950 ring-4 ring-amber-400/30 animate-pulse'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
            }`}
          >
            <MapPin className="w-4 h-4 text-red-400" />
            <span>{isMarkingZone ? '📍 Click Map to Place Pin' : 'Mark Zone on Map'}</span>
          </button>

          <button
            onClick={() => {
              setPreviewZone(null);
              setShowAlertModal(true);
            }}
            className="px-4 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold rounded-xl text-xs flex items-center space-x-2 shadow-lg shadow-red-600/30 active:scale-95 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Issue Hazard Alert</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-bold uppercase text-slate-400 tracking-wider">Active Alerts</div>
            <div className="text-2xl font-black text-slate-800 mt-0.5">{activeCount}</div>
            <div className="text-[11px] text-slate-500">Live Danger Zones</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-red-50 text-red-600 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-bold uppercase text-slate-400 tracking-wider">Critical Sirens</div>
            <div className="text-2xl font-black text-red-600 mt-0.5">{criticalCount}</div>
            <div className="text-[11px] text-red-500 font-semibold">Immediate Action</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-red-50 text-red-600 flex items-center justify-center">
            <BellRing className="w-5 h-5 animate-bounce" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-bold uppercase text-slate-400 tracking-wider">Warning Radius</div>
            <div className="text-2xl font-black text-indigo-600 mt-0.5">25 km</div>
            <div className="text-[11px] text-slate-500">Max Grid Coverage</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-bold uppercase text-slate-400 tracking-wider">Sync Pipeline</div>
            <div className="text-2xl font-black text-emerald-600 mt-0.5">ACTIVE</div>
            <div className="text-[11px] text-emerald-600 font-semibold">Mobile App Sync 100%</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <Radio className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Map & Live Danger Zones */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-red-600" />
              State Hazard Geospatial Map (Interactive Danger Zones)
            </h2>
            <p className="text-xs text-slate-500">
              {isMarkingZone
                ? '🎯 Click anywhere on the map to define the exact center point for an emergency danger zone.'
                : 'Pulsating dashed circles indicate active government hazard zones synced in real-time to citizen apps.'}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={loadAlertsAndMapData}
              className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 text-xs font-semibold hover:bg-slate-50 flex items-center space-x-1"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh Map</span>
            </button>
          </div>
        </div>

        <div className="h-[460px] rounded-xl overflow-hidden relative">
          <LiveMap
            sosList={sosList}
            rescueTeams={rescueTeams}
            shelters={shelters}
            hospitals={hospitals}
            reports={reports}
            alerts={alerts}
            isMarkingDangerZone={isMarkingZone}
            onMapClick={handleMapClick}
            previewDangerZone={previewZone}
          />
        </div>
      </div>

      {/* Active Broadcasts Feed */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
          <h3 className="text-base font-black text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-600" />
            Active Official Advisories ({alerts.length})
          </h3>
          <span className="text-xs text-slate-400 font-mono">Auto-synced with Android App</span>
        </div>

        {alerts.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-sm">
            <p>No active hazard alerts recorded. The jurisdiction is currently safe.</p>
            <button
              onClick={() => setShowAlertModal(true)}
              className="mt-3 px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 font-bold rounded-xl text-xs inline-flex items-center space-x-1.5 transition"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Broadcast First Alert</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {alerts.map((al) => {
              const isCrit = al.severity === 'CRITICAL' || al.severity === 'EXTREME';
              return (
                <div
                  key={al._id}
                  className={`p-4 rounded-xl border transition-all ${
                    isCrit
                      ? 'bg-red-50/50 border-red-300 ring-1 ring-red-200'
                      : 'bg-amber-50/40 border-amber-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${
                          isCrit ? 'bg-red-600 text-white' : 'bg-amber-500 text-white'
                        }`}
                      >
                        {al.severity}
                      </span>
                      <span className="text-[11px] font-bold text-slate-600 uppercase flex items-center gap-1">
                        {al.type === 'FLOOD' && <Waves className="w-3.5 h-3.5 text-blue-600" />}
                        {al.type === 'FIRE' && <Flame className="w-3.5 h-3.5 text-orange-600" />}
                        {al.type === 'CYCLONE' && <Wind className="w-3.5 h-3.5 text-cyan-600" />}
                        {al.type}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-400 flex items-center gap-1 font-mono">
                      <Clock className="w-3 h-3" />
                      {new Date(al.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  <h4 className="font-bold text-sm text-slate-900 mb-1">{al.title}</h4>
                  <p className="text-xs text-slate-700 leading-relaxed mb-3">{al.message}</p>

                  <div className="flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-200/60 pt-2 font-mono">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-red-500 shrink-0" />
                      <span>
                        GPS: {al.location?.coordinates?.[1]?.toFixed(4)}°N, {al.location?.coordinates?.[0]?.toFixed(4)}°E (Radius: {al.radiusKm || 15} km)
                      </span>
                    </div>
                    <span className="px-1.5 py-0.5 bg-white rounded border border-slate-200 font-bold text-[10px] text-emerald-700">
                      SYNCED TO APPS
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Publish Alert Modal */}
      {showAlertModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-100 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center space-x-2 text-red-600">
                <AlertTriangle className="w-5 h-5" />
                <h3 className="font-bold text-slate-900 text-lg">Broadcast Official Hazard Alert</h3>
              </div>
              <button
                onClick={() => {
                  setShowAlertModal(false);
                  setPreviewZone(null);
                }}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handlePublishAlert} className="space-y-4 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Alert Headline / Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. FLASH FLOOD WARNING: Sabarmati River Basin Lowlands"
                  value={alertForm.title}
                  onChange={(e) => setAlertForm({ ...alertForm, title: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-red-500 focus:outline-none text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Hazard Category</label>
                  <select
                    value={alertForm.type}
                    onChange={(e) => setAlertForm({ ...alertForm, type: e.target.value })}
                    className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none"
                  >
                    <option value="FLOOD">FLOOD HAZARD</option>
                    <option value="FIRE">FIRE / EXPLOSION</option>
                    <option value="CYCLONE">HIGH WIND / CYCLONE</option>
                    <option value="EARTHQUAKE">EARTHQUAKE TREMOR</option>
                    <option value="EVACUATION">IMMEDIATE EVACUATION</option>
                    <option value="GENERAL">GENERAL ADVISORY</option>
                  </select>
                </div>

                <div>
                  <label className="font-bold text-slate-700 block mb-1">Severity Tier</label>
                  <select
                    value={alertForm.severity}
                    onChange={(e) => setAlertForm({ ...alertForm, severity: e.target.value })}
                    className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none"
                  >
                    <option value="CRITICAL">CRITICAL (Emergency Siren on Phones)</option>
                    <option value="WARNING">WARNING (High Priority Advisory)</option>
                    <option value="ADVISORY">ADVISORY (Precautionary)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Affected Area / Danger Zone Name</label>
                <input
                  type="text"
                  placeholder="Sabarmati Riverfront promenade, Paldi, Vasna"
                  value={alertForm.area}
                  onChange={(e) => setAlertForm({ ...alertForm, area: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={alertForm.latitude}
                    onChange={(e) => setAlertForm({ ...alertForm, latitude: parseFloat(e.target.value) || 23.0225 })}
                    className="w-full p-2 border border-slate-200 rounded-xl font-mono"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={alertForm.longitude}
                    onChange={(e) => setAlertForm({ ...alertForm, longitude: parseFloat(e.target.value) || 72.5714 })}
                    className="w-full p-2 border border-slate-200 rounded-xl font-mono"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Radius (km)</label>
                  <input
                    type="number"
                    value={alertForm.radiusKm}
                    onChange={(e) => {
                      const rad = parseInt(e.target.value) || 15;
                      setAlertForm({ ...alertForm, radiusKm: rad });
                      if (previewZone) setPreviewZone({ ...previewZone, radiusKm: rad });
                    }}
                    className="w-full p-2 border border-slate-200 rounded-xl font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Public Directives &amp; Action Instructions</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Move to higher ground immediately. Do not attempt to cross submerged roads. Emergency shelters operational at Sardar Patel Hall."
                  value={alertForm.message}
                  onChange={(e) => setAlertForm({ ...alertForm, message: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => {
                    setShowAlertModal(false);
                    setPreviewZone(null);
                  }}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold rounded-xl shadow-lg shadow-red-600/30 flex items-center space-x-1.5 active:scale-95 transition"
                >
                  <Send className="w-4 h-4" />
                  <span>Broadcast to All Devices</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
