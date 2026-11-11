import React from 'react';
import { useApp } from '../../context/AppContext';
import type { PageView } from '../../types';
import {
  LayoutDashboard,
  Users,
  UserCheck,
  UserMinus,
  UserX,
  Heart,
  Repeat,
  TrendingUp,
  History,
  FileText,
  UserCog,
  UploadCloud,
  Shield,
  Settings,
  Activity,
  Layers,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onCloseMobile: () => void;
}

interface NavItem {
  id: PageView;
  label: string;
  icon: React.ElementType;
  badge?: number | string;
  badgeColor?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onCloseMobile }) => {
  const { currentPage, setCurrentPage, comparison, snapshots, activeSnapshot } = useApp();

  const handleNav = (page: PageView) => {
    setCurrentPage(page);
    onCloseMobile();
  };

  const navSections: { title: string; items: NavItem[] }[] = [
    {
      title: 'OVERVIEW',
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
      ],
    },
    {
      title: 'INSTAGRAM',
      items: [
        {
          id: 'followers',
          label: 'Followers',
          icon: Users,
          badge: activeSnapshot ? activeSnapshot.followersCount : undefined,
        },
        {
          id: 'following',
          label: 'Following',
          icon: UserCheck,
          badge: activeSnapshot ? activeSnapshot.followingCount : undefined,
        },
        {
          id: 'unfollowers',
          label: 'Unfollowers',
          icon: UserMinus,
          badge: comparison?.hasPreviousSnapshot ? comparison.unfollowers.length : undefined,
          badgeColor: 'text-[#EF4444] bg-[#EF4444]/15',
        },
        {
          id: 'not-following-back',
          label: 'Not Following Back',
          icon: UserX,
          badge: comparison ? comparison.notFollowingBack.length : undefined,
          badgeColor: 'text-[#F59E0B] bg-[#F59E0B]/15',
        },
        {
          id: 'fans',
          label: 'Your Fans',
          icon: Heart,
          badge: comparison ? comparison.fans.length : undefined,
          badgeColor: 'text-[#6366F1] bg-[#6366F1]/15',
        },
        {
          id: 'mutuals',
          label: 'Mutual Followers',
          icon: Repeat,
          badge: comparison ? comparison.mutuals.length : undefined,
          badgeColor: 'text-[#22C55E] bg-[#22C55E]/15',
        },
      ],
    },
    {
      title: 'ANALYTICS',
      items: [
        { id: 'analytics', label: 'Follower Growth', icon: TrendingUp },
        {
          id: 'history',
          label: 'History & Snapshots',
          icon: History,
          badge: snapshots.length > 0 ? snapshots.length : undefined,
        },
        { id: 'reports', label: 'Export Reports', icon: FileText },
      ],
    },
    {
      title: 'MANAGEMENT',
      items: [
        {
          id: 'smart-unfollow',
          label: 'Smart Unfollow Manager',
          icon: UserCog,
        },
      ],
    },
    {
      title: 'SETTINGS',
      items: [
        { id: 'import', label: 'Import Data', icon: UploadCloud },
        { id: 'privacy', label: 'Privacy & Security', icon: Shield },
        { id: 'settings', label: 'Settings', icon: Settings },
      ],
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-black/60 z-40 lg:hidden backdrop-blur-xs"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-64 bg-[#10141D] border-r border-[#252B38] flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-6 flex items-center justify-between border-b border-[#252B38]">
          <button
            onClick={() => handleNav('landing')}
            className="flex items-center space-x-2.5 text-left focus:outline-none group"
          >
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#8B5CF6] to-[#6366F1] flex items-center justify-center text-white shadow-lg shadow-[#8B5CF6]/30 group-hover:scale-105 transition-transform">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-base tracking-wider text-[#F8FAFC]">
                FOLLOW<span className="text-[#8B5CF6]">TRACK</span>
              </span>
              <span className="block text-[10px] text-[#94A3B8] font-medium leading-none">
                Analytics Platform
              </span>
            </div>
          </button>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
          {navSections.map((section) => (
            <div key={section.title} className="space-y-1">
              <span className="text-[10px] font-bold text-[#94A3B8] tracking-wider px-3 uppercase">
                {section.title}
              </span>

              <div className="space-y-0.5 mt-1">
                {section.items.map((item) => {
                  const isActive = currentPage === item.id;
                  const Icon = item.icon;

                  return (
                    <button
                      key={item.id}
                      onClick={() => handleNav(item.id)}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all group ${
                        isActive
                          ? 'bg-[#8B5CF6] text-white shadow-md shadow-[#8B5CF6]/20'
                          : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#151B27]'
                      }`}
                    >
                      <div className="flex items-center space-x-2.5 min-w-0">
                        <Icon
                          className={`w-4 h-4 transition-colors ${
                            isActive ? 'text-white' : 'text-[#94A3B8] group-hover:text-[#F8FAFC]'
                          }`}
                        />
                        <span className="truncate">{item.label}</span>
                      </div>

                      {item.badge !== undefined && (
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0 ${
                            isActive
                              ? 'bg-white/20 text-white'
                              : item.badgeColor || 'bg-[#151B27] text-[#94A3B8]'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Active Snapshot Indicator Footer */}
        <div className="p-4 border-t border-[#252B38] bg-[#0B0D12]/50">
          {activeSnapshot ? (
            <div className="space-y-1">
              <div className="flex items-center justify-between text-[11px] text-[#94A3B8]">
                <span className="flex items-center space-x-1">
                  <Layers className="w-3.5 h-3.5 text-[#8B5CF6]" />
                  <span>Active Snapshot</span>
                </span>
                <span className="w-2 h-2 rounded-full bg-[#22C55E]"></span>
              </div>
              <p className="text-xs font-semibold text-[#F8FAFC] truncate">
                {activeSnapshot.name}
              </p>
              <p className="text-[10px] text-[#94A3B8]">
                {new Date(activeSnapshot.createdAt).toLocaleDateString()} • {activeSnapshot.followersCount} followers
              </p>
            </div>
          ) : (
            <div className="text-center py-1">
              <button
                onClick={() => handleNav('import')}
                className="w-full flex items-center justify-center space-x-1.5 py-2 px-3 bg-[#151B27] hover:bg-[#1C2433] border border-[#252B38] rounded-xl text-xs font-medium text-[#8B5CF6] transition-colors"
              >
                <UploadCloud className="w-3.5 h-3.5" />
                <span>Import Instagram Data</span>
              </button>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
