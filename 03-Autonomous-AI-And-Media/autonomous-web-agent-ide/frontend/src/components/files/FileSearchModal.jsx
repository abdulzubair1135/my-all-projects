import React, { useState, useEffect } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { Search, FileCode, X } from 'lucide-react';
import { api } from '../../services/api';

export function FileSearchModal() {
  const { isFileSearchOpen, setFileSearchOpen, activeProject, openFile } = useAppStore();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (!isFileSearchOpen) {
      setQuery('');
      setResults([]);
      return;
    }
  }, [isFileSearchOpen]);

  useEffect(() => {
    if (!query.trim() || !activeProject) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const matches = await api.searchFiles(activeProject.id, query.trim());
        setResults(matches);
      } catch (err) {
        console.error('Search error:', err);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query, activeProject]);

  if (!isFileSearchOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center pt-20 p-4">
      <div className="bg-ide-panel border border-ide-border rounded-lg shadow-2xl max-w-xl w-full overflow-hidden">
        <div className="p-3 border-b border-ide-border flex items-center gap-2">
          <Search className="w-4 h-4 text-ide-accent shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search files by name or content..."
            autoFocus
            className="flex-1 bg-transparent text-sm text-white placeholder-ide-muted focus:outline-none"
          />
          <button onClick={() => setFileSearchOpen(false)} className="text-ide-muted hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto p-2 flex flex-col gap-1">
          {results.length === 0 ? (
            <div className="p-4 text-center text-xs text-ide-muted">
              {query.trim() ? 'No matching files found' : 'Type to search...'}
            </div>
          ) : (
            results.map((res, i) => (
              <div
                key={i}
                onClick={() => {
                  openFile(res.path);
                  setFileSearchOpen(false);
                }}
                className="flex items-center justify-between p-2 rounded hover:bg-ide-hover cursor-pointer text-xs text-white"
              >
                <div className="flex items-center gap-2 truncate">
                  <FileCode className="w-4 h-4 text-ide-accent shrink-0" />
                  <span className="truncate">{res.path}</span>
                </div>
                <span className="text-[10px] text-ide-muted uppercase px-1 rounded bg-ide-bg">
                  {res.type}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
