import React, { useState } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { FolderGit2, Plus, Trash2, FolderOpen, MessageSquarePlus, Sparkles } from 'lucide-react';

export function ProjectSelector() {
  const { projects, activeProject, selectProject, createProject, deleteProject } = useAppStore();
  const [isOpen, setIsOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    await createProject(newProjectName.trim(), '');
    setNewProjectName('');
    setIsCreating(false);
    setIsOpen(false);
  };

  const handleQuickNewConvo = async () => {
    const defaultName = `project_${Date.now().toString().slice(-4)}`;
    await createProject(defaultName, '');
    useAppStore.setState({ terminalLogs: [], tasks: [], openTabs: [], activeTab: null });
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this project and all its files?')) {
      await deleteProject(id);
    }
  };

  return (
    <div className="relative p-2 border-b border-ide-border flex flex-col gap-1.5 bg-ide-sidebar">
      <div className="flex items-center gap-1.5">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex-1 flex items-center justify-between px-2.5 py-1.5 bg-ide-panel hover:bg-ide-hover border border-ide-border rounded text-xs font-semibold text-white transition-colors truncate"
          title="Select or Switch Project Workspace"
        >
          <div className="flex items-center gap-2 truncate">
            <FolderGit2 className="w-3.5 h-3.5 text-ide-accent shrink-0" />
            <span className="truncate">{activeProject ? activeProject.name : 'Select Project'}</span>
          </div>
          <FolderOpen className="w-3.5 h-3.5 text-ide-muted shrink-0 ml-1" />
        </button>

        {/* Quick New Convo / Project Button */}
        <button
          onClick={() => setIsCreating(true)}
          className="px-2 py-1.5 bg-ide-accent/15 hover:bg-ide-accent/25 text-ide-accent border border-ide-accent/30 rounded text-xs font-semibold flex items-center gap-1 shrink-0 transition-colors"
          title="Create New Project / Conversation"
        >
          <MessageSquarePlus className="w-3.5 h-3.5" />
          <span>New Convo</span>
        </button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreate} className="p-2 bg-ide-panel border border-ide-accent rounded flex flex-col gap-1.5 shadow-lg">
          <div className="text-[11px] font-semibold text-ide-accent flex items-center gap-1">
            <Sparkles className="w-3 h-3" />
            <span>Create New Project / Conversation</span>
          </div>
          <input
            type="text"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            placeholder="e.g. modern_crypto_app"
            autoFocus
            className="w-full px-2 py-1 bg-ide-bg border border-ide-border focus:border-ide-accent rounded text-xs text-white focus:outline-none"
          />
          <div className="flex gap-1.5">
            <button
              type="submit"
              className="flex-1 py-1 bg-ide-accent text-black font-semibold text-xs rounded hover:opacity-90 transition-opacity"
            >
              Create Project
            </button>
            <button
              type="button"
              onClick={() => setIsCreating(false)}
              className="px-2.5 py-1 bg-ide-hover text-xs text-ide-muted rounded hover:text-white"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {isOpen && (
        <div className="absolute top-full left-2 right-2 mt-1 z-30 bg-ide-panel border border-ide-border rounded shadow-xl p-2 max-h-72 overflow-y-auto">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-ide-border">
            <span className="text-xs font-semibold text-ide-muted uppercase tracking-wider">Projects & Conversations</span>
            <button
              onClick={() => {
                setIsCreating(true);
                setIsOpen(false);
              }}
              className="p-1 hover:bg-ide-hover rounded text-ide-accent flex items-center gap-1 text-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New</span>
            </button>
          </div>

          <div className="flex flex-col gap-1">
            {projects.length === 0 ? (
              <div className="p-2 text-center text-xs text-ide-muted">No projects yet. Click "+ New Convo"</div>
            ) : (
              projects.map((proj) => (
                <div
                  key={proj.id}
                  onClick={() => {
                    selectProject(proj.id);
                    setIsOpen(false);
                  }}
                  className={`group flex items-center justify-between px-2.5 py-1.5 rounded cursor-pointer text-xs transition-colors ${
                    activeProject?.id === proj.id
                      ? 'bg-ide-accent/15 text-ide-accent border border-ide-accent/30 font-medium'
                      : 'text-ide-text hover:bg-ide-hover'
                  }`}
                >
                  <span className="truncate">{proj.name}</span>
                  <button
                    onClick={(e) => handleDelete(e, proj.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 text-ide-muted transition-opacity"
                    title="Delete Project Workspace"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
