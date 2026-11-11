import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Layers,
  FolderKanban,
  CheckSquare,
  ShieldAlert,
  Activity,
  HeartPulse,
  Settings,
  Package,
  MessageSquare,
  Radio,
  Calendar
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Workspaces', path: '/workspaces', icon: Layers },
  { name: 'Projects', path: '/projects', icon: FolderKanban },
  { name: 'Tasks Explorer', path: '/tasks', icon: CheckSquare },
  { name: 'Delivery Calendar', path: '/calendar', icon: Calendar },
  { name: 'Persons & Groups', path: '/users', icon: Users, badge: 'LIVE' },
  { name: 'Push Broadcast', path: '/broadcast', icon: Radio },
  { name: 'Risk Radar', path: '/risks', icon: ShieldAlert },
  { name: 'App Releases', path: '/releases', icon: Package },
  { name: 'Audit Logs', path: '/audit-logs', icon: Activity },
  { name: 'System Telemetry', path: '/health', icon: HeartPulse },
  { name: 'Admin Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-[#FAFAF7] border-r border-[#E2E0D8] flex flex-col h-screen sticky top-0 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-[#E2E0D8]">
        <div className="flex items-center gap-3">
          <img src="/logo.jpg" alt="ProjectFlow Logo" style={{ width: '36px', height: '36px', maxWidth: '36px', maxHeight: '36px' }} className="w-9 h-9 rounded-lg object-contain bg-white border border-[#E2E0D8] shadow-sm shrink-0" />
          <div>
            <h1 className="text-base font-semibold text-[#292D28] leading-tight tracking-tight">
              ProjectFlow
            </h1>
            <p className="text-xs text-[#78866B] font-medium tracking-wide uppercase">
              Admin Console
            </p>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-[#78866B] uppercase">
          Management
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-[#56664C] text-[#F4F2E9] shadow-sm'
                    : 'text-[#5A6258] hover:bg-[#EFECE4] hover:text-[#292D28]'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="text-[9px] font-mono font-bold bg-[#47745A] text-white px-1.5 py-0.5 rounded shadow-xs">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#E2E0D8] bg-[#F4F2E9]/60">
        <div className="flex items-center justify-between text-xs text-[#5A6258]">
          <span className="font-medium">Natural Mineral</span>
          <span className="font-mono bg-[#E2E0D8] px-1.5 py-0.5 rounded text-[10px]">v2.0.0</span>
        </div>
      </div>
    </aside>
  );
};
