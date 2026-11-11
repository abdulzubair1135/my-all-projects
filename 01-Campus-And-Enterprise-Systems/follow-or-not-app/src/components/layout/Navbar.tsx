import React from 'react';
import { useApp } from '../../context/AppContext';
import {
  Menu,
  UploadCloud,
  FileDown,
  Layers,
  ChevronDown,
  ShieldCheck,
} from 'lucide-react';

interface NavbarProps {
  onToggleMobileSidebar: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleMobileSidebar }) => {
  const {
    currentPage,
    setCurrentPage,
    snapshots,
    activeSnapshot,
    setActiveSnapshotId,
    comparison,
  } = useApp();

  const getPageTitle = () => {
    switch (currentPage) {
      case 'landing':
        return 'Overview';
      case 'dashboard':
        return 'Dashboard & Analytics';
      case 'followers':
        return 'Followers List';
      case 'following':
        return 'Following Accounts';
      case 'unfollowers':
        return 'People Who Unfollowed You';
      case 'not-following-back':
        return "Accounts That Don't Follow Back";
      case 'fans':
        return 'Your Fans (You Don’t Follow Back)';
      case 'mutuals':
        return 'Mutual Followers';
      case 'history':
        return 'Snapshot History & Compare';
      case 'analytics':
        return 'Follower Growth Analytics';
      case 'smart-unfollow':
        return 'Smart Unfollow Manager';
      case 'reports':
        return 'Export Reports & Summary';
      case 'settings':
        return 'Application Settings';
      case 'privacy':
        return 'Privacy & Client-Side Architecture';
      case 'import':
        return 'Import Instagram Data';
      default:
        return 'Dashboard';
    }
  };

  return (
    <header className="h-16 bg-[#10141D] border-b border-[#252B38] px-4 md:px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <button
          onClick={onToggleMobileSidebar}
          className="lg:hidden p-2 rounded-xl text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#151B27] transition-colors"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2">
          <span className="text-xs uppercase tracking-wider text-[#94A3B8] hidden sm:inline">
            FollowTrack
          </span>
          <span className="text-xs text-[#252B38] hidden sm:inline">/</span>
          <h1 className="text-sm md:text-base font-bold text-[#F8FAFC]">
            {getPageTitle()}
          </h1>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center space-x-2.5">
        {/* Snapshot Selector (if multiple snapshots exist) */}
        {snapshots.length > 0 && (
          <div className="relative hidden md:flex items-center space-x-1.5 bg-[#151B27] border border-[#252B38] rounded-xl px-2.5 py-1.5 text-xs">
            <Layers className="w-3.5 h-3.5 text-[#8B5CF6]" />
            <select
              value={activeSnapshot?.id || ''}
              onChange={(e) => setActiveSnapshotId(e.target.value)}
              className="bg-transparent text-[#F8FAFC] focus:outline-none cursor-pointer pr-4 font-medium"
            >
              {snapshots.map((s) => (
                <option key={s.id} value={s.id} className="bg-[#151B27] text-[#F8FAFC]">
                  {s.name} ({new Date(s.createdAt).toLocaleDateString()})
                </option>
              ))}
            </select>
            <ChevronDown className="w-3 h-3 text-[#94A3B8] absolute right-2 pointer-events-none" />
          </div>
        )}

        {/* Client-Side Safe Badge */}
        <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-xl bg-[#22C55E]/10 border border-[#22C55E]/20 text-[11px] font-medium text-[#22C55E]">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Local Only</span>
        </div>

        {/* Quick Report Button */}
        {comparison && (
          <button
            onClick={() => setCurrentPage('reports')}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-[#151B27] hover:bg-[#1C2433] text-xs font-medium text-[#F8FAFC] border border-[#252B38] transition-colors"
          >
            <FileDown className="w-3.5 h-3.5 text-[#8B5CF6]" />
            <span className="hidden sm:inline">Export</span>
          </button>
        )}

        {/* Import CTA Button */}
        <button
          onClick={() => setCurrentPage('import')}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-[#8B5CF6] to-[#6366F1] hover:from-[#7C3AED] hover:to-[#4F46E5] text-xs font-semibold text-white shadow-md shadow-[#8B5CF6]/20 transition-all active:scale-95"
        >
          <UploadCloud className="w-3.5 h-3.5" />
          <span>Import Data</span>
        </button>
      </div>
    </header>
  );
};
