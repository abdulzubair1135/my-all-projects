import React from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { ShieldAlert, Check, X, CheckCheck } from 'lucide-react';

export function ApprovalModal() {
  const { pendingApprovals, handleApproval } = useAppStore();

  if (pendingApprovals.length === 0) return null;

  const currentApproval = pendingApprovals[0];
  let payload = {};
  try {
    payload = typeof currentApproval.action_payload === 'string'
      ? JSON.parse(currentApproval.action_payload)
      : currentApproval.action_payload;
  } catch {}

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-ide-panel border border-amber-500/50 rounded-lg shadow-2xl max-w-lg w-full overflow-hidden animate-in fade-in zoom-in-95">
        {/* Modal Header */}
        <div className="bg-amber-500/10 border-b border-amber-500/30 px-4 py-3 flex items-center gap-2.5">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
          <div className="flex-1">
            <h3 className="text-sm font-bold text-white">Agent Approval Required</h3>
            <span className="text-[11px] text-amber-300/80">
              Policy Engine: Caution / Elevated Privileges
            </span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono">
            {pendingApprovals.length} pending
          </span>
        </div>

        {/* Modal Body */}
        <div className="p-4 flex flex-col gap-3 text-xs">
          <div>
            <span className="text-ide-muted uppercase tracking-wider text-[10px] font-semibold">Action Type</span>
            <div className="mt-0.5 font-mono text-ide-accent font-semibold">
              {currentApproval.action_type}
            </div>
          </div>

          {payload.command && (
            <div>
              <span className="text-ide-muted uppercase tracking-wider text-[10px] font-semibold">Command to Execute</span>
              <div className="mt-1 p-2 bg-ide-bg border border-ide-border rounded font-mono text-emerald-400 text-xs break-all">
                $ {payload.command}
              </div>
            </div>
          )}

          {payload.path && (
            <div>
              <span className="text-ide-muted uppercase tracking-wider text-[10px] font-semibold">Target File</span>
              <div className="mt-1 p-2 bg-ide-bg border border-ide-border rounded font-mono text-white text-xs break-all">
                {payload.path}
              </div>
            </div>
          )}

          {currentApproval.reason && (
            <div>
              <span className="text-ide-muted uppercase tracking-wider text-[10px] font-semibold">Reason</span>
              <div className="mt-0.5 text-slate-300 text-xs">
                {currentApproval.reason}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="bg-ide-sidebar border-t border-ide-border px-4 py-3 flex items-center justify-end gap-2">
          <button
            onClick={() => handleApproval(currentApproval.id, false)}
            className="px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
            <span>REJECT</span>
          </button>

          <button
            onClick={() => handleApproval(currentApproval.id, true, true)}
            className="px-3 py-1.5 bg-ide-hover hover:bg-ide-panel border border-ide-border text-slate-300 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <CheckCheck className="w-3.5 h-3.5 text-ide-accent" />
            <span>ALWAYS ALLOW</span>
          </button>

          <button
            onClick={() => handleApproval(currentApproval.id, true, false)}
            className="px-4 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <Check className="w-3.5 h-3.5" />
            <span>ALLOW</span>
          </button>
        </div>
      </div>
    </div>
  );
}
