import React from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { GitBranch, Terminal, ShieldAlert, Cpu, HardDrive } from 'lucide-react';

export function StatusBar() {
  const { activeProject, processes, pendingApprovals, isConnected, activeTab, setSidebarTab } = useAppStore();

  return (
    <footer className="h-6 bg-ide-sidebar border-t border-ide-border flex items-center justify-between px-3 text-xs text-ide-muted select-none font-mono shrink-0">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-ide-text hover:text-white cursor-pointer">
          <GitBranch className="w-3.5 h-3.5 text-ide-accent" />
          <span>main</span>
        </div>

        {activeProject && (
          <div className="flex items-center gap-1.5 text-ide-text">
            <HardDrive className="w-3.5 h-3.5" />
            <span>{activeProject.name}</span>
          </div>
        )}

        {processes.length > 0 && (
          <div className="flex items-center gap-1.5 text-emerald-400">
            <Cpu className="w-3.5 h-3.5" />
            <span>{processes.length} server{processes.length > 1 ? 's' : ''} running</span>
          </div>
        )}

        <button
          onClick={() => setSidebarTab('qa')}
          className="flex items-center gap-1 text-ide-muted hover:text-blue-400 cursor-pointer transition-colors"
          title="Open Visual QA & ADB Hardware Panel"
        >
          <span>Visual QA</span>
        </button>

        {pendingApprovals.length > 0 && (
          <div className="flex items-center gap-1.5 text-amber-400 font-bold animate-pulse">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{pendingApprovals.length} Approval Pending</span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        {activeTab && (
          <span>{activeTab}</span>
        )}
        <span>UTF-8</span>
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-rose-500'}`} />
          <span>{isConnected ? 'LIVE' : 'DISCONNECTED'}</span>
        </div>
      </div>
    </footer>
  );
}
