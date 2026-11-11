import React, { useState, useEffect } from 'react';
import {
  HeartHandshake,
  Package,
  Users,
  Plus,
  Check,
  ShieldAlert,
  Radio,
  MapPin,
  Phone,
  AlertTriangle,
  Send,
  Building2,
  AlertCircle,
  Truck,
  RefreshCw
} from 'lucide-react';
import { Resource, SOSEvent } from '../types';
import { api } from '../services/api';
import { getSocket } from '../services/socket';

export const NGODashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'depot' | 'directives' | 'volunteers'>('directives');
  const [resources, setResources] = useState<Resource[]>([]);
  const [volunteers, setVolunteers] = useState<any[]>([]);
  const [incomingSOS, setIncomingSOS] = useState<SOSEvent[]>([]);
  const [directives, setDirectives] = useState<any[]>([]);

  const [showAddResourceModal, setShowAddResourceModal] = useState(false);
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [showShortageModal, setShowShortageModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedVolunteer, setSelectedVolunteer] = useState<any | null>(null);
  const [selectedDirective, setSelectedDirective] = useState<any | null>(null);

  const [volunteerTaskForm, setVolunteerTaskForm] = useState({
    title: 'Deliver Food Rations & Potable Water',
    targetLocation: 'Relief Camp Sector 4, Ahmedabad',
    priority: 'HIGH',
    instructions: 'Coordinate with local community leaders to distribute 100 meal packets and water supplies.'
  });

  const [shortageForm, setShortageForm] = useState({
    missingItems: 'Clean Drinking Water Packets & Chlorine Tablets',
    requestedQuantity: 200,
    notes: 'Local regional supplier depleted due to flash flood bridge washout.'
  });

  const [alertForm, setAlertForm] = useState({
    title: '',
    message: '',
    type: 'SHELTER',
    severity: 'ADVISORY',
    area: 'Ahmedabad Relief Hub'
  });

  const [resourceForm, setResourceForm] = useState({
    organizationName: 'Gujarat Relief Network / Red Cross',
    type: 'FOOD',
    quantity: 500,
    unit: 'meal packets'
  });

  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [resData, volData, sosData, dirData] = await Promise.all([
        api.getResources(),
        api.getVolunteers(),
        api.getSOSList({ limit: '10' }),
        api.getDirectives()
      ]);
      if (resData.success) setResources(resData.data || []);
      if (volData.success) setVolunteers(volData.data || []);
      if (sosData.success) setIncomingSOS(sosData.data || []);
      if (dirData.success) setDirectives(dirData.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    const socket = getSocket();
    const handleNewSOS = (sos: SOSEvent) => {
      setIncomingSOS((prev) => {
        if (prev.some((item) => item.eventId === sos.eventId)) return prev;
        return [sos, ...prev];
      });
    };

    socket.on('sos:new', handleNewSOS);
    socket.on('sos:alert', handleNewSOS);
    socket.on('directive:new', () => loadData());
    socket.on('directive:updated', () => loadData());

    return () => {
      socket.off('sos:new', handleNewSOS);
      socket.off('sos:alert', handleNewSOS);
      socket.off('directive:new');
      socket.off('directive:updated');
    };
  }, []);

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      await api.updateDirectiveStatus(id, status);
      alert('Order status updated to: ' + status);
      loadData();
    } catch (err) {
      alert('Failed to update status');
    }
  };

  const handleTriggerShortageRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDirective) return;
    try {
      await api.requestStockShortage(selectedDirective._id || selectedDirective.id, shortageForm);
      setShowShortageModal(false);
      alert('🚨 Stock shortage alert transmitted to Government Command Center!');
      loadData();
    } catch (err) {
      alert('Failed to report shortage');
    }
  };

  const handleCreateResource = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('aapdasetu_token');
      await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000/api'}/resources`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(resourceForm)
      });
      setShowAddResourceModal(false);
      loadData();
    } catch {
      alert('Error saving relief item');
    }
  };

  const handleBroadcastAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!alertForm.title || !alertForm.message) return;
    try {
      await api.createAlert(alertForm);
      setShowAlertModal(false);
      setAlertForm({ title: '', message: '', type: 'SHELTER', severity: 'ADVISORY', area: 'Ahmedabad Relief Hub' });
      alert('NGO Relief Alert successfully broadcasted to citizens!');
      loadData();
    } catch {
      alert('Failed to broadcast alert');
    }
  };

  const handleAssignVolunteerTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedVolunteer) return;
    try {
      await api.createDirective({
        title: `[Volunteer Order] ${volunteerTaskForm.title}`,
        targetAgency: 'VOLUNTEER',
        assignedVolunteer: selectedVolunteer.name,
        volunteerPhone: selectedVolunteer.phone,
        priority: volunteerTaskForm.priority,
        targetLocation: volunteerTaskForm.targetLocation,
        instructions: volunteerTaskForm.instructions,
        status: 'DISPATCHED'
      });
      setShowAssignModal(false);
      alert(`✅ Field Order successfully dispatched to volunteer ${selectedVolunteer.name}!`);
      loadData();
    } catch {
      alert('Failed to dispatch volunteer directive');
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <HeartHandshake className="w-6 h-6 text-emerald-600" />
            <span>NGO Disaster Relief Command &amp; Supplies Network</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time emergency relief coordination: Food, Clean Water, Medical Kits, Blankets &amp; Volunteer Squads
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* Sub Navigation */}
          <div className="bg-slate-100 p-1 rounded-xl flex items-center space-x-1 border border-slate-200 text-xs">
            <button
              onClick={() => setActiveTab('directives')}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                activeTab === 'directives'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Gov Directives ({directives.length})
            </button>
            <button
              onClick={() => setActiveTab('depot')}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                activeTab === 'depot'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Relief Depot ({resources.length})
            </button>
            <button
              onClick={() => setActiveTab('volunteers')}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                activeTab === 'volunteers'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Volunteers ({volunteers.length})
            </button>
          </div>

          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 bg-slate-100 hover:bg-slate-200 rounded-xl text-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setShowAlertModal(true)}
            className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/30 transition flex items-center space-x-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Broadcast Aid Alert</span>
          </button>
        </div>
      </div>

      {/* Tab 1: Government Directives & Supply Allocation */}
      {activeTab === 'directives' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                  <Building2 className="w-4 h-4 text-emerald-600" />
                  <span>State Government Supply Orders Assigned to NGOs</span>
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Orders dispatched by State Disaster Management Authority for immediate fulfillment
                </p>
              </div>
            </div>

            <div className="divide-y divide-slate-100">
              {directives.length === 0 ? (
                <div className="text-center py-8 text-slate-400 text-xs">
                  No pending government directives at this time. All relief supplies in target camps are satisfied.
                </div>
              ) : (
                directives.map((dir) => (
                  <div key={dir._id || dir.id} className="py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="space-y-1 max-w-xl">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          dir.priority === 'EMERGENCY' ? 'bg-red-100 text-red-700' :
                          dir.priority === 'URGENT' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {dir.priority}
                        </span>
                        <span className="text-xs font-bold text-slate-900">{dir.title}</span>
                        <span className="text-[10px] text-slate-400 font-mono">[{dir.category}]</span>
                      </div>
                      <p className="text-xs text-slate-600">
                        Target Agency: <strong className="text-slate-800">{dir.targetAgency}</strong> &bull; Quantity: <strong className="text-emerald-700 font-black">{dir.quantity} {dir.unit}</strong>
                      </p>
                      <div className="flex items-center space-x-3 text-[11px] text-slate-500">
                        <span className="flex items-center space-x-1">
                          <MapPin className="w-3.5 h-3.5 text-slate-400" />
                          <span>{dir.targetShelter || dir.location?.address || 'Ahmedabad Grid'}</span>
                        </span>
                        <span>&bull;</span>
                        <span>Current Status: <strong className="text-slate-800">{dir.status}</strong></span>
                      </div>
                    </div>

                    {/* Action Buttons for NGO */}
                    <div className="flex items-center space-x-2 shrink-0">
                      {dir.status === 'PENDING' && (
                        <button
                          onClick={() => handleUpdateStatus(dir._id || dir.id, 'ACKNOWLEDGED')}
                          className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg text-xs font-bold transition"
                        >
                          Acknowledge
                        </button>
                      )}

                      {dir.status === 'ACKNOWLEDGED' && (
                        <button
                          onClick={() => handleUpdateStatus(dir._id || dir.id, 'IN_TRANSIT')}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition flex items-center space-x-1"
                        >
                          <Truck className="w-3.5 h-3.5" />
                          <span>Dispatch In-Transit</span>
                        </button>
                      )}

                      {dir.status === 'IN_TRANSIT' && (
                        <button
                          onClick={() => handleUpdateStatus(dir._id || dir.id, 'FULFILLED')}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition flex items-center space-x-1"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>Mark Fulfilled</span>
                        </button>
                      )}

                      {dir.status === 'FULFILLED' && (
                        <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-lg text-xs font-bold">
                          &check; Order Completed
                        </span>
                      )}

                      {/* Request Stock Shortage from Government */}
                      {dir.status !== 'FULFILLED' && (
                        <button
                          onClick={() => {
                            setSelectedDirective(dir);
                            setShowShortageModal(true);
                          }}
                          className="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-lg text-xs font-bold transition flex items-center space-x-1"
                        >
                          <AlertCircle className="w-3.5 h-3.5" />
                          <span>Request Govt Stock</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Depot Resources */}
      {activeTab === 'depot' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                <Package className="w-4 h-4 text-emerald-600" />
                <span>NGO Warehouse Relief Inventory</span>
              </h2>
            </div>
            <button
              onClick={() => setShowAddResourceModal(true)}
              className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold flex items-center space-x-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Stock Item</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {resources.map((r: any) => (
              <div key={r._id || r.id} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                <span className="text-[10px] font-bold text-emerald-700 uppercase bg-emerald-100 px-2 py-0.5 rounded">
                  {r.type}
                </span>
                <div className="text-base font-black text-slate-900 mt-1">
                  {r.quantity} <span className="text-xs font-normal text-slate-500">{r.unit}</span>
                </div>
                <div className="text-xs text-slate-600 truncate">{r.organizationName}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Volunteers */}
      {activeTab === 'volunteers' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <Users className="w-4 h-4 text-emerald-600" />
              <span>Registered Field Volunteers ({volunteers.length})</span>
            </h2>
          </div>

          <div className="divide-y divide-slate-100">
            {volunteers.map((vol: any) => (
              <div key={vol._id || vol.id} className="py-2.5 flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-slate-800">{vol.name}</span>
                  <span className="text-slate-400 ml-2">({vol.phone})</span>
                  <div className="text-[10px] text-slate-500">{vol.skills?.join(', ') || 'General Relief & First Aid'}</div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    vol.status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {vol.status || 'AVAILABLE'}
                  </span>
                  <button
                    onClick={() => {
                      setSelectedVolunteer(vol);
                      setShowAssignModal(true);
                    }}
                    className="px-2.5 py-1 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-700 text-[10px] transition-colors shadow-xs"
                  >
                    Assign Field Task
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal: Assign Field Order to Volunteer */}
      {showAssignModal && selectedVolunteer && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-in fade-in">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                <Users className="w-5 h-5 text-emerald-600" />
                <span>Assign Field Order to Volunteer</span>
              </h2>
              <button onClick={() => setShowAssignModal(false)} className="text-slate-400 hover:text-slate-600">
                &times;
              </button>
            </div>

            <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-xs">
              <span className="font-bold text-emerald-900">Volunteer: {selectedVolunteer.name}</span>
              <span className="text-emerald-700 ml-2">({selectedVolunteer.phone})</span>
              <div className="text-[10px] text-emerald-600 mt-0.5">Deployment Zone: Ahmedabad Disaster Grid</div>
            </div>

            <form onSubmit={handleAssignVolunteerTask} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Task Title / Mission Directive</label>
                <input
                  type="text"
                  required
                  value={volunteerTaskForm.title}
                  onChange={(e) => setVolunteerTaskForm({ ...volunteerTaskForm, title: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Priority Level</label>
                <select
                  value={volunteerTaskForm.priority}
                  onChange={(e) => setVolunteerTaskForm({ ...volunteerTaskForm, priority: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-emerald-500 focus:outline-none"
                >
                  <option value="CRITICAL">🔴 CRITICAL — Immediate Deployment</option>
                  <option value="HIGH">🟠 HIGH — Priority Relief</option>
                  <option value="MEDIUM">🟡 MEDIUM — Standard Support</option>
                </select>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Target Location / Camp</label>
                <input
                  type="text"
                  required
                  value={volunteerTaskForm.targetLocation}
                  onChange={(e) => setVolunteerTaskForm({ ...volunteerTaskForm, targetLocation: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Mission Instructions / Supply Details</label>
                <textarea
                  rows={3}
                  value={volunteerTaskForm.instructions}
                  onChange={(e) => setVolunteerTaskForm({ ...volunteerTaskForm, instructions: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAssignModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-700 shadow-sm"
                >
                  🚀 Dispatch Order to Volunteer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Request Stock Shortage Replenishment from Govt */}
      {showShortageModal && selectedDirective && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-in fade-in">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h2 className="text-base font-bold text-red-600 flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <span>Report Critical Stock Shortage to Govt</span>
              </h2>
              <button onClick={() => setShowShortageModal(false)} className="text-slate-400 hover:text-slate-600">
                &times;
              </button>
            </div>

            <p className="text-xs text-slate-600">
              Reporting a shortage for order: <strong>{selectedDirective.title}</strong> will trigger a high-priority replenishment alert in the State Emergency Operations Centre.
            </p>

            <form onSubmit={handleTriggerShortageRequest} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Missing Items / Deficit Description</label>
                <input
                  type="text"
                  required
                  value={shortageForm.missingItems}
                  onChange={(e) => setShortageForm({ ...shortageForm, missingItems: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Deficit Quantity Needed from Govt Central Stock</label>
                <input
                  type="number"
                  required
                  value={shortageForm.requestedQuantity}
                  onChange={(e) => setShortageForm({ ...shortageForm, requestedQuantity: parseInt(e.target.value) || 0 })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Reason / Bottleneck</label>
                <textarea
                  rows={2}
                  value={shortageForm.notes}
                  onChange={(e) => setShortageForm({ ...shortageForm, notes: e.target.value })}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:ring-1 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowShortageModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold shadow-md shadow-red-600/30"
                >
                  Transmit Shortage Alert
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Add Resource */}
      {showAddResourceModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-in fade-in">
            <h2 className="text-base font-bold text-slate-900 pb-2 border-b border-slate-100">
              Register New Relief Item in Depot
            </h2>
            <form onSubmit={handleCreateResource} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Item Category</label>
                <select
                  value={resourceForm.type}
                  onChange={(e) => setResourceForm({ ...resourceForm, type: e.target.value })}
                  className="w-full p-2 border border-slate-200 rounded-xl"
                >
                  <option value="FOOD">Food &amp; Rations</option>
                  <option value="WATER">Drinking Water</option>
                  <option value="MEDICAL">Medical Kits</option>
                  <option value="BLANKET">Blankets / Shelter Tarps</option>
                  <option value="BOAT">Rescue Boat</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Quantity</label>
                  <input
                    type="number"
                    value={resourceForm.quantity}
                    onChange={(e) => setResourceForm({ ...resourceForm, quantity: parseInt(e.target.value) || 0 })}
                    className="w-full p-2 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Unit</label>
                  <input
                    type="text"
                    value={resourceForm.unit}
                    onChange={(e) => setResourceForm({ ...resourceForm, unit: e.target.value })}
                    className="w-full p-2 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>
              <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddResourceModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold"
                >
                  Save Stock
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Broadcast Alert */}
      {showAlertModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-in fade-in">
            <h2 className="text-base font-bold text-slate-900 pb-2 border-b border-slate-100">
              Broadcast Humanitarian Relief Advisory
            </h2>
            <form onSubmit={handleBroadcastAlert} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Alert Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Free Hot Meals & Water Distribution Center Open"
                  value={alertForm.title}
                  onChange={(e) => setAlertForm({ ...alertForm, title: e.target.value })}
                  className="w-full p-2 border border-slate-200 rounded-xl"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Details &amp; Camp Location</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Distribution active from 9am to 6pm at Sardar Patel Relief Camp. Free baby formula and medical kits available."
                  value={alertForm.message}
                  onChange={(e) => setAlertForm({ ...alertForm, message: e.target.value })}
                  className="w-full p-2 border border-slate-200 rounded-xl"
                />
              </div>
              <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAlertModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold"
                >
                  Broadcast to Citizens
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
