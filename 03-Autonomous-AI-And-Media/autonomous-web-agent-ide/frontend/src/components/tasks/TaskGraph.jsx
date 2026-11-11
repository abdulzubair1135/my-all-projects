import React from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { CheckCircle2, Circle, Clock, XCircle, ShieldAlert, AlertCircle, RefreshCw } from 'lucide-react';

export function TaskGraph() {
  const { tasks, dependencies } = useAppStore();

  if (tasks.length === 0) {
    return (
      <div className="p-4 text-center text-xs text-ide-muted flex flex-col items-center justify-center h-full">
        <Clock className="w-8 h-8 mb-2 opacity-30" />
        <p>No tasks generated yet.</p>
        <p className="mt-1 text-slate-500">Enter a project requirement below to start the autonomous planner.</p>
      </div>
    );
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />;
      case 'RUNNING':
        return <RefreshCw className="w-4 h-4 text-ide-accent animate-spin shrink-0" />;
      case 'FAILED':
        return <XCircle className="w-4 h-4 text-rose-400 shrink-0" />;
      case 'BLOCKED':
        return <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />;
      default:
        return <Circle className="w-4 h-4 text-ide-muted shrink-0" />;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'COMPLETED':
        return 'border-emerald-500/30 bg-emerald-500/5';
      case 'RUNNING':
        return 'border-ide-accent/50 bg-ide-accent/10 shadow-sm shadow-blue-500/10';
      case 'FAILED':
        return 'border-rose-500/30 bg-rose-500/5';
      case 'BLOCKED':
        return 'border-amber-500/30 bg-amber-500/5';
      default:
        return 'border-ide-border bg-ide-panel/40';
    }
  };

  return (
    <div className="p-3 flex flex-col gap-2 overflow-y-auto h-full">
      <div className="flex items-center justify-between pb-1 border-b border-ide-border text-xs text-ide-muted font-semibold uppercase tracking-wider">
        <span>Task Graph ({tasks.filter(t => t.status === 'COMPLETED').length}/{tasks.length})</span>
      </div>

      <div className="flex flex-col gap-2 mt-1">
        {tasks.map((task, idx) => {
          const taskDeps = dependencies.filter(d => d.task_id === task.id);

          return (
            <div
              key={task.id}
              className={`p-2.5 rounded border transition-all ${getStatusClass(task.status)}`}
            >
              <div className="flex items-start gap-2">
                <div className="pt-0.5">{getStatusIcon(task.status)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-xs font-semibold text-white truncate">
                      {idx + 1}. {task.title}
                    </span>
                    {task.retry_count > 0 && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono">
                        retry #{task.retry_count}
                      </span>
                    )}
                  </div>

                  {task.description && (
                    <p className="text-[11px] text-ide-muted mt-1 leading-relaxed line-clamp-2">
                      {task.description}
                    </p>
                  )}

                  {task.error_message && (
                    <div className="mt-2 p-1.5 rounded bg-rose-950/40 border border-rose-800/50 text-rose-300 text-[10px] font-mono whitespace-pre-wrap">
                      {task.error_message}
                    </div>
                  )}

                  {taskDeps.length > 0 && (
                    <div className="mt-1.5 flex items-center gap-1 text-[10px] text-ide-muted">
                      <span>Depends on:</span>
                      {taskDeps.map(d => (
                        <span key={d.id} className="px-1 py-0.2 rounded bg-ide-hover border border-ide-border font-mono">
                          {d.depends_on_task_id.substring(0, 4)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
