import React from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { X, Circle } from 'lucide-react';

export function EditorTabs() {
  const { openTabs, activeTab, closeTab, selectProject, activeProject } = useAppStore();

  if (openTabs.length === 0) return null;

  return (
    <div className="h-9 bg-ide-sidebar border-b border-ide-border flex items-center overflow-x-auto select-none shrink-0 px-1 gap-1">
      {openTabs.map((tab) => {
        const isActive = tab.path === activeTab;

        return (
          <div
            key={tab.path}
            onClick={() => useAppStore.setState({ activeTab: tab.path })}
            className={`group flex items-center gap-2 px-3 py-1.5 rounded-t text-xs cursor-pointer border-t-2 transition-colors ${
              isActive
                ? 'bg-ide-bg border-ide-accent text-white font-medium'
                : 'bg-ide-panel/40 border-transparent text-ide-muted hover:bg-ide-hover hover:text-ide-text'
            }`}
          >
            <span className="truncate max-w-[150px]">{tab.name}</span>

            {tab.isDirty ? (
              <span className="w-2 h-2 rounded-full bg-ide-accent shrink-0" />
            ) : (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  closeTab(tab.path);
                }}
                className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-ide-hover text-ide-muted hover:text-white transition-opacity"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
