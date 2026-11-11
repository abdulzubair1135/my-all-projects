import React from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { ProjectSelector } from './ProjectSelector';
import { TaskGraph } from '../tasks/TaskGraph';
import { FileTree } from '../files/FileTree';
import { EvolutionLab } from './EvolutionLab';
import { QAPanel } from './QAPanel';
import { CheckSquare, FolderTree, Cpu, StopCircle, Brain, Camera } from 'lucide-react';
import { api } from '../../services/api';

export function Sidebar() {
  const { activeSidebarTab, setSidebarTab, processes, refreshProcesses } = useAppStore();

  const handleStopProcess = async (procId) => {
    try {
      await api.stopProcess(procId);
      await refreshProcesses();
    } catch (err) {
      alert(`Error stopping process: ${err.message}`);
    }
  };

  return (
    <aside className="w-80 bg-ide-sidebar border-r border-ide-border flex flex-col h-full shrink-0 select-none">
      <ProjectSelector />

      {/* Tabs */}
      <div className="flex border-b border-ide-border bg-ide-panel/50 text-[11px]">
        <button
          onClick={() => setSidebarTab('tasks')}
          className={`flex-1 py-2 px-1 flex items-center justify-center gap-1 font-medium transition-colors border-b-2 ${
            activeSidebarTab === 'tasks'
              ? 'border-ide-accent text-ide-accent bg-ide-sidebar'
              : 'border-transparent text-ide-muted hover:text-white'
          }`}
          title="Plan & Tasks"
        >
          <CheckSquare className="w-3 h-3" />
          <span>Plan</span>
        </button>

        <button
          onClick={() => setSidebarTab('files')}
          className={`flex-1 py-2 px-1 flex items-center justify-center gap-1 font-medium transition-colors border-b-2 ${
            activeSidebarTab === 'files'
              ? 'border-ide-accent text-ide-accent bg-ide-sidebar'
              : 'border-transparent text-ide-muted hover:text-white'
          }`}
          title="Workspace Files"
        >
          <FolderTree className="w-3 h-3" />
          <span>Files</span>
        </button>

        <button
          onClick={() => setSidebarTab('processes')}
          className={`flex-1 py-2 px-1 flex items-center justify-center gap-1 font-medium transition-colors border-b-2 ${
            activeSidebarTab === 'processes'
              ? 'border-ide-accent text-ide-accent bg-ide-sidebar'
              : 'border-transparent text-ide-muted hover:text-white'
          }`}
          title="Dev Servers"
        >
          <Cpu className="w-3 h-3" />
          <span>Servers</span>
          {processes.length > 0 && (
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          )}
        </button>

        <button
          onClick={() => setSidebarTab('qa')}
          className={`flex-1 py-2 px-1 flex items-center justify-center gap-1 font-medium transition-colors border-b-2 ${
            activeSidebarTab === 'qa'
              ? 'border-blue-400 text-blue-400 bg-ide-sidebar'
              : 'border-transparent text-ide-muted hover:text-blue-300'
          }`}
          title="Visual QA, Snapshots & Android ADB"
        >
          <Camera className="w-3 h-3 text-blue-400" />
          <span>QA</span>
        </button>

        <button
          onClick={() => setSidebarTab('evolution')}
          className={`flex-1 py-2 px-1 flex items-center justify-center gap-1 font-medium transition-colors border-b-2 ${
            activeSidebarTab === 'evolution'
              ? 'border-indigo-400 text-indigo-400 bg-ide-sidebar'
              : 'border-transparent text-ide-muted hover:text-indigo-300'
          }`}
          title="DeepSeek AI Evolution Lab"
        >
          <Brain className="w-3 h-3 text-indigo-400" />
          <span>Evolution</span>
        </button>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeSidebarTab === 'tasks' && <TaskGraph />}
        {activeSidebarTab === 'files' && <FileTree />}
        {activeSidebarTab === 'evolution' && <EvolutionLab />}
        {activeSidebarTab === 'qa' && <QAPanel />}
        {activeSidebarTab === 'processes' && (
          <div className="p-3 flex flex-col gap-2 h-full overflow-y-auto">
            <div className="text-xs text-ide-muted font-semibold uppercase pb-1 border-b border-ide-border">
              Managed Servers ({processes.length})
            </div>
            {processes.length === 0 ? (
              <div className="p-4 text-center text-xs text-ide-muted">
                No active development servers.
              </div>
            ) : (
              processes.map((proc) => (
                <div key={proc.id} className="p-2.5 rounded bg-ide-panel border border-ide-border flex flex-col gap-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white truncate">{proc.name}</span>
                    <button
                      onClick={() => handleStopProcess(proc.id)}
                      className="p-1 hover:bg-rose-500/20 text-rose-400 rounded flex items-center gap-1 text-[11px]"
                    >
                      <StopCircle className="w-3 h-3" />
                      <span>Stop</span>
                    </button>
                  </div>
                  <div className="font-mono text-[10px] text-ide-muted truncate">
                    PID: {proc.pid} | {proc.command}
                  </div>
                  {proc.port && (
                    <div className="flex items-center gap-1 text-[11px] text-emerald-400 font-mono">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      <span>Port {proc.port}</span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </aside>
  );
}
