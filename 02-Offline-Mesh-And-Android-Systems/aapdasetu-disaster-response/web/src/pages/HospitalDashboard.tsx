import React, { useState, useEffect } from 'react';
import { Building2, Bed, HeartPulse, Truck, Droplet, Check, Save } from 'lucide-react';
import { Hospital } from '../types';
import { api } from '../services/api';

export const HospitalDashboard: React.FC = () => {
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [selectedHospital, setSelectedHospital] = useState<Hospital | null>(null);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const loadHospitals = async () => {
    try {
      const res = await api.getHospitals();
      if (res.success && res.data?.length > 0) {
        setHospitals(res.data);
        if (!selectedHospital) setSelectedHospital(res.data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadHospitals();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHospital) return;
    setSaving(true);
    try {
      await api.updateHospital(selectedHospital._id, selectedHospital);
      setSuccessMsg('Hospital capacity synchronized with State Emergency Grid!');
      setTimeout(() => setSuccessMsg(''), 4000);
      loadHospitals();
    } catch (err) {
      alert('Failed to update hospital resources');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <Building2 className="w-5 h-5 text-rose-600" />
            <span>Hospital Emergency Readiness Dashboard</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time critical care capacity, ICU availability, ambulances, and blood inventory
          </p>
        </div>

        {hospitals.length > 0 && (
          <select
            value={selectedHospital?._id}
            onChange={(e) => {
              const h = hospitals.find((item) => item._id === e.target.value);
              if (h) setSelectedHospital(h);
            }}
            className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold text-slate-800"
          >
            {hospitals.map((h) => (
              <option key={h._id} value={h._id}>
                {h.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {successMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 font-semibold flex items-center space-x-2">
          <Check className="w-4 h-4 text-emerald-600" />
          <span>{successMsg}</span>
        </div>
      )}

      {selectedHospital && (
        <form onSubmit={handleSave} className="space-y-6">
          {/* Capacity Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-500">
                <Bed className="w-4 h-4 text-blue-500" />
                <span>General Beds</span>
              </div>
              <div>
                <label className="block text-[11px] text-slate-500 mb-1">Available / Total</label>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    value={selectedHospital.availableBeds}
                    onChange={(e) =>
                      setSelectedHospital({ ...selectedHospital, availableBeds: Number(e.target.value) })
                    }
                    className="w-20 bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm font-bold text-slate-900"
                  />
                  <span className="text-slate-400">/</span>
                  <input
                    type="number"
                    value={selectedHospital.totalBeds}
                    onChange={(e) =>
                      setSelectedHospital({ ...selectedHospital, totalBeds: Number(e.target.value) })
                    }
                    className="w-20 bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm text-slate-600"
                  />
                </div>
              </div>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-500">
                <HeartPulse className="w-4 h-4 text-rose-500" />
                <span>ICU / Ventilator Beds</span>
              </div>
              <div>
                <label className="block text-[11px] text-slate-500 mb-1">Available / Total</label>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    value={selectedHospital.availableICUBeds}
                    onChange={(e) =>
                      setSelectedHospital({ ...selectedHospital, availableICUBeds: Number(e.target.value) })
                    }
                    className="w-20 bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm font-bold text-rose-600"
                  />
                  <span className="text-slate-400">/</span>
                  <input
                    type="number"
                    value={selectedHospital.icuBeds}
                    onChange={(e) =>
                      setSelectedHospital({ ...selectedHospital, icuBeds: Number(e.target.value) })
                    }
                    className="w-20 bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm text-slate-600"
                  />
                </div>
              </div>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-500">
                <Truck className="w-4 h-4 text-amber-500" />
                <span>Ambulances</span>
              </div>
              <div>
                <label className="block text-[11px] text-slate-500 mb-1">On-Duty / Total Fleet</label>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    value={selectedHospital.availableAmbulances}
                    onChange={(e) =>
                      setSelectedHospital({ ...selectedHospital, availableAmbulances: Number(e.target.value) })
                    }
                    className="w-20 bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm font-bold text-amber-600"
                  />
                  <span className="text-slate-400">/</span>
                  <input
                    type="number"
                    value={selectedHospital.ambulances}
                    onChange={(e) =>
                      setSelectedHospital({ ...selectedHospital, ambulances: Number(e.target.value) })
                    }
                    className="w-20 bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm text-slate-600"
                  />
                </div>
              </div>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-500">
                <span>Emergency State</span>
              </div>
              <div>
                <label className="block text-[11px] text-slate-500 mb-1">Triage Protocol</label>
                <select
                  value={selectedHospital.emergencyStatus}
                  onChange={(e) =>
                    setSelectedHospital({ ...selectedHospital, emergencyStatus: e.target.value as any })
                  }
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs font-bold text-slate-800"
                >
                  <option value="NORMAL">Normal Reception</option>
                  <option value="HIGH_ALERT">High Alert (Mass Casualty Ready)</option>
                  <option value="OVERWHELMED">Overwhelmed</option>
                  <option value="DIVERTING">Diverting Inbound Cases</option>
                </select>
              </div>
            </div>
          </div>

          {/* Blood Availability Section */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-700">
              <Droplet className="w-4 h-4 text-red-600" />
              <span>Blood Bank Stock Units</span>
            </div>

            <div className="grid grid-cols-4 sm:grid-cols-8 gap-3">
              {['aPos', 'aNeg', 'bPos', 'bNeg', 'abPos', 'abNeg', 'oPos', 'oNeg'].map((type) => {
                const label = type
                  .replace('Pos', '+')
                  .replace('Neg', '-')
                  .toUpperCase();
                const count = (selectedHospital.bloodAvailability as any)[type] || 0;
                return (
                  <div key={type} className="p-3 bg-red-50/50 rounded-xl border border-red-100 text-center">
                    <div className="font-black text-sm text-red-700">{label}</div>
                    <input
                      type="number"
                      value={count}
                      onChange={(e) => {
                        setSelectedHospital({
                          ...selectedHospital,
                          bloodAvailability: {
                            ...selectedHospital.bloodAvailability,
                            [type]: Number(e.target.value)
                          }
                        });
                      }}
                      className="w-16 mx-auto mt-1 bg-white border border-red-200 rounded text-center text-xs font-bold text-slate-800 p-1"
                    />
                    <div className="text-[10px] text-slate-400 mt-0.5">units</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Submit */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold flex items-center space-x-2 shadow-md shadow-rose-600/30 transition"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Syncing...' : 'Save & Broadcast Capacity'}</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
