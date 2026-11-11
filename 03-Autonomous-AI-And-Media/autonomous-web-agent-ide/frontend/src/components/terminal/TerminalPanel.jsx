import React, { useEffect, useRef, useState } from 'react';
import { Terminal as XTerm } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';
import { useAppStore } from '../../stores/useAppStore';
import { Terminal as TermIcon, Trash2, Maximize2, Minimize2, Copy, Check, ChevronRight } from 'lucide-react';
import { api } from '../../services/api';

export function TerminalPanel() {
  const terminalRef = useRef(null);
  const xtermInstance = useRef(null);
  const fitAddonInstance = useRef(null);
  const { terminalLogs, clearTerminal, activeProject } = useAppStore();
  const [activeStream, setActiveStream] = useState('all'); // 'all', 'agent', 'server'
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const [cmdInput, setCmdInput] = useState('');
  const logsCountRef = useRef(0);

  useEffect(() => {
    if (!terminalRef.current) return;

    const term = new XTerm({
      cursorBlink: true,
      fontFamily: '"Fira Code", Consolas, monospace',
      fontSize: 12,
      theme: {
        background: '#0d1117',
        foreground: '#c9d1d9',
        cursor: '#58a6ff',
        selectionBackground: 'rgba(88, 166, 255, 0.3)',
        black: '#0d1117',
        red: '#ff7b72',
        green: '#3fb950',
        yellow: '#d29922',
        blue: '#58a6ff',
        magenta: '#bc8cff',
        cyan: '#39c5cf',
        white: '#d0d7de'
      },
      convertEol: true
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalRef.current);
    fitAddon.fit();

    term.writeln('\x1b[1;36m=== Autonomous Web-Agent IDE Terminal ===\x1b[0m');
    term.writeln('\x1b[90mWaiting for agent commands and server processes...\x1b[0m\r\n');

    xtermInstance.current = term;
    fitAddonInstance.current = fitAddon;

    const handleResize = () => fitAddon.fit();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      term.dispose();
    };
  }, []);

  // Stream incoming logs into xterm
  useEffect(() => {
    if (!xtermInstance.current) return;
    const term = xtermInstance.current;

    const newLogs = terminalLogs.slice(logsCountRef.current);
    logsCountRef.current = terminalLogs.length;

    for (const log of newLogs) {
      if (activeStream !== 'all') {
        if (activeStream === 'agent' && log.name !== 'agent') continue;
        if (activeStream === 'server' && log.name === 'agent') continue;
      }

      if (log.stream === 'stderr') {
        term.write(`\x1b[31m${log.data}\x1b[0m`);
      } else {
        term.write(log.data);
      }
    }
  }, [terminalLogs, activeStream]);

  const handleClear = () => {
    clearTerminal();
    logsCountRef.current = 0;
    if (xtermInstance.current) {
      xtermInstance.current.clear();
      xtermInstance.current.writeln('\x1b[90m[Terminal cleared]\x1b[0m\r\n');
    }
  };

  const handleCopy = async () => {
    try {
      // Clean ANSI escape sequences for clean text copying
      const rawText = terminalLogs
        .filter((log) => {
          if (activeStream === 'agent') return log.name === 'agent';
          if (activeStream === 'server') return log.name !== 'agent';
          return true;
        })
        .map((log) => log.data)
        .join('');

      // Regex to strip ANSI styling characters
      const cleanText = rawText.replace(/\x1b\[[0-9;]*[a-zA-Z]/g, '');

      await navigator.clipboard.writeText(cleanText || 'No terminal output.');
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy terminal output:', err);
    }
  };

  const handleDirectCommand = async (e) => {
    e.preventDefault();
    const cmd = cmdInput.trim();
    if (!cmd) return;
    if (!activeProject) {
      if (xtermInstance.current) {
        xtermInstance.current.writeln('\x1b[31m[Error] Please select or create a project first.\x1b[0m\r\n');
      }
      return;
    }
    setCmdInput('');
    if (xtermInstance.current) {
      xtermInstance.current.writeln(`\r\n\x1b[1;36m$ ${cmd}\x1b[0m`);
    }
    try {
      await api.runCommand(activeProject.id, cmd);
    } catch (err) {
      if (xtermInstance.current) {
        xtermInstance.current.writeln(`\x1b[31m[Command Error] ${err.message}\x1b[0m\r\n`);
      }
    }
  };

  return (
    <div className={`flex flex-col bg-ide-bg border-t border-ide-border transition-all ${
      isExpanded ? 'h-96' : 'h-56'
    }`}>
      <div className="h-8 bg-ide-sidebar border-b border-ide-border flex items-center justify-between px-3 text-xs select-none">
        <div className="flex items-center gap-2">
          <TermIcon className="w-3.5 h-3.5 text-ide-accent" />
          <span className="font-semibold text-white">Terminal Output</span>

          <div className="flex items-center ml-4 gap-1 bg-ide-panel rounded p-0.5 border border-ide-border text-[11px]">
            <button
              onClick={() => setActiveStream('all')}
              className={`px-2 py-0.5 rounded ${activeStream === 'all' ? 'bg-ide-hover text-white' : 'text-ide-muted'}`}
            >
              All
            </button>
            <button
              onClick={() => setActiveStream('agent')}
              className={`px-2 py-0.5 rounded ${activeStream === 'agent' ? 'bg-ide-hover text-white' : 'text-ide-muted'}`}
            >
              Agent
            </button>
            <button
              onClick={() => setActiveStream('server')}
              className={`px-2 py-0.5 rounded ${activeStream === 'server' ? 'bg-ide-hover text-white' : 'text-ide-muted'}`}
            >
              Servers
            </button>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Copy Terminal Button */}
          <button
            onClick={handleCopy}
            title="Copy Terminal Output"
            className="flex items-center gap-1 px-2 py-0.5 hover:bg-ide-hover text-ide-muted hover:text-white rounded border border-transparent hover:border-ide-border transition-colors text-[11px]"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-medium">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>

          <button
            onClick={handleClear}
            title="Clear Terminal"
            className="p-1 hover:bg-ide-hover text-ide-muted hover:text-white rounded transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => {
              setIsExpanded(!isExpanded);
              setTimeout(() => fitAddonInstance.current?.fit(), 100);
            }}
            title={isExpanded ? 'Collapse' : 'Expand'}
            className="p-1 hover:bg-ide-hover text-ide-muted hover:text-white rounded transition-colors"
          >
            {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      <div ref={terminalRef} className="flex-1 w-full overflow-hidden" />

      {/* Direct terminal command line */}
      <form onSubmit={handleDirectCommand} className="h-7 bg-ide-sidebar border-t border-ide-border flex items-center px-3 gap-2 shrink-0">
        <ChevronRight className="w-3.5 h-3.5 text-cyan-400" />
        <input
          type="text"
          value={cmdInput}
          onChange={(e) => setCmdInput(e.target.value)}
          placeholder="Execute shell command in project workspace... (e.g. npm test, git status, ls)"
          className="flex-1 bg-transparent text-xs text-white placeholder-ide-muted focus:outline-none font-mono"
        />
        <button
          type="submit"
          disabled={!cmdInput.trim()}
          className="text-[10px] px-2 py-0.5 bg-ide-panel hover:bg-ide-hover border border-ide-border text-slate-300 hover:text-white rounded disabled:opacity-30 transition-colors"
        >
          Run
        </button>
      </form>
    </div>
  );
}

