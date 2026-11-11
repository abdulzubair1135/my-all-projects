import React, { useState, useEffect, useRef } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { 
  Folder, 
  FolderOpen, 
  File, 
  FileCode, 
  FileText, 
  FileJson, 
  ChevronRight, 
  ChevronDown, 
  Trash2,
  Search,
  FilePlus2,
  FolderPlus,
  Copy,
  AlertTriangle,
  X
} from 'lucide-react';
import { api } from '../../services/api';

function getFileIcon(fileName) {
  const ext = fileName.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'js':
    case 'jsx':
    case 'ts':
    case 'tsx':
      return <FileCode className="w-3.5 h-3.5 text-amber-400 shrink-0" />;
    case 'py':
      return <FileCode className="w-3.5 h-3.5 text-blue-400 shrink-0" />;
    case 'json':
      return <FileJson className="w-3.5 h-3.5 text-yellow-500 shrink-0" />;
    case 'md':
    case 'txt':
      return <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0" />;
    case 'css':
    case 'html':
      return <FileCode className="w-3.5 h-3.5 text-cyan-400 shrink-0" />;
    default:
      return <File className="w-3.5 h-3.5 text-ide-muted shrink-0" />;
  }
}

function TreeNode({ item, level = 0, onSelect, onDelete, onContextMenu }) {
  const [isOpen, setIsOpen] = useState(true);
  const { activeTab } = useAppStore();
  const isSelected = activeTab && item.path && activeTab.replace(/\\/g, '/') === item.path.replace(/\\/g, '/');

  if (item.type === 'directory') {
    return (
      <div>
        <div
          onClick={() => setIsOpen(!isOpen)}
          onContextMenu={(e) => onContextMenu(e, item)}
          style={{ paddingLeft: `${level * 12 + 6}px` }}
          className="flex items-center justify-between py-1 px-2 rounded cursor-pointer hover:bg-ide-hover text-xs text-slate-300 font-medium select-none group transition-colors"
        >
          <div className="flex items-center gap-1.5 truncate flex-1">
            {isOpen ? <ChevronDown className="w-3.5 h-3.5 text-ide-muted shrink-0" /> : <ChevronRight className="w-3.5 h-3.5 text-ide-muted shrink-0" />}
            {isOpen ? <FolderOpen className="w-4 h-4 text-ide-accent shrink-0" /> : <Folder className="w-4 h-4 text-ide-accent shrink-0" />}
            <span className="truncate">{item.name}</span>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(item.path, true, item.name);
            }}
            className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-400 hover:bg-rose-500/20 rounded transition-all shrink-0"
            title={`Delete folder "${item.name}"`}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
        {isOpen && item.children && (
          <div>
            {item.children.map((child) => (
              <TreeNode
                key={child.path}
                item={child}
                level={level + 1}
                onSelect={onSelect}
                onDelete={onDelete}
                onContextMenu={onContextMenu}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      onClick={() => onSelect(item.path)}
      onContextMenu={(e) => onContextMenu(e, item)}
      style={{ paddingLeft: `${level * 12 + 18}px` }}
      className={`group flex items-center justify-between py-1 px-2 rounded cursor-pointer text-xs select-none transition-colors ${
        isSelected
          ? 'bg-ide-accent/20 text-white font-medium'
          : 'text-ide-text hover:bg-ide-hover'
      }`}
    >
      <div className="flex items-center gap-1.5 truncate flex-1">
        {getFileIcon(item.name)}
        <span className="truncate">{item.name}</span>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(item.path, false, item.name);
        }}
        className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-400 hover:bg-rose-500/20 rounded transition-all shrink-0"
        title={`Delete file "${item.name}"`}
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

export function FileTree() {
  const { fileTree, activeProject, openFile, refreshFileTree, setFileSearchOpen, closeTab } = useAppStore();
  const [isCreatingFile, setIsCreatingFile] = useState(false);
  const [isCreatingFolder, setIsCreatingFolder] = useState(false);
  const [newItemName, setNewItemName] = useState('');
  
  // Custom in-app delete modal
  const [deleteConfirm, setDeleteConfirm] = useState(null); // { path, isDir, name }
  const [isDeleting, setIsDeleting] = useState(false);

  // Right-click context menu
  const [contextMenu, setContextMenu] = useState(null); // { x, y, item }
  const contextMenuRef = useRef(null);

  // Close context menu on outside click
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (contextMenuRef.current && !contextMenuRef.current.contains(e.target)) {
        setContextMenu(null);
      }
    };
    if (contextMenu) {
      document.addEventListener('mousedown', handleOutsideClick);
      return () => document.removeEventListener('mousedown', handleOutsideClick);
    }
  }, [contextMenu]);

  const handleContextMenu = (e, item) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({
      x: Math.min(e.clientX, window.innerWidth - 180),
      y: Math.min(e.clientY, window.innerHeight - 150),
      item
    });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newItemName.trim() || !activeProject) return;

    try {
      if (isCreatingFolder) {
        await api.createDirectory(activeProject.id, newItemName.trim());
      } else {
        await api.saveFile(activeProject.id, newItemName.trim(), '');
        await openFile(newItemName.trim());
      }
      setNewItemName('');
      setIsCreatingFile(false);
      setIsCreatingFolder(false);
      await refreshFileTree();
    } catch (err) {
      alert(`Error creating item: ${err.message}`);
    }
  };

  const requestDelete = (filePath, isDir = false, name = '') => {
    setDeleteConfirm({
      path: filePath,
      isDir,
      name: name || filePath.split('/').pop()
    });
    setContextMenu(null);
  };

  const confirmDelete = async () => {
    if (!activeProject || !deleteConfirm) return;
    setIsDeleting(true);
    try {
      await api.deleteFile(activeProject.id, deleteConfirm.path);
      // Close open tab if this file was currently open in editor
      if (!deleteConfirm.isDir) {
        closeTab(deleteConfirm.path);
      }
      await refreshFileTree();
      setDeleteConfirm(null);
    } catch (err) {
      alert(`Failed to delete: ${err.message}`);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-ide-sidebar relative">
      {/* File Tree Header */}
      <div className="flex items-center justify-between p-2 border-b border-ide-border text-xs">
        <span className="font-semibold text-ide-muted uppercase tracking-wider text-[11px]">Workspace Explorer</span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setFileSearchOpen(true)}
            title="Search Files (Ctrl+P)"
            className="p-1 hover:bg-ide-hover rounded text-ide-muted hover:text-white transition-colors"
          >
            <Search className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => {
              setIsCreatingFile(true);
              setIsCreatingFolder(false);
            }}
            title="New File"
            className="px-1.5 py-0.5 bg-ide-panel hover:bg-ide-hover border border-ide-border rounded text-[11px] text-white flex items-center gap-1 transition-colors"
          >
            <FilePlus2 className="w-3 h-3 text-ide-accent" />
            <span>+ File</span>
          </button>
          <button
            onClick={() => {
              setIsCreatingFolder(true);
              setIsCreatingFile(false);
            }}
            title="New Folder"
            className="px-1.5 py-0.5 bg-ide-panel hover:bg-ide-hover border border-ide-border rounded text-[11px] text-white flex items-center gap-1 transition-colors"
          >
            <FolderPlus className="w-3 h-3 text-amber-400" />
            <span>+ Folder</span>
          </button>
        </div>
      </div>

      {/* Creation form */}
      {(isCreatingFile || isCreatingFolder) && (
        <form onSubmit={handleCreate} className="p-2 bg-ide-panel border-b border-ide-accent flex flex-col gap-1.5">
          <div className="text-[11px] font-semibold text-white flex items-center gap-1">
            {isCreatingFolder ? (
              <>
                <FolderPlus className="w-3.5 h-3.5 text-amber-400" />
                <span>Create New Folder</span>
              </>
            ) : (
              <>
                <FilePlus2 className="w-3.5 h-3.5 text-ide-accent" />
                <span>Create New File</span>
              </>
            )}
          </div>
          <input
            type="text"
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            placeholder={isCreatingFolder ? 'e.g. src/components or assets' : 'e.g. src/components/Button.jsx'}
            autoFocus
            className="w-full px-2 py-1 bg-ide-bg border border-ide-accent rounded text-xs text-white focus:outline-none"
          />
          <div className="flex gap-1.5">
            <button type="submit" className="flex-1 py-0.5 bg-ide-accent text-black font-semibold text-xs rounded hover:opacity-90">
              {isCreatingFolder ? 'Create Folder' : 'Create File'}
            </button>
            <button
              type="button"
              onClick={() => {
                setIsCreatingFile(false);
                setIsCreatingFolder(false);
              }}
              className="px-2.5 py-0.5 bg-ide-hover text-xs text-ide-muted rounded hover:text-white"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* File Tree List */}
      <div className="flex-1 overflow-y-auto p-1">
        {fileTree.length === 0 ? (
          <div className="p-4 text-center text-xs text-ide-muted">No files in current workspace.</div>
        ) : (
          fileTree.map((item) => (
            <TreeNode
              key={item.path}
              item={item}
              onSelect={openFile}
              onDelete={requestDelete}
              onContextMenu={handleContextMenu}
            />
          ))
        )}
      </div>

      {/* Right-Click Context Menu */}
      {contextMenu && (
        <div
          ref={contextMenuRef}
          style={{ top: `${contextMenu.y}px`, left: `${contextMenu.x}px` }}
          className="fixed z-50 bg-[#181824] border border-slate-700/80 rounded-lg shadow-2xl py-1 min-w-[170px] text-xs text-slate-200 animate-in fade-in"
        >
          <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 border-b border-slate-700/50 truncate max-w-[160px]">
            {contextMenu.item.name}
          </div>

          <button
            onClick={() => {
              navigator.clipboard.writeText(contextMenu.item.path);
              setContextMenu(null);
            }}
            className="w-full px-3 py-1.5 text-left flex items-center gap-2 hover:bg-slate-700/50 hover:text-white transition-colors"
          >
            <Copy className="w-3.5 h-3.5 text-slate-400" />
            <span>Copy Path</span>
          </button>

          {contextMenu.item.type === 'directory' && (
            <>
              <button
                onClick={() => {
                  setNewItemName(`${contextMenu.item.path}/`);
                  setIsCreatingFile(true);
                  setContextMenu(null);
                }}
                className="w-full px-3 py-1.5 text-left flex items-center gap-2 hover:bg-slate-700/50 hover:text-white transition-colors"
              >
                <FilePlus2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>New File Here</span>
              </button>
              <button
                onClick={() => {
                  setNewItemName(`${contextMenu.item.path}/`);
                  setIsCreatingFolder(true);
                  setContextMenu(null);
                }}
                className="w-full px-3 py-1.5 text-left flex items-center gap-2 hover:bg-slate-700/50 hover:text-white transition-colors"
              >
                <FolderPlus className="w-3.5 h-3.5 text-amber-400" />
                <span>New Folder Here</span>
              </button>
            </>
          )}

          <div className="my-1 border-t border-slate-700/50" />

          <button
            onClick={() => {
              requestDelete(
                contextMenu.item.path,
                contextMenu.item.type === 'directory',
                contextMenu.item.name
              );
            }}
            className="w-full px-3 py-1.5 text-left flex items-center gap-2 text-rose-400 hover:bg-rose-500/20 hover:text-rose-300 font-medium transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Delete {contextMenu.item.type === 'directory' ? 'Folder' : 'File'}</span>
          </button>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#181824] border border-rose-500/30 rounded-xl shadow-2xl max-w-sm w-full p-5 animate-in zoom-in-95">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2 text-rose-400 font-semibold text-sm">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>Delete {deleteConfirm.isDir ? 'Folder' : 'File'}?</span>
              </div>
              <button
                onClick={() => setDeleteConfirm(null)}
                className="text-slate-400 hover:text-white p-0.5 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-300 mb-2 leading-relaxed">
              Are you sure you want to delete <span className="font-semibold text-white">"{deleteConfirm.name}"</span>?
            </p>
            {deleteConfirm.isDir && (
              <p className="text-[11px] text-amber-400/90 mb-4 bg-amber-500/10 p-2 rounded border border-amber-500/20">
                ⚠️ All files and subdirectories inside this folder will be permanently deleted.
              </p>
            )}

            <div className="flex items-center justify-end gap-2 mt-4">
              <button
                onClick={() => setDeleteConfirm(null)}
                disabled={isDeleting}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                disabled={isDeleting}
                className="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 shadow-lg shadow-rose-600/30 transition-all"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{isDeleting ? 'Deleting...' : 'Delete'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
