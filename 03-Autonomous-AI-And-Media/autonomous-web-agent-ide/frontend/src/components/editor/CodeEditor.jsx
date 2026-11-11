import React, { useEffect, useRef, useState } from 'react';
import Editor from '@monaco-editor/react';
import { useAppStore } from '../../stores/useAppStore';
import { Code2, Brain, Sparkles, GitCompare } from 'lucide-react';
import { LiveEvolutionStudio } from '../evolution/LiveEvolutionStudio';
import { DiffViewer } from './DiffViewer';

function getLanguage(filePath) {
  if (!filePath) return 'javascript';
  const ext = filePath.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'js':
    case 'jsx':
      return 'javascript';
    case 'ts':
    case 'tsx':
      return 'typescript';
    case 'py':
      return 'python';
    case 'json':
      return 'json';
    case 'html':
      return 'html';
    case 'css':
      return 'css';
    case 'md':
      return 'markdown';
    case 'sql':
      return 'sql';
    case 'sh':
    case 'bash':
      return 'shell';
    default:
      return 'plaintext';
  }
}

export function CodeEditor() {
  const { openTabs, activeTab, updateTabContent, saveCurrentFile } = useAppStore();
  const currentTab = openTabs.find((t) => t.path === activeTab);
  const editorRef = useRef(null);
  const [showEvolutionStudio, setShowEvolutionStudio] = useState(false);
  const [showDiff, setShowDiff] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveCurrentFile();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [saveCurrentFile]);

  const [monacoFailed, setMonacoFailed] = useState(false);

  if (!currentTab) {
    if (showEvolutionStudio) {
      return <LiveEvolutionStudio onClose={() => setShowEvolutionStudio(false)} />;
    }

    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-ide-bg text-ide-muted select-none p-6 text-center">
        <Code2 className="w-12 h-12 mb-3 opacity-20" />
        <p className="text-sm font-semibold text-white">No file is currently open</p>
        <p className="text-xs text-slate-500 mt-1 mb-5">Select a file from the explorer on the left or watch the AI train live</p>
        
        {/* Button to open Live Evolution Studio */}
        <button
          onClick={() => setShowEvolutionStudio(true)}
          className="px-4 py-2.5 bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 hover:opacity-90 text-white font-semibold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
        >
          <Brain className="w-4 h-4 text-amber-300" />
          <span>Open Live Evolution & Training Studio</span>
          <Sparkles className="w-3.5 h-3.5 text-amber-300" />
        </button>
      </div>
    );
  }

  // Diff Mode
  if (showDiff) {
    return (
      <DiffViewer
        original={currentTab.originalContent || ''}
        modified={currentTab.content || ''}
        language={getLanguage(currentTab.path)}
        fileName={currentTab.name}
        onClose={() => setShowDiff(false)}
      />
    );
  }

  // Fallback direct text editor if Monaco CDN fails
  if (monacoFailed) {
    return (
      <div className="flex-1 w-full h-full flex flex-col bg-[#1e1e1e] text-slate-100 font-mono text-xs">
        <div className="px-3 py-1 bg-[#252526] text-amber-400 text-[11px] flex items-center justify-between border-b border-slate-800">
          <span>{currentTab.name} (Direct View Mode)</span>
          <button 
            onClick={() => setMonacoFailed(false)}
            className="text-xs text-indigo-400 hover:underline"
          >
            Retry Monaco
          </button>
        </div>
        <textarea
          value={currentTab.content}
          onChange={(e) => updateTabContent(currentTab.path, e.target.value)}
          className="flex-1 w-full p-4 bg-transparent resize-none focus:outline-none font-mono text-xs leading-relaxed text-slate-200"
          spellCheck={false}
        />
      </div>
    );
  }

  return (
    <div className="flex-1 w-full h-full overflow-hidden bg-ide-bg relative">
      {/* Diff toggle button in top-right of editor */}
      <div className="absolute top-2 right-4 z-10 flex items-center gap-2">
        <button
          onClick={() => setShowDiff(!showDiff)}
          className="flex items-center gap-1 px-2 py-1 bg-ide-sidebar/90 border border-ide-border rounded text-[10px] text-cyan-300 hover:bg-ide-hover transition-colors shadow-sm"
          title="Compare original with current modified content"
        >
          <GitCompare className="w-3 h-3" />
          <span>Diff View</span>
        </button>
      </div>

      {currentTab.isLoading && (
        <div className="absolute inset-0 z-10 bg-ide-bg/80 backdrop-blur-sm flex items-center justify-center text-xs text-ide-accent">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-ide-accent border-t-transparent rounded-full animate-spin" />
            <span>Loading {currentTab.name}...</span>
          </div>
        </div>
      )}
      <Editor
        height="100%"
        language={getLanguage(currentTab.path)}
        theme="vs-dark"
        value={currentTab.content || ''}
        onChange={(val) => updateTabContent(currentTab.path, val || '')}
        onMount={(editor) => {
          editorRef.current = editor;
        }}
        loading={
          <div className="flex-1 h-full w-full flex items-center justify-center bg-ide-bg text-xs text-slate-400 gap-2">
            <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span>Initializing Editor...</span>
          </div>
        }
        options={{
          minimap: { enabled: true },
          fontSize: 13,
          fontFamily: '"Fira Code", Consolas, "Courier New", monospace',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          renderWhitespace: 'selection'
        }}
      />
    </div>
  );
}
