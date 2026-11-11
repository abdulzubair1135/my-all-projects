import React, { useState } from 'react';
import { User, Phone, Mail, KeyRound, ArrowRight, ShieldCheck, CheckCircle2, AlertTriangle, Sparkles } from 'lucide-react';
import { api } from '../services/api';

interface Props {
  onLoginSuccess: (user: any, token: string) => void;
  onNavigate: (view: string) => void;
}

export const CitizenLogin: React.FC<Props> = ({ onLoginSuccess, onNavigate }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [step, setStep] = useState<'details' | 'otp'>('details');

  const [name, setName] = useState('Rahul Sharma');
  const [email, setEmail] = useState('sahay1382@gmail.com');
  const [phone, setPhone] = useState('9876543210');
  const [password, setPassword] = useState('SahayApp1');
  const [otp, setOtp] = useState('');
  const [devHint, setDevHint] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    try {
      const res = await api.sendOtp({ email, phone, purpose: isSignUp ? 'signup' : 'login' });
      if (res.success) {
        setStep('otp');
        setMessage(res.message || 'OTP sent to your email!');
        if (res.data?.devHint) {
          setDevHint(res.data.devHint);
          setOtp(res.data.devHint);
        }
      } else {
        setError(res.error?.message || 'Failed to send OTP');
      }
    } catch (err: any) {
      setError(err.message || 'Error communicating with server');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyAndSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (isSignUp) {
        const res = await api.registerWithOtp({ name, email, phone, password, otp });
        if (res.success && res.data) {
          localStorage.setItem('aapdasetu_token', res.data.token);
          localStorage.setItem('sahay_user', JSON.stringify(res.data.user));
          onLoginSuccess(res.data.user, res.data.token);
        } else {
          setError(res.error?.message || 'Registration failed');
        }
      } else {
        const res = await api.verifyOtp({ email, phone, otp });
        if (res.success && res.data) {
          localStorage.setItem('aapdasetu_token', res.data.token);
          localStorage.setItem('sahay_user', JSON.stringify(res.data.user));
          onLoginSuccess(res.data.user, res.data.token);
        } else {
          setError(res.error?.message || 'OTP verification failed');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-red-950/40 via-slate-950 to-slate-950 pointer-events-none" />

      <div className="w-full max-w-md bg-slate-900/90 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl p-8 relative z-10">
        <div className="flex flex-col items-center text-center mb-6">
          <img src="/sahay_logo.png" alt="Sahay" className="h-16 w-16 object-contain mb-3 drop-shadow-[0_0_15px_rgba(239,68,68,0.4)]" />
          <h1 className="text-2xl font-black text-white tracking-tight">Citizen Emergency Portal</h1>
          <p className="text-xs text-red-400 mt-1 font-semibold">"When the Network Fails, Sahay Doesn't."</p>
        </div>

        <div className="flex p-1 bg-slate-950 rounded-xl mb-6 border border-slate-800">
          <button
            type="button"
            onClick={() => { setIsSignUp(false); setStep('details'); setError(''); setMessage(''); }}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${!isSignUp ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white'}`}
          >
            Quick Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsSignUp(true); setStep('details'); setError(''); setMessage(''); }}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${isSignUp ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white'}`}
          >
            New Registration (with OTP)
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {message && (
          <div className="mb-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            {message}
          </div>
        )}

        {step === 'details' ? (
          <form onSubmit={handleRequestOtp} className="space-y-4">
            {isSignUp && (
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="w-full bg-slate-950 border border-slate-700 focus:border-red-500 rounded-xl px-10 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none"
                    placeholder="Rahul Sharma"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address (for OTP Verification)</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full bg-slate-950 border border-slate-700 focus:border-red-500 rounded-xl px-10 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none"
                  placeholder="sahay1382@gmail.com"
                />
              </div>
            </div>

            {isSignUp && (
              <>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Emergency Mobile Number</label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      required
                      className="w-full bg-slate-950 border border-slate-700 focus:border-red-500 rounded-xl px-10 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none"
                      placeholder="9876543210"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full bg-slate-950 border border-slate-700 focus:border-red-500 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none"
                    placeholder="Create secure password"
                  />
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-red-900/40 flex items-center justify-center gap-2 text-sm transition-all"
            >
              {loading ? 'Sending OTP to Email...' : (
                <>{isSignUp ? 'Send Registration OTP' : 'Send Login OTP'} <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyAndSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Enter 6-Digit Email OTP</label>
              <div className="relative">
                <KeyRound className="absolute left-3 top-3 w-4 h-4 text-red-500" />
                <input
                  type="text"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  required
                  autoFocus
                  className="w-full bg-slate-950 border-2 border-red-500/60 focus:border-red-500 rounded-xl px-10 py-3 text-center text-2xl tracking-[8px] font-mono font-bold text-white focus:outline-none"
                  placeholder="••••••"
                />
              </div>
              {devHint && (
                <p className="text-[11px] text-emerald-400 mt-1.5 flex items-center gap-1 font-mono">
                  <Sparkles className="w-3 h-3" /> Auto-detected OTP from server: {devHint}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-red-900/40 flex items-center justify-center gap-2 text-sm transition-all"
            >
              {loading ? 'Verifying...' : (
                <>Verify OTP & Access Sahay <CheckCircle2 className="w-4 h-4" /></>
              )}
            </button>

            <button
              type="button"
              onClick={() => setStep('details')}
              className="w-full text-xs text-slate-400 hover:text-white py-1 transition-colors text-center"
            >
              ← Back to Details
            </button>
          </form>
        )}

        <div className="mt-6 pt-6 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <button onClick={() => onNavigate('gov-login')} className="hover:text-emerald-400 transition-colors">Gov Portal</button>
          <span>•</span>
          <button onClick={() => onNavigate('ngo-login')} className="hover:text-amber-400 transition-colors">NGO Portal</button>
          <span>•</span>
          <button onClick={() => onNavigate('admin-login')} className="hover:text-red-400 transition-colors">Admin Console</button>
        </div>
      </div>
    </div>
  );
};
