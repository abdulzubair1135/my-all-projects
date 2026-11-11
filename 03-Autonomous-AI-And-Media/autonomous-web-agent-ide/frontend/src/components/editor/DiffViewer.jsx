import React from 'react';
import { DiffEditor } from '@monaco-editor/react';
import { GitCompare, X } from 'lucide-react';

export function DiffViewer({
  original = '',
  modified = '',
  language = 'javascript',
  fileName = 'file',
  onClose,
}) {
  return (
    <div className="flex flex-col h-full w-full bg-ide-bg">
      {/* Diff header */}
      <div className="h-8 bg-ide-sidebar border-b border-ide-border flex items-center justify-between px-3 text-xs text-ide-muted shrink-0">
        <div className="flex items-center gap-2">
          <GitCompare className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-mono text-white font-medium">{fileName}</span>
          <span className="text-[10px] bg-cyan-900/40 text-cyan-300 border border-cyan-500/30 px-1.5 py-0.5 rounded">
            Diff Mode (Original ↔ Modified)
          </span>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-ide-hover text-ide-muted hover:text-white transition-colors"
            title="Close Diff"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Monaco Diff Editor */}
      <div className="flex-1 w-full overflow-hidden">
        <DiffEditor
          original={original}
          modified={modified}
          language={language}
          theme="vs-dark"
          options={{
            readOnly: true,
            renderSideBySide: true,
            fontSize: 12,
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            lineNumbers: 'on',
          }}
        />
      </div>
    </div>
  );
}
