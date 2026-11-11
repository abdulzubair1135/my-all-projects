import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  Radio,
  CheckCircle,
  Clock,
  Plus,
  Filter,
  RefreshCw,
  Users,
  HeartPulse,
  Send,
  Package,
  HeartHandshake,
  MapPin,
  ArrowRight,
  ShieldCheck,
  Building2,
  AlertCircle
} from 'lucide-react';
import { SOSEvent, SOSStats, RescueTeam, Shelter, Hospital, CitizenReport, Alert } from '../types';
import { api } from '../services/api';
import { getSocket } from '../services/socket';
import { LiveMap } from '../components/LiveMap';
import { SOSTriageModal } from '../components/SOSTriageModal';

export const GovernmentDashboard: React.FC = () => {
  const [sosList, setSosList] = useState<SOSEvent[]>([]);
  const [stats, setStats] = useState<SOSStats>({
    totalActive: 0,
    critical: 0,
    highPriority: 0,
    assigned: 0,
    resolved: 0,
    offlineRelayed: 0,
    averageResponseTimeMinutes: 0
  });
  const [rescueTeams, setRescueTeams] = useState<RescueTeam[]>([]);
  const [shelters, setShelters] = useState<Shelter[]>([]);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [reports, setReports] = useState<CitizenReport[]>([]);
  const [directives, setDirectives] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isMarkingZone, setIsMarkingZone] = useState(false);
  const [previewZone, setPreviewZone] = useState<{ lat: number; lng: number; radiusKm: number } | null>(null);

  const [activeSubTab, setActiveSubTab] = useState<'overview' | 'directives'>('overview');
  const [selectedSOS, setSelectedSOS] = useState<SOSEvent | null>(null);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [filterSource, setFilterSource] = useState('ALL');

  const [showAlertModal, setShowAlertModal] = useState(false);
  const [alertForm, setAlertForm] = useState({
    title: '',
    message: '',
    type: 'GENERAL',
    severity: 'WARNING',
    area: 'Ahmedabad Lowline Promenade',
    radiusKm: 25,
    latitude: 23.0225,
    longitude: 72.5714
  });

  const [showDirectiveModal, setShowDirectiveModal] = useState(false);
  const [directiveForm, setDirectiveForm] = useState({
    title: '',
    description: '',
    category: 'FOOD_SUPPLY',
    targetAgency: 'Red Cross Gujarat',
    targetShelter: 'Paldi Relief Center',
    address: 'Paldi Ward, Ahmedabad',
    latitude: 23.0125,
    longitude: 72.5621,
    quantity: 500,
    unit: 'meal packets',
    priority: 'URGENT',
    deadline: ''
  });

  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sosRes, statsRes, teamsRes, sheltersRes, hospRes, repRes, dirRes, alertsRes] = await Promise.all([
        api.getSOSList(),
        api.getSOSStats(),
        api.getRescueTeams(),
        api.getShelters(),
        api.getHospitals(),
        api.getReports(),
        api.getDirectives(),
        api.getAlerts()
      ]);

      if (sosRes.success) setSosList(sosRes.data || []);
      if (statsRes.success) setStats(statsRes.data || stats);
      if (teamsRes.success) setRescueTeams(teamsRes.data || []);
      if (sheltersRes.success) setShelters(sheltersRes.data || []);
      if (hospRes.success) setHospitals(hospRes.data || []);
      if (repRes.success) setReports(repRes.data || []);
      if (dirRes.success) setDirectives(dirRes.data || []);
      if (alertsRes.success) setAlerts(alertsRes.data || []);
    } catch (err) {
      console.error('Failed to load command center data:', err);
    } finally {
      setLoading(false);
    }
  };

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

  useEffect(() => {
    loadData();

    const socket = getSocket();
    const handleNewSOS = (newSOS: SOSEvent) => {
      setSosList((prev) => [newSOS, ...prev.filter((s) => s.eventId !== newSOS.eventId)]);
      api.getSOSStats().then((res) => { if (res.success) setStats(res.data); });
    };

    const handleStatusChanged = (payload: any) => {
      setSosList((prev) =>
        prev.map((s) => (s.eventId === payload.eventId ? { ...s, status: payload.status } : s))
      );
      api.getSOSStats().then((res) => { if (res.success) setStats(res.data); });
    };

    const handleNewAlert = (newAlert: Alert) => {
      setAlerts((prev) => [newAlert, ...prev.filter((a) => a._id !== newAlert._id)]);
    };

    socket.on('sos:new', handleNewSOS);
    socket.on('sos:status_changed', handleStatusChanged);
    socket.on('sos:assigned', () => loadData());
    socket.on('sos:verified', () => loadData());
    socket.on('directive:updated', () => loadData());
    socket.on('alert:new', handleNewAlert);
    socket.on('alert:broadcast', handleNewAlert);

    return () => {
      socket.off('sos:new', handleNewSOS);
      socket.off('sos:status_changed', handleStatusChanged);
      socket.off('sos:assigned');
      socket.off('sos:verified');
      socket.off('directive:updated');
      socket.off('alert:new', handleNewAlert);
      socket.off('alert:broadcast', handleNewAlert);
    };
  }, []);

  const handleBroadcastAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!alertForm.title || !alertForm.message) return;
    try {
      await api.createAlert(alertForm);
      setShowAlertModal(false);
      setPreviewZone(null);
      setAlertForm({
        title: '',
        message: '',
        type: 'GENERAL',
        severity: 'WARNING',
        area: 'Ahmedabad Lowline Promenade',
        radiusKm: 25,
        latitude: 23.0225,
        longitude: 72.5714
      });
      loadData();
    } catch (err) {
      alert('Failed to broadcast alert');
    }
  };

  const handleCreateDirective = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!directiveForm.title || !directiveForm.targetAgency) return;
    try {
      await api.createDirective({
        ...directiveForm,
        location: {
          type: 'Point',
          coordinates: [directiveForm.longitude, directiveForm.latitude],
          address: directiveForm.address
        }
      });
      setShowDirectiveModal(false);
      setDirectiveForm({
        title: '',
        description: '',
        category: 'FOOD_SUPPLY',
        targetAgency: 'Red Cross Gujarat',
        targetShelter: 'Paldi Relief Center',
        address: 'Paldi Ward, Ahmedabad',
        latitude: 23.0125,
        longitude: 72.5621,
        quantity: 500,
        unit: 'meal packets',
        priority: 'URGENT',
        deadline: ''
      });
      alert('Directive issued to ' + directiveForm.targetAgency + '!');
      loadData();
    } catch (err) {
      alert('Failed to issue directive');
    }
  };

  const handleReplenishStock = async (directiveId: string) => {
    try {
      await api.replenishStock(directiveId, 'Dispatched Central State Disaster Reserve Stock');
      alert('Central Stock Replenished & Dispatched!');
      loadData();
    } catch (err) {
      alert('Error replenishing stock');
    }
  };

  const filteredSOS = sosList.filter((s) => {
    if (filterSeverity !== 'ALL' && s.severity !== filterSeverity) return false;
    if (filterSource !== 'ALL') {
      if (filterSource === 'BLE' && s.source === 'ONLINE') return false;
      if (filterSource === 'ONLINE' && s.source !== 'ONLINE') return false;
    }
    return true;
  });

  const stockShortages = directives.filter((d) => d.status === 'CRITICAL_STOCK_SHORTAGE');

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Controls & Sub-Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center space-x-2">
            <span>Disaster Command &amp; Triage Center</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time live multi-hop emergency grid &bull; Zero simulated data &bull; MongoDB synchronized
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* Sub Navigation */}
          <div className="bg-slate-100 p-1 rounded-xl flex items-center space-x-1 border border-slate-200">
            <button
              onClick={() => setActiveSubTab('overview')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeSubTab === 'overview'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Overview &amp; Map
            </button>
            <button
              onClick={() => setActiveSubTab('directives')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5 ${
                activeSubTab === 'directives'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span>NGO Supply Orders</span>
              {stockShortages.length > 0 && (
                <span className="w-4 h-4 rounded-full bg-red-600 text-white text-[10px] flex items-center justify-center font-bold animate-pulse">
                  {stockShortages.length}
                </span>
              )}
            </button>
          </div>

          <button
            onClick={loadData}
            disabled={loading}
            className="px-3 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold shadow-xs transition flex items-center space-x-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync</span>
          </button>
          <button
            onClick={() => setShowAlertModal(true)}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-md shadow-red-600/30 transition flex items-center space-x-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Issue Hazard Alert</span>
          </button>
        </div>
      </div>

      {/* Stock Shortage Warning Banner */}
      {stockShortages.length > 0 && (
        <div className="bg-red-600 text-white p-4 rounded-2xl shadow-lg border border-red-500 flex flex-col md:flex-row md:items-center md:justify-between gap-3 animate-in slide-in-from-top">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center shrink-0 animate-bounce">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="text-xs font-black uppercase tracking-wider bg-white/20 inline-block px-2 py-0.5 rounded">
                CRITICAL RELIEF SUPPLY DEFICIT
              </div>
              <p className="text-sm font-bold mt-0.5">
                {stockShortages.length} NGO team(s) report depleted stocks ({stockShortages.map(s => s.targetAgency).join(', ')}). Immediate State replenishment required!
              </p>
            </div>
          </div>
          <button
            onClick={() => setActiveSubTab('directives')}
            className="px-4 py-2 bg-white text-red-700 hover:bg-red-50 font-black text-xs rounded-xl shadow-md uppercase tracking-wider shrink-0"
          >
            Review &amp; Replenish &rarr;
          </button>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">Active SOS</div>
          <div className="text-2xl font-black text-slate-900">{stats.totalActive}</div>
          <div className="text-[10px] text-slate-400 mt-1">Pending response</div>
        </div>

        <div className="p-4 rounded-2xl bg-red-50/60 border border-red-200/60 shadow-xs">
          <div className="text-[11px] font-bold uppercase tracking-wider text-red-600 mb-1 flex items-center space-x-1">
            <ShieldAlert className="w-3.5 h-3.5 animate-pulse" />
            <span>Critical</span>
          </div>
          <div className="text-2xl font-black text-red-700">{stats.critical}</div>
          <div className="text-[10px] text-red-500 mt-1">Immediate danger</div>
        </div>

        <div className="p-4 rounded-2xl bg-amber-50/60 border border-amber-200/60 shadow-xs">
          <div className="text-[11px] font-bold uppercase tracking-wider text-amber-700 mb-1">High Priority</div>
          <div className="text-2xl font-black text-amber-800">{stats.highPriority}</div>
          <div className="text-[10px] text-amber-600 mt-1">Urgent attention</div>
        </div>

        <div className="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-200/60 shadow-xs">
          <div className="text-[11px] font-bold uppercase tracking-wider text-indigo-700 mb-1">Assigned</div>
          <div className="text-2xl font-black text-indigo-800">{stats.assigned}</div>
          <div className="text-[10px] text-indigo-500 mt-1">Rescue en route</div>
        </div>

        <div className="p-4 rounded-2xl bg-purple-50/60 border border-purple-200/60 shadow-xs">
          <div className="text-[11px] font-bold uppercase tracking-wider text-purple-700 mb-1 flex items-center space-x-1">
            <Radio className="w-3.5 h-3.5" />
            <span>BLE Relayed</span>
          </div>
          <div className="text-2xl font-black text-purple-900">{stats.offlineRelayed}</div>
          <div className="text-[10px] text-purple-600 mt-1">Offline multi-hop</div>
        </div>

        <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200/60 shadow-xs">
          <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 mb-1">Resolved</div>
          <div className="text-2xl font-black text-emerald-800">{stats.resolved}</div>
          <div className="text-[10px] text-emerald-600 mt-1">Closed incidents</div>
        </div>
      </div>

      {/* Tab 1: Overview (Map + SOS Feed) */}
      {activeSubTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 flex flex-col h-[620px]">
            <div className="mb-2 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-red-600" />
                  Live Operational Map &amp; Danger Zones
                </h2>
                <span className="text-[11px] text-slate-500">
                  {isMarkingZone ? '🎯 Click anywhere on the map to define danger zone' : 'Real GPS coordinates layer'}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setIsMarkingZone(!isMarkingZone)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 shadow-sm ${
                  isMarkingZone
                    ? 'bg-amber-500 text-slate-950 ring-2 ring-amber-300 animate-pulse'
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                <MapPin className="w-3.5 h-3.5 text-red-500" />
                <span>{isMarkingZone ? '📍 Click Map to Set' : 'Mark Alert on Map'}</span>
              </button>
            </div>
            <div className="flex-1">
              <LiveMap
                sosList={filteredSOS}
                rescueTeams={rescueTeams}
                shelters={shelters}
                hospitals={hospitals}
                reports={reports}
                alerts={alerts}
                isMarkingDangerZone={isMarkingZone}
                onMapClick={handleMapClick}
                previewDangerZone={previewZone}
                onSelectSOS={(sos) => setSelectedSOS(sos)}
                selectedSOS={selectedSOS}
              />
            </div>
          </div>

          <div className="lg:col-span-5 flex flex-col h-[620px] bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Emergency Incident Feed</h2>
                <span className="text-xs text-slate-500">{filteredSOS.length} incidents reported</span>
              </div>

              <div className="flex items-center space-x-1">
                <select
                  value={filterSeverity}
                  onChange={(e) => setFilterSeverity(e.target.value)}
                  className="bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-[11px] text-slate-700 focus:outline-none"
                >
                  <option value="ALL">Severity: All</option>
                  <option value="CRITICAL">Critical</option>
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                </select>

                <select
                  value={filterSource}
                  onChange={(e) => setFilterSource(e.target.value)}
                  className="bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-[11px] text-slate-700 focus:outline-none"
                >
                  <option value="ALL">Transport: All</option>
                  <option value="BLE">BLE Relayed</option>
                  <option value="ONLINE">Online Direct</option>
                </select>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-slate-100 mt-2 pr-1 scrollbar-thin">
              {filteredSOS.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs">
                  <CheckCircle className="w-8 h-8 text-emerald-500 mb-2" />
                  <span>No active emergency SOS incidents matching filters</span>
                </div>
              ) : (
                filteredSOS.map((sos) => (
                  <div
                    key={sos.eventId}
                    onClick={() => setSelectedSOS(sos)}
                    className={`p-3 rounded-xl cursor-pointer transition-all ${
                      selectedSOS?.eventId === sos.eventId
                        ? 'bg-red-50 border border-red-200'
                        : 'hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          sos.severity === 'CRITICAL' ? 'bg-red-600 text-white' :
                          sos.severity === 'HIGH' ? 'bg-amber-500 text-white' : 'bg-slate-200 text-slate-800'
                        }`}>
                          {sos.severity}
                        </span>
                        <span className="text-xs font-bold text-slate-800">{sos.type}</span>
                        <span className="text-[10px] text-slate-400">
                          {sos.source === 'ONLINE' ? '🌐 Direct' : `📡 Relayed (${sos.hopCount || 1} hops)`}
                        </span>
                      </div>
                      <span className={`text-[10px] font-bold uppercase ${
                        sos.status === 'RESOLVED' ? 'text-emerald-600' :
                        sos.status === 'ASSIGNED' ? 'text-indigo-600' : 'text-amber-600'
                      }`}>
                        {sos.status}
                      </span>
                    </div>

                    <p className="text-xs text-slate-700 font-medium mt-1 line-clamp-2">
                      {sos.description}
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2">
                      <span className="truncate max-w-[200px]">{sos.userName || 'Citizen'} • {sos.addressText || 'Ahmedabad'}</span>
                      <span className="font-semibold text-slate-700">{sos.peopleCount} person(s)</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Directives & NGO Supply Distribution */}
      {activeSubTab === 'directives' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-lg font-black text-slate-900 flex items-center space-x-2">
                <HeartHandshake className="w-5 h-5 text-red-600" />
                <span>State Government Relief Directives &amp; NGO Resource Allocation</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Issue authoritative mobilization orders to verified humanitarian partners: Food, Water, Tarps, Boats &amp; Medical Supplies
              </p>
            </div>

            <button
              onClick={() => setShowDirectiveModal(true)}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-md shadow-red-600/30 transition flex items-center space-x-1.5"
            >
              <Plus className="w-4 h-4" />
              <span>Issue New Supply Order</span>
            </button>
          </div>

          {/* Directives Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Directive &amp; Category</th>
                  <th className="py-3 px-4">Assigned Partner</th>
                  <th className="py-3 px-4">Quantity &amp; Camp</th>
                  <th className="py-3 px-4">Priority</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {directives.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-slate-400">
                      No active relief directives issued. Click &quot;Issue New Supply Order&quot; to mobilize humanitarian partners.
                    </td>
                  </tr>
                ) : (
                  directives.map((dir) => (
                    <tr key={dir._id || dir.id} className="hover:bg-slate-50/80">
                      <td className="py-3 px-4 font-semibold text-slate-900">
                        <div>{dir.title}</div>
                        <span className="text-[10px] text-slate-500 uppercase">{dir.category}</span>
                      </td>
                      <td className="py-3 px-4 text-slate-700 font-medium">
                        <div className="flex items-center space-x-1.5">
                          <Building2 className="w-3.5 h-3.5 text-slate-400" />
                          <span>{dir.targetAgency}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-800">{dir.quantity} {dir.unit}</div>
                        <div className="text-[10px] text-slate-500">{dir.targetShelter || dir.location?.address || 'Ahmedabad Camp'}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          dir.priority === 'EMERGENCY' ? 'bg-red-100 text-red-700 border border-red-200' :
                          dir.priority === 'URGENT' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {dir.priority}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {dir.status === 'CRITICAL_STOCK_SHORTAGE' ? (
                          <span className="px-2.5 py-1 rounded-full bg-red-600 text-white text-[10px] font-black uppercase tracking-wider animate-pulse flex items-center space-x-1 w-max">
                            <AlertCircle className="w-3 h-3" />
                            <span>STOCK SHORTAGE REPORTED</span>
                          </span>
                        ) : dir.status === 'FULFILLED' ? (
                          <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                            &check; FULFILLED
                          </span>
                        ) : dir.status === 'IN_TRANSIT' ? (
                          <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 text-[10px] font-bold">
                            🚚 IN TRANSIT
                          </span>
                        ) : dir.status === 'ACKNOWLEDGED' ? (
                          <span className="px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800 text-[10px] font-bold">
                            ACKNOWLEDGED
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 text-[10px] font-bold">
                            PENDING NGO
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        {dir.status === 'CRITICAL_STOCK_SHORTAGE' && (
                          <button
                            onClick={() => handleReplenishStock(dir._id || dir.id)}
                            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-black shadow-xs uppercase tracking-wider"
                          >
                            Replenish Stock
                          </button>
                        )}
                        {dir.status !== 'CRITICAL_STOCK_SHORTAGE' && (
                          <span className="text-[10px] text-slate-400 font-mono">
                            ID: {(dir._id || dir.id).slice(-6)}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* SOS Triage Modal */}
      {selectedSOS && (
        <SOSTriageModal
          sos={selectedSOS}
          onClose={() => setSelectedSOS(null)}
          onUpdate={() => {
            setSelectedSOS(null);
            loadData();
          }}
          rescueTeams={rescueTeams}
        />
      )}

      {/* Modal: Issue Hazard / Map Danger Zone Alert */}
      {showAlertModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 animate-in fade-in">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                <span>Publish Official Hazard Alert &amp; Danger Zone</span>
              </h2>
              <button onClick={() => setShowAlertModal(false)} className="text-slate-400 hover:text-slate-600">
                &times;
              </button>
            </div>

            <form onSubmit={handleBroadcastAlert} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Alert Headline</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. FLASH FLOOD WARNING: Sabarmati River Basin Lowlands"
                  value={alertForm.title}
                  onChange={(e) => setAlertForm({ ...alertForm, title: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-red-500 focus:outline-none"
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
                    <option value="CRITICAL">CRITICAL (Emergency Siren)</option>
                    <option value="WARNING">WARNING (High Priority)</option>
                    <option value="ADVISORY">ADVISORY (Precautionary)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Affected Area / Danger Zone</label>
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
                    className="w-full p-2 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={alertForm.longitude}
                    onChange={(e) => setAlertForm({ ...alertForm, longitude: parseFloat(e.target.value) || 72.5714 })}
                    className="w-full p-2 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Radius (km)</label>
                  <input
                    type="number"
                    value={alertForm.radiusKm}
                    onChange={(e) => setAlertForm({ ...alertForm, radiusKm: parseInt(e.target.value) || 10 })}
                    className="w-full p-2 border border-slate-200 rounded-xl"
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
                  onClick={() => setShowAlertModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold shadow-md shadow-red-600/30 flex items-center space-x-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Broadcast to All Devices</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Issue Supply Directive to NGO */}
      {showDirectiveModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 animate-in fade-in">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                <Package className="w-5 h-5 text-red-600" />
                <span>Issue Tactical Supply Order to NGO</span>
              </h2>
              <button onClick={() => setShowDirectiveModal(false)} className="text-slate-400 hover:text-slate-600">
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateDirective} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Directive Order Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Deploy 1,000 Food Packets & Water Filter Kits to Paldi Relief Camp"
                  value={directiveForm.title}
                  onChange={(e) => setDirectiveForm({ ...directiveForm, title: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Humanitarian Partner (NGO)</label>
                  <select
                    value={directiveForm.targetAgency}
                    onChange={(e) => setDirectiveForm({ ...directiveForm, targetAgency: e.target.value })}
                    className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none"
                  >
                    <option value="Red Cross Gujarat">Red Cross Gujarat</option>
                    <option value="Goonj Disaster Relief">Goonj Disaster Relief</option>
                    <option value="SEWA Emergency Relief Wing">SEWA Emergency Relief Wing</option>
                    <option value="Akshaya Patra Disaster Relief">Akshaya Patra Disaster Relief</option>
                    <option value="Habitat for Humanity Gujarat">Habitat for Humanity Gujarat</option>
                  </select>
                </div>

                <div>
                  <label className="font-bold text-slate-700 block mb-1">Resource Category</label>
                  <select
                    value={directiveForm.category}
                    onChange={(e) => setDirectiveForm({ ...directiveForm, category: e.target.value })}
                    className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none"
                  >
                    <option value="FOOD_SUPPLY">Food Packets &amp; Meals</option>
                    <option value="DRINKING_WATER">Drinking Water / Filter Kits</option>
                    <option value="MEDICAL_KITS">Medical Kits &amp; First Aid</option>
                    <option value="SHELTER_TARPS">Tarpaulins &amp; Tents</option>
                    <option value="RESCUE_BOATS">Rescue Inflatable Boats</option>
                    <option value="POWER_BACKUP">Portable Generators &amp; Solar</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Quantity</label>
                  <input
                    type="number"
                    required
                    value={directiveForm.quantity}
                    onChange={(e) => setDirectiveForm({ ...directiveForm, quantity: parseInt(e.target.value) || 0 })}
                    className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none"
                  />
                </div>

                <div>
                  <label className="font-bold text-slate-700 block mb-1">Unit of Measurement</label>
                  <input
                    type="text"
                    required
                    placeholder="packets, liters, kits, units"
                    value={directiveForm.unit}
                    onChange={(e) => setDirectiveForm({ ...directiveForm, unit: e.target.value })}
                    className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Target Distribution Camp / Location</label>
                <input
                  type="text"
                  required
                  placeholder="Paldi Relief Camp, Ward 7, Ahmedabad"
                  value={directiveForm.targetShelter}
                  onChange={(e) => setDirectiveForm({ ...directiveForm, targetShelter: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowDirectiveModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold shadow-md shadow-red-600/30 flex items-center space-x-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Dispatch Order to NGO</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
