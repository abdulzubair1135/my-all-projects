import React from 'react';
import { Home, Bell, Map as MapIcon, FileText, Settings as SettingsIcon } from 'lucide-react';
import { TabType, NavTab } from '../types';

interface BottomNavProps {
  activeTab?: NavTab;
  currentTab?: TabType;
  onChangeTab?: (tab: NavTab) => void;
  onSelectTab?: (tab: TabType) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({
  activeTab,
  currentTab,
  onChangeTab,
  onSelectTab,
}) => {
  const current = activeTab || currentTab || 'home';

  const handleSelect = (tab: NavTab) => {
    if (onChangeTab) onChangeTab(tab);
    if (onSelectTab) onSelectTab(tab);
  };

  return (
    <nav
      className="bg-white/95 backdrop-blur-md border-t border-slate-200/80 px-4 pt-2.5 pb-4 flex justify-between items-center z-30 select-none shadow-sm shrink-0"
      data-purpose="bottom-bar"
    >
      {/* Home Tab */}
      <button
        type="button"
        onClick={() => handleSelect('home')}
        className="flex flex-col items-center group focus:outline-none transition-transform active:scale-95 cursor-pointer"
      >
        <Home
          className={`w-5 h-5 transition-colors ${
            current === 'home' ? 'text-red-600 fill-red-600' : 'text-slate-400 group-hover:text-slate-600'
          }`}
        />
        <span
          className={`text-[11px] mt-1 ${
            current === 'home' ? 'font-bold text-red-600' : 'font-medium text-slate-500 group-hover:text-slate-700'
          }`}
        >
          Home
        </span>
        <div
          className={`w-7 h-0.5 rounded-full mt-0.5 transition-all ${
            current === 'home' ? 'bg-red-600' : 'bg-transparent'
          }`}
        />
      </button>

      {/* Alerts Tab */}
      <button
        type="button"
        onClick={() => handleSelect('alerts')}
        className="flex flex-col items-center group focus:outline-none transition-transform active:scale-95 cursor-pointer"
      >
        <Bell
          className={`w-5 h-5 transition-colors ${
            current === 'alerts' ? 'text-red-600 fill-red-600' : 'text-slate-400 group-hover:text-slate-600'
          }`}
        />
        <span
          className={`text-[11px] mt-1 ${
            current === 'alerts' ? 'font-bold text-red-600' : 'font-medium text-slate-500 group-hover:text-slate-700'
          }`}
        >
          Alerts
        </span>
        <div
          className={`w-7 h-0.5 rounded-full mt-0.5 transition-all ${
            current === 'alerts' ? 'bg-red-600' : 'bg-transparent'
          }`}
        />
      </button>

      {/* Map Tab */}
      <button
        type="button"
        onClick={() => handleSelect('map')}
        className="flex flex-col items-center group focus:outline-none transition-transform active:scale-95 cursor-pointer"
      >
        <MapIcon
          className={`w-5 h-5 transition-colors ${
            current === 'map' ? 'text-red-600 fill-red-600' : 'text-slate-400 group-hover:text-slate-600'
          }`}
        />
        <span
          className={`text-[11px] mt-1 ${
            current === 'map' ? 'font-bold text-red-600' : 'font-medium text-slate-500 group-hover:text-slate-700'
          }`}
        >
          Map
        </span>
        <div
          className={`w-7 h-0.5 rounded-full mt-0.5 transition-all ${
            current === 'map' ? 'bg-red-600' : 'bg-transparent'
          }`}
        />
      </button>

      {/* History Tab */}
      <button
        type="button"
        onClick={() => handleSelect('history')}
        className="flex flex-col items-center group focus:outline-none transition-transform active:scale-95 cursor-pointer"
      >
        <FileText
          className={`w-5 h-5 transition-colors ${
            current === 'history' ? 'text-red-600 fill-red-600' : 'text-slate-400 group-hover:text-slate-600'
          }`}
        />
        <span
          className={`text-[11px] mt-1 ${
            current === 'history' ? 'font-bold text-red-600' : 'font-medium text-slate-500 group-hover:text-slate-700'
          }`}
        >
          History
        </span>
        <div
          className={`w-7 h-0.5 rounded-full mt-0.5 transition-all ${
            current === 'history' ? 'bg-red-600' : 'bg-transparent'
          }`}
        />
      </button>

      {/* Settings Tab */}
      <button
        type="button"
        onClick={() => handleSelect('settings')}
        className="flex flex-col items-center group focus:outline-none transition-transform active:scale-95 cursor-pointer"
      >
        <SettingsIcon
          className={`w-5 h-5 transition-colors ${
            current === 'settings' ? 'text-red-600 fill-red-600' : 'text-slate-400 group-hover:text-slate-600'
          }`}
        />
        <span
          className={`text-[11px] mt-1 ${
            current === 'settings' ? 'font-bold text-red-600' : 'font-medium text-slate-500 group-hover:text-slate-700'
          }`}
        >
          Settings
        </span>
        <div
          className={`w-7 h-0.5 rounded-full mt-0.5 transition-all ${
            current === 'settings' ? 'bg-red-600' : 'bg-transparent'
          }`}
        />
      </button>
    </nav>
  );
};
