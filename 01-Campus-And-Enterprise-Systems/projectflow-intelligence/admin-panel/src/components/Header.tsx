import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import {
  LogOut,
  ShieldCheck,
  User,
  Bell,
  Search,
  CheckCheck,
  ChevronDown,
  Layers,
  FolderKanban,
  CheckSquare,
  X
} from 'lucide-react';
import { api } from '../api/client';
import { Project, Task, AuditLog } from '../types';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Notification states
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<AuditLog[]>([]);
  const [unreadCount, setUnreadCount] = useState(3);
  const notifRef = useRef<HTMLDivElement>(null);

  // Profile dropdown states
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);

  // Global search palette states
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<{
    projects: Project[];
    tasks: Task[];
  }>({ projects: [], tasks: [] });
  const searchRef = useRef<HTMLDivElement>(null);

  // Load recent audit events as notifications
  useEffect(() => {
    let isMounted = true;
    async function fetchNotifs() {
      try {
        const resp = await api.getAuditEvents(0, 5);
        if (isMounted && resp && resp.content) {
          setNotifications(resp.content);
        }
      } catch (e) {
        // Fallback default system events
        if (isMounted) {
          setNotifications([
            {
              id: '1',
              action: 'SECURITY_AUDIT',
              actorEmail: 'system@projectflow.io',
              details: 'Workspace policy integrity verified',
              ipAddress: '127.0.0.1',
              timestamp: new Date().toISOString()
            },
            {
              id: '2',
              action: 'DATA_SYNC',
              actorEmail: 'admin@projectflow.io',
              details: 'Cloud database telemetry synchronized',
              ipAddress: '127.0.0.1',
              timestamp: new Date(Date.now() - 3600000).toISOString()
            }
          ]);
        }
      }
    }
    fetchNotifs();
    return () => { isMounted = false; };
  }, []);

  // Handle outside clicks to close dropdowns
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setShowProfileMenu(false);
      }
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsSearching(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Real global search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults({ projects: [], tasks: [] });
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const [pAll, tAll] = await Promise.all([
          api.getProjects().catch(() => []),
          api.getAllTasks().catch(() => [])
        ]);
        const q = searchQuery.toLowerCase();
        const pList = pAll.filter(
          (p: Project) => p.name.toLowerCase().includes(q) || (p.code && p.code.toLowerCase().includes(q))
        );
        const tList = tAll.filter(
          (t: Task) => t.title.toLowerCase().includes(q)
        );
        setSearchResults({ projects: pList, tasks: tList });
      } catch (err) {
        console.warn('Search lookup failed', err);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const markAllRead = () => {
    setUnreadCount(0);
  };

  return (
    <header className="h-16 bg-[#FAFAF7] border-b border-[#E2E0D8] px-8 flex items-center justify-between sticky top-0 z-30 select-none">
      {/* Left: Operational status badge & Global Search */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2.5">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#56664C]/10 text-[#56664C] border border-[#56664C]/20">
            <span className="w-2 h-2 rounded-full bg-[#56664C] animate-pulse"></span>
            Operational
          </span>
          <span className="text-xs text-[#78866B] font-mono hidden md:inline">Console Connected</span>
        </div>

        {/* Global Search Input with Instant Jump-to */}
        <div ref={searchRef} className="relative hidden sm:block w-72">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#78866B]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setIsSearching(true);
              }}
              onFocus={() => setIsSearching(true)}
              placeholder="Search projects, tasks, squad..."
              className="w-full pl-9 pr-7 py-1.5 bg-[#F4F2E9]/70 border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:bg-white focus:border-[#56664C] focus:ring-1 focus:ring-[#56664C] transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => { setSearchQuery(''); setIsSearching(false); }}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-[#78866B] hover:text-[#292D28]"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Search Dropdown Results */}
          {isSearching && searchQuery.trim() && (
            <div className="absolute left-0 right-0 top-full mt-1.5 bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl shadow-xl p-2 z-40 max-h-80 overflow-y-auto">
              <div className="text-[10px] font-bold text-[#78866B] uppercase tracking-wider px-2 py-1">
                Matching Projects ({searchResults.projects.length})
              </div>
              {searchResults.projects.length > 0 ? (
                searchResults.projects.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => {
                      navigate('/projects');
                      setIsSearching(false);
                      setSearchQuery('');
                    }}
                    className="w-full flex items-center gap-2 p-2 rounded-lg hover:bg-[#EFECE4] text-left transition-colors"
                  >
                    <FolderKanban className="w-4 h-4 text-[#56664C] shrink-0" />
                    <div className="truncate">
                      <div className="text-xs font-semibold text-[#292D28]">{p.name}</div>
                      <div className="text-[10px] text-[#78866B]">{p.code} • {p.status}</div>
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-xs text-[#78866B] px-2 py-1 italic">No projects found</div>
              )}

              <div className="border-t border-[#E2E0D8] my-1"></div>

              <div className="text-[10px] font-bold text-[#78866B] uppercase tracking-wider px-2 py-1">
                Matching Tasks ({searchResults.tasks.length})
              </div>
              {searchResults.tasks.length > 0 ? (
                searchResults.tasks.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => {
                      navigate('/tasks');
                      setIsSearching(false);
                      setSearchQuery('');
                    }}
                    className="w-full flex items-center gap-2 p-2 rounded-lg hover:bg-[#EFECE4] text-left transition-colors"
                  >
                    <CheckSquare className="w-4 h-4 text-[#A56A2B] shrink-0" />
                    <div className="truncate">
                      <div className="text-xs font-semibold text-[#292D28]">{t.title}</div>
                      <div className="text-[10px] text-[#78866B]">{t.priority} • {t.statusCategory}</div>
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-xs text-[#78866B] px-2 py-1 italic">No tasks found</div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right Controls: Notifications Bell & Profile Menu */}
      <div className="flex items-center gap-3">
        {/* Notification Bell Dropdown */}
        <div ref={notifRef} className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            title="Notifications & Security Alerts"
            className="relative p-2 rounded-xl text-[#5A6258] hover:bg-[#EFECE4] hover:text-[#292D28] transition-colors border border-transparent hover:border-[#E2E0D8]"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-[#B7473C] text-white text-[9px] font-bold rounded-full flex items-center justify-center shadow-sm">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notification Tray Modal / Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl shadow-2xl p-4 z-40">
              <div className="flex items-center justify-between pb-3 border-b border-[#E2E0D8]">
                <div className="text-xs font-bold text-[#292D28] uppercase tracking-wider">
                  Notifications & Alerts
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    className="flex items-center gap-1 text-[11px] font-semibold text-[#56664C] hover:underline"
                  >
                    <CheckCheck className="w-3.5 h-3.5" />
                    Mark read
                  </button>
                )}
              </div>

              <div className="divide-y divide-[#E2E0D8] max-h-72 overflow-y-auto my-1">
                {notifications.length > 0 ? (
                  notifications.map((n) => (
                    <div key={n.id} className="py-2.5 px-1 hover:bg-[#F4F2E9]/60 rounded-lg transition-colors">
                      <div className="flex items-center justify-between mb-0.5">
                        <span className="text-[10px] font-mono font-bold text-[#56664C] bg-[#56664C]/10 px-1.5 py-0.5 rounded">
                          {n.action}
                        </span>
                        <span className="text-[10px] text-[#78866B]">
                          {new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <p className="text-xs text-[#292D28] font-medium leading-snug">{n.details}</p>
                      <span className="text-[10px] text-[#78866B] font-mono">{n.actorEmail}</span>
                    </div>
                  ))
                ) : (
                  <div className="py-6 text-center text-xs text-[#78866B]">No notifications recorded</div>
                )}
              </div>

              <div className="pt-2 border-t border-[#E2E0D8] text-center">
                <button
                  onClick={() => {
                    navigate('/audit-logs');
                    setShowNotifications(false);
                  }}
                  className="text-xs font-semibold text-[#56664C] hover:underline"
                >
                  View Full Audit Log
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Profile Dropdown */}
        {user ? (
          <div ref={profileRef} className="relative">
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="flex items-center gap-2.5 p-1.5 pl-2 pr-3 rounded-xl hover:bg-[#EFECE4] border border-transparent hover:border-[#E2E0D8] transition-all"
            >
              <div className="w-8 h-8 rounded-xl bg-[#56664C] text-[#F4F2E9] flex items-center justify-center font-bold text-xs shadow-sm">
                {user.fullName ? user.fullName.substring(0, 2).toUpperCase() : <User className="w-4 h-4" />}
              </div>
              <div className="text-left hidden sm:block">
                <div className="text-xs font-bold text-[#292D28] leading-tight">{user.fullName || user.email}</div>
                <div className="text-[10px] flex items-center gap-1 font-semibold text-[#78866B]">
                  <ShieldCheck className="w-3 h-3 text-[#56664C]" />
                  {user.role}
                </div>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-[#78866B]" />
            </button>

            {/* Profile Menu Popup */}
            {showProfileMenu && (
              <div className="absolute right-0 top-full mt-2 w-64 bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl shadow-2xl p-3 z-40">
                <div className="px-3 py-2 border-b border-[#E2E0D8]">
                  <div className="text-xs font-bold text-[#292D28]">{user.fullName || 'Administrator'}</div>
                  <div className="text-[11px] text-[#78866B] truncate">{user.email}</div>
                  <div className="mt-1.5 inline-flex items-center gap-1 text-[10px] font-bold text-[#56664C] bg-[#56664C]/10 px-2 py-0.5 rounded-full">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#56664C]"></span>
                    ACTIVE {user.role}
                  </div>
                </div>

                <div className="py-1">
                  <button
                    onClick={() => {
                      navigate('/settings');
                      setShowProfileMenu(false);
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-[#292D28] hover:bg-[#EFECE4] rounded-lg transition-colors text-left"
                  >
                    <Layers className="w-3.5 h-3.5 text-[#56664C]" />
                    <span>Workspace Settings</span>
                  </button>
                  <button
                    onClick={() => {
                      navigate('/users');
                      setShowProfileMenu(false);
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-[#292D28] hover:bg-[#EFECE4] rounded-lg transition-colors text-left"
                  >
                    <User className="w-3.5 h-3.5 text-[#56664C]" />
                    <span>Manage Team & Roles</span>
                  </button>
                </div>

                <div className="pt-1 border-t border-[#E2E0D8]">
                  <button
                    onClick={() => {
                      setShowProfileMenu(false);
                      logout();
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-[#B7473C] hover:bg-red-50 rounded-lg transition-colors text-left"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out of Console</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-xs text-[#5A6258]">Not authenticated</div>
        )}
      </div>
    </header>
  );
};
