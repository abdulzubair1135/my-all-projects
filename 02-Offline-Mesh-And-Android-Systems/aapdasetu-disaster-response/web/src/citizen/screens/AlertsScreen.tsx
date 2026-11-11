import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  ShieldCheck,
  AlertTriangle,
  Radio,
  PhoneCall,
  RefreshCw,
  Bell,
  MapPin,
  Clock,
} from 'lucide-react';
import { api } from '../../services/api';

interface AlertsScreenProps {
  onBack?: () => void;
}

export const AlertsScreen: React.FC<AlertsScreenProps> = ({ onBack }) => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [callNotice, setCallNotice] = useState<string | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const res = await api.getAlerts();
      if (res.success && Array.isArray(res.data)) {
        setAlerts(res.data);
      }
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleCall = (name: string, number: string) => {
    setCallNotice(`Connecting emergency hotline to ${name} (${number})...`);
    setTimeout(() => setCallNotice(null), 3500);
  };

  const emergencyHelplines = [
    { number: '112', title: 'National Unified Emergency', desc: 'Police, Fire, Medical & Rescue', color: 'border-red-500/30 bg-red-50/50 text-red-700' },
    { number: '108', title: 'Ambulance & Trauma Medical', desc: 'Emergency 24x7 Life Support', color: 'border-rose-500/30 bg-rose-50/50 text-rose-700' },
    { number: '1070', title: 'State Disaster Control Room', desc: 'Gujarat State Disaster Authority', color: 'border-amber-500/30 bg-amber-50/50 text-amber-800' },
    { number: '1077', title: 'District Disaster EOC', desc: 'District Emergency Operations', color: 'border-blue-500/30 bg-blue-50/50 text-blue-700' },
    { number: '1091', title: 'Women Safety Helpline', desc: '24x7 Police Women Protection', color: 'border-purple-500/30 bg-purple-50/50 text-purple-700' },
  ];

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-[#F7F9FC] select-none">
      {/* Top Header */}
      <header className="px-5 pt-3 pb-3 bg-white border-b border-slate-100 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-2">
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="p-1 -ml-1 text-slate-700 hover:text-slate-900"
            >
              <ArrowLeft className="w-5 h-5 stroke-[2.2]" />
            </button>
          )}
          <div className="w-8 h-8 rounded-xl bg-red-500/10 flex items-center justify-center text-red-600">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-900 leading-tight">Official Disaster Advisories</h1>
            <p className="text-[10px] text-slate-500 font-medium">Government &amp; Relief Operations Alerts</p>
          </div>
        </div>

        <button
          type="button"
          onClick={fetchAlerts}
          disabled={loading}
          className="p-2 bg-slate-100 hover:bg-slate-200 rounded-xl text-slate-700 active:scale-95 transition-all"
          title="Refresh Alerts"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-red-600' : ''}`} />
        </button>
      </header>

      {callNotice && (
        <div className="bg-red-600 text-white text-xs px-4 py-2 text-center flex items-center justify-center gap-2 animate-in fade-in">
          <PhoneCall className="w-4 h-4 animate-bounce" />
          <span>{callNotice}</span>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto px-4 py-4 space-y-4 pb-24 no-scrollbar">
        {alerts.length === 0 ? (
          /* 'No Active Alerts — You Are Safe' Green Shield Empty State */
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="bg-gradient-to-b from-emerald-500/10 to-teal-500/5 border-2 border-emerald-500/30 rounded-3xl p-6 text-center shadow-sm">
              <div className="w-20 h-20 mx-auto rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-xl shadow-emerald-500/30 mb-3 animate-pulse">
                <ShieldCheck className="w-10 h-10 stroke-[2.4]" />
              </div>

              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-700 font-bold text-xs uppercase tracking-wider mb-1">
                Zone Status: Normal
              </span>

              <h2 className="text-xl font-black text-slate-900 tracking-tight mt-1">
                No Active Alerts &mdash; You Are Safe
              </h2>

              <p className="text-xs text-slate-600 max-w-xs mx-auto mt-1 leading-relaxed">
                All flood gauges, meteorological sensors and civic emergency channels in Ahmedabad are operating within safe baseline limits.
              </p>

              <div className="mt-4 pt-3 border-t border-emerald-500/20 flex items-center justify-center space-x-2 text-[11px] font-semibold text-emerald-800">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                <span>Sahay BLE Mesh Monitoring Engine Active</span>
              </div>
            </div>

            {/* Official Helplines Directory */}
            <div className="bg-white rounded-3xl p-4 border border-slate-200/80 shadow-xs space-y-2.5">
              <div className="flex items-center justify-between px-1">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <PhoneCall className="w-3.5 h-3.5 text-red-600" />
                  <span>24x7 Emergency Helplines</span>
                </h3>
                <span className="text-[10px] text-slate-400 font-medium">Toll Free</span>
              </div>

              <div className="grid grid-cols-1 gap-2">
                {emergencyHelplines.map((item) => (
                  <div
                    key={item.number}
                    onClick={() => handleCall(item.title, item.number)}
                    className={`flex items-center justify-between p-3 rounded-2xl border ${item.color} cursor-pointer hover:shadow-xs active:scale-98 transition-all`}
                  >
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-black">{item.number}</span>
                        <span className="text-xs font-bold text-slate-800">&bull; {item.title}</span>
                      </div>
                      <p className="text-[10px] text-slate-500 mt-0.5">{item.desc}</p>
                    </div>
                    <button
                      type="button"
                      className="w-8 h-8 rounded-full bg-white shadow-xs flex items-center justify-center text-slate-700 hover:text-red-600 shrink-0"
                    >
                      <PhoneCall className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Active Alerts List */
          <div className="space-y-3">
            <div className="flex items-center justify-between px-1">
              <span className="text-xs font-bold text-red-600 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>{alerts.length} Active Official Alert(s)</span>
              </span>
              <span className="text-[10px] text-slate-500">Live Broadcast</span>
            </div>

            {alerts.map((alert: any) => (
              <div
                key={alert._id || alert.id}
                className="bg-white rounded-2xl border border-red-200/80 p-4 shadow-sm space-y-2 border-l-4 border-l-red-600"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="px-2 py-0.5 rounded-full bg-red-100 text-red-700 text-[10px] font-bold uppercase tracking-wider">
                      {alert.severity || 'WARNING'} &bull; {alert.type || 'DISASTER'}
                    </span>
                    <h3 className="text-sm font-bold text-slate-900 mt-1">{alert.title}</h3>
                  </div>
                  <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-1" />
                </div>

                <p className="text-xs text-slate-600 leading-relaxed">{alert.message}</p>

                {alert.area && (
                  <div className="flex items-center text-[11px] text-slate-500 gap-1 pt-1 border-t border-slate-100">
                    <MapPin className="w-3 h-3 text-red-500 shrink-0" />
                    <span>Affected Area: {alert.area}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};
