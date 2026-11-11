import React, { useState, useRef } from 'react';
import {
  Bell,
  MapPin,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  Radio,
  Home,
  Plus,
  MessageSquare,
  Wifi,
  Camera,
  Map,
  Megaphone,
} from 'lucide-react';
import { ScreenType, UserProfile } from '../types';
import { defaultUserProfile } from '../data/mockData';
import { api } from '../../services/api';

interface HomeScreenProps {
  user?: UserProfile;
  userProfile?: UserProfile;
  onNavigate: (screen: ScreenType) => void;
  onTriggerSos: () => void;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ user, userProfile, onNavigate, onTriggerSos }) => {
  const currentUser = userProfile || user || defaultUserProfile;
  const [isHolding, setIsHolding] = useState(false);
  const [holdProgress, setHoldProgress] = useState(0);
  const holdIntervalRef = useRef<number | null>(null);
  const [showLocationPicker, setShowLocationPicker] = useState(false);

  const dispatchLiveSOS = () => {
    try {
      api.createSOS({
        originDeviceId: 'WEB_CITIZEN_' + Math.floor(1000 + Math.random() * 9000),
        userName: currentUser.fullName || currentUser.name || 'Rahul Sharma',
        userPhone: currentUser.phone || '9876543210',
        type: 'MEDICAL',
        severity: 'CRITICAL',
        description: 'Immediate distress beacon dispatched from Citizen Web Portal',
        peopleCount: 1,
        injuredCount: 0,
        latitude: 23.0395,
        longitude: 72.5082,
        accuracy: 10,
        addressText: `${currentUser.city || 'Ahmedabad'}, ${currentUser.state || 'Gujarat'} (SG Highway)`,
        source: 'ONLINE',
      });
    } catch (e) {
      console.error('Failed to trigger SOS API:', e);
    }
    onTriggerSos();
  };

  // Press & hold handler for SOS
  const startHold = () => {
    setIsHolding(true);
    setHoldProgress(0);
    const startTime = Date.now();
    const duration = 2000; // 2 seconds hold to trigger

    if (holdIntervalRef.current) clearInterval(holdIntervalRef.current);

    holdIntervalRef.current = window.setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min((elapsed / duration) * 100, 100);
      setHoldProgress(progress);

      if (progress >= 100) {
        if (holdIntervalRef.current) clearInterval(holdIntervalRef.current);
        setIsHolding(false);
        setHoldProgress(0);
        dispatchLiveSOS();
      }
    }, 50);
  };

  const endHold = () => {
    if (holdIntervalRef.current) clearInterval(holdIntervalRef.current);
    setIsHolding(false);
    setHoldProgress(0);
  };

  return (
    <div className="w-full flex-1 flex flex-col justify-between px-5 pt-3 pb-20 select-none">
      {/* Top User Profile Bar */}
      <div className="flex items-center justify-between mt-1 mb-3" data-purpose="user-header">
        <div className="flex items-center gap-3">
          {/* Profile Avatar Icon */}
          <button
            type="button"
            onClick={() => onNavigate('settings')}
            className="w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center text-rose-500 overflow-hidden shadow-inner shrink-0 hover:opacity-90 transition-opacity border border-slate-200 cursor-pointer"
            aria-label="User Avatar"
          >
            {currentUser.avatarUrl ? (
              <img
                src={currentUser.avatarUrl}
                alt={currentUser.fullName || currentUser.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <svg className="w-7 h-7 fill-current translate-y-1" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
            )}
          </button>

          {/* Greetings & Location */}
          <div className="leading-tight text-left">
            <p className="text-xs font-normal text-slate-500">Hello,</p>
            <h1 className="text-base font-bold text-slate-900 tracking-tight">
              {currentUser.fullName || currentUser.name || 'Citizen'}
            </h1>
            <button
              type="button"
              onClick={() => setShowLocationPicker(!showLocationPicker)}
              className="inline-flex items-center text-xs font-medium text-slate-600 hover:text-slate-900 mt-0.5"
              aria-label="Change Location"
            >
              <MapPin className="w-3.5 h-3.5 text-red-500 mr-1 fill-red-500 shrink-0" />
              <span>{currentUser.city || 'Ahmedabad'}, {currentUser.state || 'Gujarat'}</span>
              <ChevronDown className="w-3 h-3 text-slate-500 ml-1" />
            </button>
          </div>
        </div>

        {/* Notifications Icon Button */}
        <button
          type="button"
          onClick={() => onNavigate('history')}
          className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-700 hover:bg-slate-200 transition-colors relative"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white animate-pulse" />
        </button>
      </div>

      {/* Location Dropdown Modal */}
      {showLocationPicker && (
        <div className="mb-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-md flex items-center justify-between text-xs animate-in fade-in">
          <div>
            <span className="text-slate-500 block text-[10px]">Detected GPS Location</span>
            <strong className="text-slate-800 font-semibold">
              {currentUser.address || 'Sarkhej - Gandhinagar Hwy'}, {currentUser.city || 'Ahmedabad'} 380015
            </strong>
          </div>
          <button
            type="button"
            onClick={() => setShowLocationPicker(false)}
            className="px-2.5 py-1 bg-red-50 text-red-600 font-semibold rounded-lg hover:bg-red-100"
          >
            Verified
          </button>
        </div>
      )}

      {/* Safety Status Banner */}
      <section
        onClick={() => onNavigate('disaster-map')}
        className="bg-[#eef8f2] border border-[#d1edd9] rounded-2xl p-3.5 flex items-center justify-between shadow-xs cursor-pointer hover:bg-[#e7f5ec] transition-colors"
        data-purpose="area-safety-status"
      >
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 bg-[#2cb563] rounded-full flex items-center justify-center text-white shadow-md shadow-green-500/20 shrink-0">
            <ShieldCheck className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div className="text-left">
            <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase">YOUR AREA IS</p>
            <h2 className="text-xl font-black text-[#155a30] leading-none tracking-tight">SAFE</h2>
            <p className="text-xs text-slate-600 font-normal mt-0.5">No immediate threats reported</p>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-slate-400 mr-1 shrink-0 stroke-[2.2]" />
      </section>

      {/* Emergency SOS Section */}
      <section className="my-3 flex flex-col items-center justify-center relative" data-purpose="emergency-sos-callout">
        {/* Concentric Pulsing Light Red Rings */}
        <div className="relative flex items-center justify-center">
          <div className="absolute w-64 h-64 rounded-full bg-rose-100/60 animate-ring pointer-events-none" />
          <div className="absolute w-56 h-56 rounded-full bg-rose-200/50 pointer-events-none" />

          {/* Hold Progress Ring */}
          {isHolding && (
            <svg className="absolute w-48 h-48 pointer-events-none z-20 -rotate-90">
              <circle
                cx="96"
                cy="96"
                r="86"
                stroke="rgba(255, 255, 255, 0.4)"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="96"
                cy="96"
                r="86"
                stroke="#ffffff"
                strokeWidth="8"
                fill="none"
                strokeDasharray="540"
                strokeDashoffset={540 - (540 * holdProgress) / 100}
                strokeLinecap="round"
                className="transition-all duration-75"
              />
            </svg>
          )}

          {/* SOS Red Button */}
          <button
            type="button"
            aria-label="Emergency SOS button"
            onMouseDown={startHold}
            onMouseUp={endHold}
            onMouseLeave={endHold}
            onTouchStart={startHold}
            onTouchEnd={endHold}
            onClick={dispatchLiveSOS}
            className={`sos-gradient relative z-10 w-44 h-44 rounded-full flex flex-col items-center justify-center text-white cursor-pointer transition-transform duration-150 focus:outline-none ${
              isHolding ? 'scale-105 shadow-2xl' : 'active:scale-95'
            }`}
          >
            <Radio className="w-12 h-12 mb-1.5 stroke-[2.5]" />
            <span className="text-sm font-black tracking-wider uppercase leading-none">EMERGENCY</span>
            <span className="text-base font-black tracking-wider uppercase mt-1">SOS</span>
          </button>
        </div>

        {/* Instruction Pill */}
        <div className="mt-3.5 bg-rose-50 border border-rose-100/70 text-rose-600 px-4 py-1.5 rounded-full text-xs font-semibold tracking-tight shadow-xs flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
          {isHolding ? `Holding... ${Math.round(holdProgress)}%` : 'Tap or hold to call for immediate help'}
        </div>
      </section>

      {/* Quick Actions Grid (8 cards matching reference design) */}
      <section className="grid grid-cols-2 gap-2.5" data-purpose="quick-actions">
        {/* Action 1: I Need Help */}
        <button
          type="button"
          onClick={() => onNavigate('need-help')}
          className="bg-white p-3 rounded-2xl shadow-xs border border-slate-100/80 flex items-center justify-between text-left hover:shadow-md transition-all active:scale-[0.98]"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-10 h-10 rounded-full bg-rose-50 text-red-500 flex items-center justify-center shrink-0">
              <MapPin className="w-5 h-5 fill-current" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs font-bold text-slate-900 leading-tight truncate">I NEED HELP</h3>
              <p className="text-[10px] text-slate-500 leading-3 mt-0.5 truncate">Request immediate...</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 shrink-0 ml-1 stroke-[2.5]" />
        </button>

        {/* Action 2: Disaster Map */}
        <button
          type="button"
          onClick={() => onNavigate('disaster-map')}
          className="bg-white p-3 rounded-2xl shadow-xs border border-slate-100/80 flex items-center justify-between text-left hover:shadow-md transition-all active:scale-[0.98]"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <Map className="w-5 h-5 stroke-[2.2]" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs font-bold text-slate-900 leading-tight truncate">DISASTER MAP</h3>
              <p className="text-[10px] text-slate-500 leading-3 mt-0.5 truncate">View live updates in area</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 shrink-0 ml-1 stroke-[2.5]" />
        </button>

        {/* Action 3: Safe Shelters */}
        <button
          type="button"
          onClick={() => onNavigate('safe-shelters')}
          className="bg-white p-3 rounded-2xl shadow-xs border border-slate-100/80 flex items-center justify-between text-left hover:shadow-md transition-all active:scale-[0.98]"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-10 h-10 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <Home className="w-5 h-5 fill-current" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs font-bold text-slate-900 leading-tight truncate">SAFE SHELTERS</h3>
              <p className="text-[10px] text-slate-500 leading-3 mt-0.5 truncate">Find nearby safe locations</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 shrink-0 ml-1 stroke-[2.5]" />
        </button>

        {/* Action 4: Medical Help */}
        <button
          type="button"
          onClick={() => onNavigate('medical-help')}
          className="bg-white p-3 rounded-2xl shadow-xs border border-slate-100/80 flex items-center justify-between text-left hover:shadow-md transition-all active:scale-[0.98]"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-10 h-10 rounded-full bg-red-50 text-red-600 flex items-center justify-center shrink-0">
              <Plus className="w-5 h-5 stroke-[3]" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs font-bold text-slate-900 leading-tight truncate">MEDICAL HELP</h3>
              <p className="text-[10px] text-slate-500 leading-3 mt-0.5 truncate">Hospitals & medical...</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 shrink-0 ml-1 stroke-[2.5]" />
        </button>

        {/* Action 5: Official Alerts */}
        <button
          type="button"
          onClick={() => onNavigate('history')}
          className="bg-white p-3 rounded-2xl shadow-xs border border-slate-100/80 flex items-center justify-between text-left hover:shadow-md transition-all active:scale-[0.98]"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-10 h-10 rounded-full bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
              <Megaphone className="w-5 h-5 stroke-[2.2]" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs font-bold text-slate-900 leading-tight truncate">OFFICIAL ALERTS</h3>
              <p className="text-[10px] text-slate-500 leading-3 mt-0.5 truncate">Latest updates from auth</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 shrink-0 ml-1 stroke-[2.5]" />
        </button>

        {/* Action 6: Emergency Chat */}
        <button
          type="button"
          onClick={() => onNavigate('emergency-chat')}
          className="bg-white p-3 rounded-2xl shadow-xs border border-slate-100/80 flex items-center justify-between text-left hover:shadow-md transition-all active:scale-[0.98]"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-10 h-10 rounded-full bg-purple-50 text-indigo-500 flex items-center justify-center shrink-0">
              <MessageSquare className="w-5 h-5 fill-current" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs font-bold text-slate-900 leading-tight truncate">EMERGENCY CHAT</h3>
              <p className="text-[10px] text-slate-500 leading-3 mt-0.5 truncate">Connect with rescue teams</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 shrink-0 ml-1 stroke-[2.5]" />
        </button>

        {/* Action 7: Offline Network */}
        <button
          type="button"
          onClick={() => onNavigate('offline-network')}
          className="bg-white p-3 rounded-2xl shadow-xs border border-slate-100/80 flex items-center justify-between text-left hover:shadow-md transition-all active:scale-[0.98]"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-10 h-10 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center shrink-0">
              <Wifi className="w-5 h-5 stroke-[2.2]" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs font-bold text-slate-900 leading-tight truncate">OFFLINE NETWORK</h3>
              <p className="text-[10px] text-slate-500 leading-3 mt-0.5 truncate">Stay connected...</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 shrink-0 ml-1 stroke-[2.5]" />
        </button>

        {/* Action 8: Report Incident */}
        <button
          type="button"
          onClick={() => onNavigate('report-incident')}
          className="bg-white p-3 rounded-2xl shadow-xs border border-slate-100/80 flex items-center justify-between text-left hover:shadow-md transition-all active:scale-[0.98]"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-10 h-10 rounded-full bg-orange-50 text-orange-500 flex items-center justify-center shrink-0">
              <Camera className="w-5 h-5 fill-current" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs font-bold text-slate-900 leading-tight truncate">REPORT INCIDENT</h3>
              <p className="text-[10px] text-slate-500 leading-3 mt-0.5 truncate">Share photos and location</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 shrink-0 ml-1 stroke-[2.5]" />
        </button>
      </section>
    </div>
  );
};
