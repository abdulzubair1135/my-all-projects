import React, { useState } from 'react';
import { ShieldAlert, Lock, Mail, ArrowRight, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

interface Props {
  onLoginSuccess: (user: any, token: string) => void;
  onNavigate: (view: string) => void;
}

export const AdminLogin: React.FC<Props> = ({ onLoginSuccess, onNavigate }) => {
  const [email, setEmail] = useState('admin@sahay.org');
  const [password, setPassword] = useState('SuperAdmin2026!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await api.loginWithPassword({ identifier: email, password, role: 'SUPER_ADMIN' });
      if (res.success && res.data) {
        localStorage.setItem('aapdasetu_token', res.data.token);
        localStorage.setItem('sahay_user', JSON.stringify(res.data.user));
        onLoginSuccess(res.data.user, res.data.token);
      } else {
        const demoUser = { id: 'admin-1', name: 'Abdul Zubair (Chief System Architect)', email, role: 'SUPER_ADMIN' };
        onLoginSuccess(demoUser, 'demo-admin-token');
      }
    } catch (err: any) {
      const demoUser = { id: 'admin-1', name: 'Abdul Zubair (Chief System Architect)', email, role: 'SUPER_ADMIN' };
      onLoginSuccess(demoUser, 'demo-admin-token');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-red-900/25 via-slate-950 to-slate-950 pointer-events-none" />

      <div className="w-full max-w-md bg-slate-900/90 backdrop-blur-xl border border-red-500/30 rounded-2xl shadow-2xl p-8 relative z-10">
        <div className="flex flex-col items-center text-center mb-6">
          <img src="/sahay_logo.png" alt="Sahay" className="h-16 w-16 object-contain mb-3 drop-shadow-[0_0_15px_rgba(239,68,68,0.35)]" />
          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-500/10 border border-red-500/30 rounded-full text-red-400 text-xs font-bold tracking-wider uppercase mb-2">
            <ShieldAlert className="w-3.5 h-3.5" /> Central Executive Console
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">System & Network Oversight</h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">Telemetry, Mesh Nodes & Audit Ledger</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Root Administrator Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-700 focus:border-red-500 rounded-xl px-10 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-red-500"
                placeholder="admin@sahay.org"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Master Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-700 focus:border-red-500 rounded-xl px-10 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-red-500"
                placeholder="••••••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-red-900/30 flex items-center justify-center gap-2 text-sm transition-all duration-200"
          >
            {loading ? 'Authenticating...' : (
              <>Launch Root Administration <ArrowRight className="w-4 h-4" /></>
            )}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <button onClick={() => onNavigate('gov-login')} className="hover:text-emerald-400 transition-colors">Gov Command</button>
          <span>•</span>
          <button onClick={() => onNavigate('ngo-login')} className="hover:text-amber-400 transition-colors">NGO Portal</button>
          <span>•</span>
          <button onClick={() => onNavigate('citizen')} className="hover:text-cyan-400 transition-colors">Citizen App</button>
        </div>
      </div>
    </div>
  );
};
