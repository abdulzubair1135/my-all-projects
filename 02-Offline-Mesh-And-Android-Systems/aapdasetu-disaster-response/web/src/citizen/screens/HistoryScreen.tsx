import React, { useState } from 'react';
import {
  Filter,
  ChevronDown,
  MapPin,
  Camera,
  MessageSquare,
  ChevronRight,
  Plus,
  Home,
  CheckCircle2,
  Clock,
  XCircle,
  Calendar,
  ShieldAlert,
} from 'lucide-react';
import { ActivityItem } from '../types';

interface HistoryScreenProps {
  activities: ActivityItem[];
  onSelectActivity?: (activity: ActivityItem) => void;
}

export const HistoryScreen: React.FC<HistoryScreenProps> = ({ activities, onSelectActivity }) => {
  const [activeCategory, setActiveCategory] = useState<'All' | 'Help Requests' | 'Reports' | 'Chats'>('All');
  const [filterDropdownOpen, setFilterDropdownOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('All Activities');
  const [selectedItem, setSelectedItem] = useState<ActivityItem | null>(null);

  const filteredList = activities.filter((act) => {
    // Filter by tab
    if (activeCategory === 'Help Requests' && act.type !== 'help-request' && act.type !== 'medical-help') return false;
    if (activeCategory === 'Reports' && act.type !== 'report') return false;
    if (activeCategory === 'Chats' && act.type !== 'chat') return false;

    // Filter by dropdown status
    if (statusFilter === 'Resolved' && act.status !== 'Resolved') return false;
    if (statusFilter === 'In Review' && act.status !== 'In Review') return false;
    if (statusFilter === 'Completed' && act.status !== 'Completed') return false;
    if (statusFilter === 'Cancelled' && act.status !== 'Cancelled') return false;

    return true;
  });

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-[#f6f8fa] select-none">
      {/* Header Section */}
      <div className="px-5 pt-3 pb-3 bg-white border-b border-slate-100 shrink-0">
        <div className="relative flex items-center justify-between">
          <div className="w-full text-center pr-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">History</h1>
            <p className="text-xs text-slate-500 mt-0.5 font-normal">View your past requests, reports and activity</p>
          </div>

          {/* Top-right Filter Dropdown */}
          <button
            type="button"
            onClick={() => setFilterDropdownOpen(!filterDropdownOpen)}
            className="absolute right-0 top-0 flex items-center space-x-1.5 border border-slate-200 bg-white shadow-xs px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-700 active:scale-95 transition-transform"
          >
            <Filter className="w-3.5 h-3.5 text-slate-600" />
            <span className="text-[11px] truncate max-w-[80px]">{statusFilter}</span>
            <ChevronDown className="w-3 h-3 text-slate-500 ml-0.5" />
          </button>
        </div>

        {/* Dropdown Options */}
        {filterDropdownOpen && (
          <div className="absolute right-5 top-12 bg-white border border-slate-200 shadow-xl rounded-xl p-1 z-30 w-36 text-xs text-left animate-in fade-in">
            {['All Activities', 'Resolved', 'In Review', 'Completed', 'Cancelled'].map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => {
                  setStatusFilter(status);
                  setFilterDropdownOpen(false);
                }}
                className={`w-full text-left px-3 py-1.5 rounded-lg hover:bg-slate-100 ${
                  statusFilter === status ? 'font-bold text-red-600' : 'text-slate-700'
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        )}

        {/* Category Tabs */}
        <div className="flex items-center space-x-2 mt-4 overflow-x-auto no-scrollbar py-0.5 select-none">
          <button
            type="button"
            onClick={() => setActiveCategory('All')}
            className={`shrink-0 px-4 py-2 text-xs rounded-xl shadow-xs transition-all ${
              activeCategory === 'All'
                ? 'bg-red-50 text-red-600 border border-red-300 font-semibold'
                : 'bg-white text-slate-700 border border-slate-200 font-medium hover:bg-slate-50'
            }`}
          >
            All
          </button>

          <button
            type="button"
            onClick={() => setActiveCategory('Help Requests')}
            className={`shrink-0 px-3.5 py-2 text-xs rounded-xl flex items-center space-x-1.5 shadow-2xs transition-all ${
              activeCategory === 'Help Requests'
                ? 'bg-red-50 text-red-600 border border-red-300 font-semibold'
                : 'bg-white text-slate-700 border border-slate-200 font-medium hover:bg-slate-50'
            }`}
          >
            <MapPin className="w-3.5 h-3.5 text-red-500 fill-current" />
            <span>Help Requests</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveCategory('Reports')}
            className={`shrink-0 px-3.5 py-2 text-xs rounded-xl flex items-center space-x-1.5 shadow-2xs transition-all ${
              activeCategory === 'Reports'
                ? 'bg-red-50 text-red-600 border border-red-300 font-semibold'
                : 'bg-white text-slate-700 border border-slate-200 font-medium hover:bg-slate-50'
            }`}
          >
            <Camera className="w-3.5 h-3.5 text-slate-600" />
            <span>Reports</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveCategory('Chats')}
            className={`shrink-0 px-3.5 py-2 text-xs rounded-xl flex items-center space-x-1.5 shadow-2xs transition-all ${
              activeCategory === 'Chats'
                ? 'bg-red-50 text-red-600 border border-red-300 font-semibold'
                : 'bg-white text-slate-700 border border-slate-200 font-medium hover:bg-slate-50'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5 text-slate-700 fill-current" />
            <span>Chats</span>
          </button>
        </div>
      </div>

      {/* Main Activity List */}
      <main className="flex-1 px-4 py-3 space-y-3.5 overflow-y-auto pb-24 no-scrollbar">
        {filteredList.map((item) => {
          return (
            <article
              key={item.id}
              role="button"
              tabIndex={0}
              onClick={() => {
                setSelectedItem(item);
                onSelectActivity?.(item);
              }}
              className="bg-white rounded-2xl p-4 shadow-xs border border-slate-100 relative text-left hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {/* Icon */}
                  <div
                    className={`w-11 h-11 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
                      item.type === 'medical-help'
                        ? 'bg-red-50 text-red-500'
                        : item.type === 'report'
                        ? 'bg-orange-50 text-orange-500'
                        : item.type === 'shelter'
                        ? 'bg-emerald-50 text-emerald-600'
                        : item.type === 'chat'
                        ? 'bg-purple-50 text-indigo-500'
                        : 'bg-red-50 text-red-500'
                    }`}
                  >
                    {item.type === 'medical-help' && <Plus className="w-6 h-6 stroke-[3]" />}
                    {item.type === 'report' && <Camera className="w-5 h-5 fill-current" />}
                    {item.type === 'shelter' && <Home className="w-5 h-5 fill-current" />}
                    {item.type === 'chat' && <MessageSquare className="w-5 h-5 fill-current" />}
                    {item.type === 'help-request' && <MapPin className="w-5 h-5 fill-current" />}
                  </div>

                  {/* Title & Details */}
                  <div className="pr-6">
                    <h2 className="text-sm font-bold text-slate-900 leading-snug">{item.title}</h2>
                    <p className="text-xs font-semibold text-slate-700 mt-0.5">{item.subtitle}</p>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">{item.description}</p>
                  </div>
                </div>

                {/* Status Badge */}
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium space-x-1 shrink-0 ${
                    item.status === 'Resolved' || item.status === 'Completed'
                      ? 'bg-emerald-50 text-emerald-700'
                      : item.status === 'In Review'
                      ? 'bg-blue-50 text-blue-600'
                      : 'bg-red-50 text-red-600'
                  }`}
                >
                  {(item.status === 'Resolved' || item.status === 'Completed') && (
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  )}
                  {item.status === 'In Review' && <Clock className="w-3 h-3 text-blue-600" />}
                  {item.status === 'Cancelled' && <XCircle className="w-3 h-3 text-red-600" />}
                  <span>{item.status}</span>
                </span>
              </div>

              {/* Thumbnails if report */}
              {item.images && item.images.length > 0 && (
                <div className="flex items-center space-x-2 mt-3 pl-14">
                  {item.images.slice(0, 3).map((img, i) => (
                    <img
                      key={i}
                      alt={`Incident photo ${i + 1}`}
                      src={img}
                      className="w-16 h-11 rounded-lg object-cover border border-slate-100"
                    />
                  ))}
                  {item.images.length > 3 && (
                    <div className="w-11 h-11 rounded-lg bg-slate-100 flex items-center justify-center text-xs font-semibold text-slate-600 border border-slate-200">
                      +{item.images.length - 3}
                    </div>
                  )}
                </div>
              )}

              {/* Chevron */}
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400">
                <ChevronRight className="w-4 h-4 stroke-[2.5]" />
              </div>

              {/* Footer Meta */}
              <div className="flex items-center text-[11px] text-slate-400 mt-3 pt-2.5 border-t border-slate-50 space-x-3">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{item.date}</span>
                </div>
                <span className="text-slate-300">|</span>
                <div className="flex items-center space-x-1 truncate max-w-[140px]">
                  <MapPin className="w-3 h-3 text-slate-500 fill-current" />
                  <span className="truncate">{item.location}</span>
                </div>
              </div>
            </article>
          );
        })}

        {/* Security Notice Footer */}
        <div className="bg-slate-200/60 rounded-xl p-3 flex items-center justify-center space-x-2 text-slate-600 text-xs mt-4 mb-2">
          <ShieldAlert className="w-4 h-4 text-slate-500 shrink-0" />
          <span className="text-[11.5px] leading-tight font-normal">
            Your history is stored securely and helps us provide better support.
          </span>
        </div>
      </main>

      {/* Activity Details Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full text-left shadow-2xl border border-slate-100">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-[10px] uppercase font-bold text-red-600 tracking-wider">Activity Log Details</span>
                <h3 className="text-base font-bold text-slate-900 mt-0.5">{selectedItem.title}</h3>
                <p className="text-xs text-slate-600 font-semibold">{selectedItem.subtitle}</p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedItem(null)}
                className="text-slate-400 hover:text-slate-700 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-600 mt-3 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
              {selectedItem.description}
            </p>

            <div className="space-y-1.5 my-3 text-xs text-slate-700">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Status</span>
                <strong className="font-semibold text-slate-900">{selectedItem.status}</strong>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Timestamp</span>
                <span>{selectedItem.date}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">Location</span>
                <span className="font-medium text-slate-900">{selectedItem.location}</span>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setSelectedItem(null)}
              className="w-full py-2.5 bg-slate-900 text-white text-xs font-semibold rounded-xl hover:bg-slate-800"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
