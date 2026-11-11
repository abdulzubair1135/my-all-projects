import React, { useState } from 'react';
import {
  ShieldAlert,
  Radio,
  Building2,
  HeartHandshake,
  FileText,
  Settings,
  Smartphone,
  ChevronDown,
  UserCheck,
  LogOut,
  KeyRound,
  BellRing
} from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  isConnected: boolean;
  activeSOSCount: number;
  currentUser?: any;
  onSignOut?: () => void;
  onSimulateSOS?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onSelectTab,
  isConnected,
  activeSOSCount,
  currentUser,
  onSignOut,
  onSimulateSOS
}) => {
  const [showPortalMenu, setShowPortalMenu] = useState(false);

  const tabs = [
    { id: 'gov', label: 'Government Command', icon: ShieldAlert, badge: activeSOSCount > 0 ? activeSOSCount : undefined },
    { id: 'alerts', label: 'Official Alerts', icon: BellRing },
    { id: 'ngo', label: 'NGO Relief Operations', icon: HeartHandshake },
    { id: 'admin', label: 'Admin & Incident Center', icon: Settings },
    { id: 'rescue', label: 'NDRF Rescue Teams', icon: Radio },
    { id: 'hospital', label: 'Hospital Beds & ICU', icon: Building2 },
    { id: 'reports', label: 'Citizen Reports', icon: FileText },
    { id: 'citizen', label: 'Citizen App (Mobile View)', icon: Smartphone },
  ];

  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectTab('gov')}>
            <div className="w-10 h-10 rounded-xl bg-white/10 border border-slate-700 flex items-center justify-center p-1 shadow-lg shadow-red-900/30">
              <img src="/sahay_logo.png" alt="Sahay" className="w-8 h-8 object-contain drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-black text-xl tracking-tight text-white">Sahay</span>
                <span className="text-[10px] uppercase font-black tracking-wider px-2 py-0.5 rounded-full bg-red-600/20 text-red-400 border border-red-500/30">
                  Command Platform
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                When the Network Fails, Sahay Doesn&apos;t.
              </p>
            </div>
          </div>

          {/* Action & status badges */}
          <div className="flex items-center space-x-3 relative">
            {onSimulateSOS && (
              <button
                onClick={onSimulateSOS}
                type="button"
                className="bg-red-600 hover:bg-red-700 active:scale-95 text-white text-xs font-black uppercase tracking-wider px-3 py-1.5 rounded-lg shadow-lg shadow-red-600/40 flex items-center space-x-1.5 transition-all border border-red-400/40 animate-pulse"
              >
                <span>🚨</span>
                <span className="hidden sm:inline">Test Live SOS</span>
              </button>
            )}

            {/* Portal Switcher / Login Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowPortalMenu(!showPortalMenu)}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold px-3 py-1.5 rounded-lg border border-slate-700 flex items-center space-x-1.5 transition-all"
              >
                <KeyRound className="w-3.5 h-3.5 text-red-400" />
                <span className="hidden md:inline">Portals / Login</span>
                <ChevronDown className="w-3 h-3 text-slate-400" />
              </button>

              {showPortalMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl p-2 z-50 text-xs animate-in fade-in space-y-1">
                  <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800">
                    Official Login Portals
                  </div>
                  <button
                    onClick={() => {
                      onSelectTab('gov-login');
                      setShowPortalMenu(false);
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800 flex items-center space-x-2 text-slate-200 hover:text-emerald-400"
                  >
                    <Building2 className="w-3.5 h-3.5" />
                    <span>Government Officer Portal</span>
                  </button>
                  <button
                    onClick={() => {
                      onSelectTab('ngo-login');
                      setShowPortalMenu(false);
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800 flex items-center space-x-2 text-slate-200 hover:text-amber-400"
                  >
                    <HeartHandshake className="w-3.5 h-3.5" />
                    <span>NGO Relief Portal</span>
                  </button>
                  <button
                    onClick={() => {
                      onSelectTab('admin-login');
                      setShowPortalMenu(false);
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800 flex items-center space-x-2 text-slate-200 hover:text-blue-400"
                  >
                    <Settings className="w-3.5 h-3.5" />
                    <span>Admin Incident Center</span>
                  </button>
                  <button
                    onClick={() => {
                      onSelectTab('citizen-login');
                      setShowPortalMenu(false);
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800 flex items-center space-x-2 text-slate-200 hover:text-red-400"
                  >
                    <Smartphone className="w-3.5 h-3.5" />
                    <span>Citizen Portal (Email OTP)</span>
                  </button>

                  {currentUser && (
                    <div className="pt-1.5 border-t border-slate-800">
                      <div className="px-3 py-1 text-[10px] text-slate-400 truncate">
                        Logged in as: <strong className="text-white">{currentUser.name || currentUser.email}</strong>
                      </div>
                      <button
                        onClick={() => {
                          if (onSignOut) onSignOut();
                          setShowPortalMenu(false);
                        }}
                        className="w-full text-left px-3 py-1.5 rounded-xl hover:bg-red-500/20 text-red-400 flex items-center space-x-2"
                      >
                        <LogOut className="w-3.5 h-3.5" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
              isConnected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
            }`}>
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'}`} />
              <span className="hidden sm:inline">{isConnected ? 'LIVE ENGINE' : 'RECONNECTING...'}</span>
            </div>
          </div>
        </div>

        {/* Role Navigation Bar */}
        <div className="flex space-x-1 overflow-x-auto py-2 border-t border-slate-800/80 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-red-600 text-white shadow-md shadow-red-600/30'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                {tab.badge !== undefined && (
                  <span className="ml-1.5 px-1.5 py-0.2 text-[10px] font-bold rounded-full bg-white text-red-600">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
