import React, { useState, useEffect } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { Command, Terminal, Save, Play, Pause, Square, FolderTree, RefreshCw, X } from 'lucide-react';

export function CommandPalette() {
  const { 
    isCommandPaletteOpen, 
    setCommandPaletteOpen, 
    saveCurrentFile, 
    startAgent, 
    pauseAgent, 
    stopAgent, 
    refreshFileTree, 
    setSidebarTab,
    setFileSearchOpen
  } = useAppStore();

  const [search, setSearch] = useState('');

  const commands = [
    {
      id: 'search_files',
      label: 'File: Quick Open / Search File',
      shortcut: 'Ctrl+P',
      icon: <FolderTree className="w-4 h-4 text-ide-accent" />,
      action: () => setFileSearchOpen(true)
    },
    {
      id: 'save_file',
      label: 'File: Save Current File',
      shortcut: 'Ctrl+S',
      icon: <Save className="w-4 h-4 text-emerald-400" />,
      action: () => saveCurrentFile()
    },
    {
      id: 'refresh_files',
      label: 'Explorer: Refresh File Tree',
      icon: <RefreshCw className="w-4 h-4 text-blue-400" />,
      action: () => refreshFileTree()
    },
    {
      id: 'tab_plan',
      label: 'View: Show Plan / Tasks',
      icon: <Command className="w-4 h-4 text-purple-400" />,
      action: () => setSidebarTab('tasks')
    },
    {
      id: 'tab_files',
      label: 'View: Show Files Explorer',
      icon: <FolderTree className="w-4 h-4 text-yellow-400" />,
      action: () => setSidebarTab('files')
    },
    {
      id: 'tab_processes',
      label: 'View: Show Background Servers',
      icon: <Terminal className="w-4 h-4 text-teal-400" />,
      action: () => setSidebarTab('processes')
    },
    {
      id: 'pause_agent',
      label: 'Agent: Pause Execution',
      icon: <Pause className="w-4 h-4 text-amber-400" />,
      action: () => pauseAgent()
    },
    {
      id: 'stop_agent',
      label: 'Agent: Stop / Abort Loop',
      icon: <Square className="w-4 h-4 text-rose-400" />,
      action: () => stopAgent()
    }
  ];

  const filtered = commands.filter((cmd) =>
    cmd.label.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && (e.key === 'p' || e.key === 'P')) {
        e.preventDefault();
        setCommandPaletteOpen(!isCommandPaletteOpen);
      }
      if (e.key === 'Escape' && isCommandPaletteOpen) {
        setCommandPaletteOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCommandPaletteOpen, setCommandPaletteOpen]);

  if (!isCommandPaletteOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center pt-20 p-4">
      <div className="bg-ide-panel border border-ide-border rounded-lg shadow-2xl max-w-xl w-full overflow-hidden">
        <div className="p-3 border-b border-ide-border flex items-center gap-2">
          <Command className="w-4 h-4 text-ide-accent shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Type a command or action..."
            autoFocus
            className="flex-1 bg-transparent text-sm text-white placeholder-ide-muted focus:outline-none"
          />
          <button onClick={() => setCommandPaletteOpen(false)} className="text-ide-muted hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto p-2 flex flex-col gap-1">
          {filtered.length === 0 ? (
            <div className="p-4 text-center text-xs text-ide-muted">No commands match your search</div>
          ) : (
            filtered.map((cmd) => (
              <div
                key={cmd.id}
                onClick={() => {
                  cmd.action();
                  setCommandPaletteOpen(false);
                }}
                className="flex items-center justify-between p-2 rounded hover:bg-ide-hover cursor-pointer text-xs text-white group"
              >
                <div className="flex items-center gap-2.5">
                  {cmd.icon}
                  <span>{cmd.label}</span>
                </div>
                {cmd.shortcut && (
                  <span className="text-[10px] text-ide-muted font-mono px-1.5 py-0.5 rounded bg-ide-bg border border-ide-border">
                    {cmd.shortcut}
                  </span>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
