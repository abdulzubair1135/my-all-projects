import React from 'react';
import { useApp } from '../../context/AppContext';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useApp();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col space-y-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => {
        let borderClass = 'border-[#252B38]';
        let icon = <Info className="w-5 h-5 text-[#8B5CF6] shrink-0" />;

        if (toast.type === 'success') {
          borderClass = 'border-[#22C55E]/40';
          icon = <CheckCircle2 className="w-5 h-5 text-[#22C55E] shrink-0" />;
        } else if (toast.type === 'error') {
          borderClass = 'border-[#EF4444]/40';
          icon = <AlertCircle className="w-5 h-5 text-[#EF4444] shrink-0" />;
        } else if (toast.type === 'warning') {
          borderClass = 'border-[#F59E0B]/40';
          icon = <AlertTriangle className="w-5 h-5 text-[#F59E0B] shrink-0" />;
        }

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto bg-[#151B27] text-[#F8FAFC] p-4 rounded-xl shadow-xl border ${borderClass} flex items-start space-x-3 transition-all duration-300 animate-in fade-in slide-in-from-bottom-2`}
          >
            {icon}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold">{toast.title}</p>
              {toast.message && <p className="text-xs text-[#94A3B8] mt-0.5">{toast.message}</p>}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors p-1"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
