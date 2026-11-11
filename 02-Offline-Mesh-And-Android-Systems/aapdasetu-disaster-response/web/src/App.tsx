import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { GovernmentDashboard } from './pages/GovernmentDashboard';
import { OfficialAlertsPage } from './pages/OfficialAlertsPage';
import { RescueDashboard } from './pages/RescueDashboard';
import { HospitalDashboard } from './pages/HospitalDashboard';
import { NGODashboard } from './pages/NGODashboard';
import { CitizenReportView } from './pages/CitizenReportView';
import { AdminDashboard } from './pages/AdminDashboard';
import { CitizenApp } from './citizen/CitizenApp';
import { GovLogin } from './pages/GovLogin';
import { NGOLogin } from './pages/NGOLogin';
import { AdminLogin } from './pages/AdminLogin';
import { CitizenLogin } from './pages/CitizenLogin';
import { getSocket } from './services/socket';
import { api } from './services/api';
import { SOSEvent } from './types';
import { Radio, MapPin, X, ArrowRight, ShieldAlert, HeartHandshake } from 'lucide-react';

const playEmergencySiren = () => {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const now = ctx.currentTime;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(880, now);
    osc.frequency.exponentialRampToValueAtTime(1200, now + 0.15);
    osc.frequency.exponentialRampToValueAtTime(600, now + 0.35);
    osc.frequency.exponentialRampToValueAtTime(960, now + 0.5);

    gain.gain.setValueAtTime(0.25, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.55);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.55);
  } catch {}
};

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState('gov');
  const [currentUser, setCurrentUser] = useState<any>(() => {
    try {
      const saved = localStorage.getItem('sahay_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [isConnected, setIsConnected] = useState(false);
  const [activeSOSCount, setActiveSOSCount] = useState(0);
  const [liveAlertSOS, setLiveAlertSOS] = useState<SOSEvent | null>(null);
  const seenEventIdsRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    const socket = getSocket();

    const onConnect = () => setIsConnected(true);
    const onDisconnect = () => setIsConnected(false);

    if (socket.connected) {
      setIsConnected(true);
    }

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);

    api.getSOSStats().then((res) => {
      if (res.success && res.data) {
        setActiveSOSCount(res.data.totalActive);
      }
    });

    const handleIncomingSOS = (sos: SOSEvent) => {
      if (!sos || !sos.eventId) return;
      if (seenEventIdsRef.current.has(sos.eventId)) return;
      seenEventIdsRef.current.add(sos.eventId);

      playEmergencySiren();
      setActiveSOSCount((prev) => prev + 1);
      setLiveAlertSOS(sos);
    };

    socket.on('sos:new', handleIncomingSOS);
    socket.on('sos:alert', handleIncomingSOS);

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('sos:new', handleIncomingSOS);
      socket.off('sos:alert', handleIncomingSOS);
    };
  }, []);

  const handleSimulateSOS = async () => {
    try {
      const demoEventId = 'demo-sos-' + Date.now();
      await api.createSOS({
        eventId: demoEventId,
        originDeviceId: 'SIMULATOR_' + Math.floor(1000 + Math.random() * 9000),
        userName: 'Pooja Patel (Field Test)',
        userPhone: '+91 98250 12345',
        type: 'TRAPPED',
        severity: 'CRITICAL',
        description: '🚨 [LIVE TEST SOS] Family trapped near Sabarmati Riverfront promenade due to rising water levels!',
        peopleCount: 3,
        injuredCount: 1,
        latitude: 23.0305,
        longitude: 72.5801,
        accuracy: 5,
        addressText: 'Sabarmati Riverfront Promenade, Ahmedabad, Gujarat',
        source: 'ONLINE',
      });
    } catch (err) {
      console.error('Error simulating SOS:', err);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem('aapdasetu_token');
    localStorage.removeItem('sahay_user');
    setCurrentUser(null);
    setCurrentTab('gov');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Navbar
        currentTab={currentTab}
        onSelectTab={(tab) => setCurrentTab(tab)}
        isConnected={isConnected}
        activeSOSCount={activeSOSCount}
        currentUser={currentUser}
        onSignOut={handleSignOut}
        onSimulateSOS={handleSimulateSOS}
      />

      {/* Global Real-Time Emergency Banner */}
      {liveAlertSOS && (
        <div className="bg-gradient-to-r from-red-600 via-rose-600 to-red-700 text-white shadow-xl border-b-2 border-red-500 animate-in slide-in-from-top duration-300 z-40 sticky top-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div className="flex items-center space-x-3 min-w-0">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center shrink-0 animate-ping">
                <Radio className="w-5 h-5 text-white" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded-full bg-white text-red-700 text-[10px] font-black uppercase tracking-wider shadow-xs">
                    🚨 LIVE DISTRESS BEACON
                  </span>
                  <span className="text-xs font-semibold opacity-90 truncate">
                    {liveAlertSOS.type || 'EMERGENCY'} &bull; {liveAlertSOS.severity || 'CRITICAL'}
                  </span>
                </div>
                <p className="text-sm font-bold truncate mt-0.5">
                  Victim: {liveAlertSOS.userName || 'Citizen'} ({liveAlertSOS.userPhone || 'Emergency Contact'}) &mdash; {liveAlertSOS.description || 'Immediate evacuation needed'}
                </p>
                <div className="flex items-center text-[11px] text-red-100 space-x-2">
                  <MapPin className="w-3.5 h-3.5 shrink-0" />
                  <span>GPS: {liveAlertSOS.location?.coordinates?.[1]?.toFixed(4)}&deg; N, {liveAlertSOS.location?.coordinates?.[0]?.toFixed(4)}&deg; E ({liveAlertSOS.addressText || 'Ahmedabad Grid'})</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-2 shrink-0">
              <button
                onClick={() => {
                  setCurrentTab('gov');
                  setLiveAlertSOS(null);
                }}
                className="px-3.5 py-1.5 bg-white hover:bg-red-50 text-red-700 rounded-lg text-xs font-bold flex items-center space-x-1.5 shadow-md active:scale-95 transition"
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Focus Map &amp; Dispatch</span>
                <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </button>

              <button
                onClick={() => {
                  setCurrentTab('ngo');
                  setLiveAlertSOS(null);
                }}
                className="px-3 py-1.5 bg-red-800/80 hover:bg-red-900 text-white rounded-lg text-xs font-semibold flex items-center space-x-1 transition"
              >
                <HeartHandshake className="w-3.5 h-3.5" />
                <span>NGO Aid</span>
              </button>

              <button
                onClick={() => setLiveAlertSOS(null)}
                className="p-1.5 hover:bg-white/20 text-white rounded-lg transition"
                title="Dismiss banner"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="flex-1">
        {currentTab === 'gov' && <GovernmentDashboard />}
        {currentTab === 'alerts' && <OfficialAlertsPage />}
        {currentTab === 'ngo' && <NGODashboard />}
        {currentTab === 'admin' && <AdminDashboard />}
        {currentTab === 'rescue' && <RescueDashboard />}
        {currentTab === 'hospital' && <HospitalDashboard />}
        {currentTab === 'reports' && <CitizenReportView />}
        {currentTab === 'citizen' && <CitizenApp />}

        {/* 4 Dedicated Login Portals */}
        {currentTab === 'gov-login' && (
          <GovLogin
            onLoginSuccess={(user) => {
              setCurrentUser(user);
              setCurrentTab('gov');
            }}
            onNavigate={(view) => setCurrentTab(view)}
          />
        )}
        {currentTab === 'ngo-login' && (
          <NGOLogin
            onLoginSuccess={(user) => {
              setCurrentUser(user);
              setCurrentTab('ngo');
            }}
            onNavigate={(view) => setCurrentTab(view)}
          />
        )}
        {currentTab === 'admin-login' && (
          <AdminLogin
            onLoginSuccess={(user) => {
              setCurrentUser(user);
              setCurrentTab('admin');
            }}
            onNavigate={(view) => setCurrentTab(view)}
          />
        )}
        {currentTab === 'citizen-login' && (
          <CitizenLogin
            onLoginSuccess={(user) => {
              setCurrentUser(user);
              setCurrentTab('citizen');
            }}
            onNavigate={(view) => setCurrentTab(view)}
          />
        )}
      </main>

      <footer className="bg-slate-900 text-slate-400 py-3 px-6 text-center text-xs border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-2">
        <span>Sahay Unified Disaster Command Platform &copy; 2026 &bull; Real Data Operation &bull; Ble Mesh Multi-Hop Relay</span>
        <span className="text-red-400 font-semibold">When the Network Fails, Sahay Doesn&apos;t.</span>
      </footer>
    </div>
  );
};

export default App;
