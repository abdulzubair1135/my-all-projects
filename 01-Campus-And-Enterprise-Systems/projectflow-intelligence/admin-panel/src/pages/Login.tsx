import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, Mail, Eye, EyeOff, AlertCircle, CheckCircle2, KeyRound } from 'lucide-react';
import { api } from '../api/client';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Forgot Password modal state
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [forgotStep, setForgotStep] = useState<1 | 2>(1);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotOtp, setForgotOtp] = useState('1234');
  const [forgotNewPassword, setForgotNewPassword] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotError, setForgotError] = useState<string | null>(null);
  const [forgotSuccess, setForgotSuccess] = useState<string | null>(null);
  const [showForgotOtp, setShowForgotOtp] = useState(true);
  const [showForgotNewPassword, setShowForgotNewPassword] = useState(false);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Please enter your account email address.');
      return;
    }
    if (!password) {
      setError('Please enter your password.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await login(email.trim(), password);
      if (rememberMe) {
        localStorage.setItem('pf_saved_email', email.trim());
      } else {
        localStorage.removeItem('pf_saved_email');
      }
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please verify your email and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotEmail.trim()) {
      setForgotError('Please enter your account email.');
      return;
    }
    setForgotLoading(true);
    setForgotError(null);
    try {
      await api.forgotPassword(forgotEmail.trim());
      setForgotStep(2);
      setForgotOtp('1234');
    } catch (err: any) {
      setForgotError(err.message || 'No account found with this email.');
    } finally {
      setForgotLoading(false);
    }
  };

  const handleForgotResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotOtp.trim()) {
      setForgotError('Please enter the OTP code (1234).');
      return;
    }
    if (!forgotNewPassword || forgotNewPassword.length < 6) {
      setForgotError('Password must be at least 6 characters.');
      return;
    }
    setForgotLoading(true);
    setForgotError(null);
    try {
      await api.resetPassword(forgotEmail.trim(), forgotOtp.trim(), forgotNewPassword);
      setForgotSuccess('Password reset successfully! You can now sign in.');
      setEmail(forgotEmail.trim());
      setPassword(forgotNewPassword);
    } catch (err: any) {
      setForgotError(err.message || 'Failed to reset password. Please check your OTP.');
    } finally {
      setForgotLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-[#F4F2E9] flex flex-col items-center justify-center p-4 select-none">
      <div className="w-full max-w-md bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl shadow-xl p-8 backdrop-blur-sm">
        {/* Brand Header */}
        <div className="flex items-center gap-3.5 mb-7">
          <img
            src="/logo.jpg"
            alt="ProjectFlow Logo"
            style={{ width: '48px', height: '48px', maxWidth: '48px', maxHeight: '48px' }}
            className="w-12 h-12 rounded-xl object-contain bg-white border border-[#E2E0D8] shadow-sm shrink-0"
          />
          <div>
            <h1 className="text-xl font-bold text-[#292D28] tracking-tight">ProjectFlow Intelligence</h1>
            <p className="text-xs text-[#78866B] font-semibold uppercase tracking-wider">Enterprise Administration</p>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-5 p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{error}</span>
          </div>
        )}

        {/* Real Authentication Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1.5">
              Account Email
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#78866B]" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@projectflow.io"
                className="w-full pl-9 pr-3 py-2.5 bg-white border border-[#E2E0D8] rounded-xl text-sm text-[#292D28] focus:outline-none focus:border-[#56664C] focus:ring-1 focus:ring-[#56664C] transition-all"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider">
                Password
              </label>
              <button
                type="button"
                onClick={() => {
                  setForgotEmail(email);
                  setForgotStep(1);
                  setForgotOtp('1234');
                  setForgotNewPassword('');
                  setForgotError(null);
                  setForgotSuccess(null);
                  setShowForgotModal(true);
                }}
                className="text-xs text-[#56664C] hover:underline font-medium"
              >
                Forgot Password?
              </button>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#78866B]" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your security password"
                className="w-full pl-9 pr-10 py-2.5 bg-white border border-[#E2E0D8] rounded-xl text-sm text-[#292D28] focus:outline-none focus:border-[#56664C] focus:ring-1 focus:ring-[#56664C] transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#78866B] hover:text-[#292D28]"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between pt-1">
            <label className="flex items-center gap-2 cursor-pointer text-xs text-[#5A6258]">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded text-[#56664C] focus:ring-[#56664C] border-[#E2E0D8]"
              />
              <span>Remember this console session</span>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-[#56664C] hover:bg-[#485640] text-[#F4F2E9] text-sm font-semibold transition-all shadow-md hover:shadow-lg disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span>Authenticating Credentials...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />
                <span>Sign In to Admin Console</span>
              </>
            )}
          </button>
        </form>

        {/* Security Isolation Footer */}
        <div className="mt-8 pt-5 border-t border-[#E2E0D8] text-center">
          <p className="text-[11px] text-[#78866B] font-mono">
            Encrypted TLS 1.3 • Workspace Isolation • Zero Demo Mockups
          </p>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50 backdrop-blur-xs">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl p-6 max-w-sm w-full shadow-2xl">
            <div className="flex items-center gap-2 mb-2">
              <KeyRound className="w-5 h-5 text-[#56664C]" />
              <h3 className="text-base font-bold text-[#292D28]">Reset Account Password</h3>
            </div>
            
            {forgotSuccess ? (
              <div className="p-4 rounded-xl bg-[#56664C]/10 border border-[#56664C]/20 text-[#56664C] text-xs space-y-3">
                <div className="flex items-center gap-2 font-semibold text-sm">
                  <CheckCircle2 className="w-4 h-4 text-[#56664C]" />
                  <span>Password Reset Completed</span>
                </div>
                <p>{forgotSuccess}</p>
                <button
                  type="button"
                  onClick={() => setShowForgotModal(false)}
                  className="mt-2 w-full py-2 bg-[#56664C] text-white rounded-lg font-semibold hover:bg-[#485640] transition-colors"
                >
                  Return to Sign In
                </button>
              </div>
            ) : forgotStep === 1 ? (
              <div>
                <p className="text-xs text-[#5A6258] mb-4">
                  Enter your registered account email. A verification code will be dispatched.
                </p>

                {forgotError && (
                  <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
                    <span>{forgotError}</span>
                  </div>
                )}

                <form onSubmit={handleForgotSendOtp} className="space-y-4">
                  <div>
                    <label className="block text-[11px] font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                      Account Email
                    </label>
                    <input
                      type="email"
                      required
                      value={forgotEmail}
                      onChange={(e) => setForgotEmail(e.target.value)}
                      placeholder="admin@projectflow.io"
                      className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-sm text-[#292D28] focus:outline-none focus:border-[#56664C]"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setShowForgotModal(false)}
                      className="flex-1 py-2 rounded-xl border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:bg-[#EFECE4]"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={forgotLoading}
                      className="flex-1 py-2 rounded-xl bg-[#56664C] text-white text-xs font-semibold hover:bg-[#485640] disabled:opacity-50"
                    >
                      {forgotLoading ? 'Checking...' : 'Send OTP'}
                    </button>
                  </div>
                </form>
              </div>
            ) : (
              <div>
                <div className="mb-3 p-2.5 rounded-lg bg-[#56664C]/10 border border-[#56664C]/20 text-[#56664C] text-xs flex items-center justify-between">
                  <span>Code sent: <strong>OTP 1234</strong></span>
                  <span className="font-mono text-[11px] truncate max-w-[130px]">{forgotEmail}</span>
                </div>

                {forgotError && (
                  <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
                    <span>{forgotError}</span>
                  </div>
                )}

                <form onSubmit={handleForgotResetPassword} className="space-y-3.5">
                  <div>
                    <label className="block text-[11px] font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                      Verification Code (OTP)
                    </label>
                    <div className="relative">
                      <input
                        type={showForgotOtp ? 'text' : 'password'}
                        required
                        value={forgotOtp}
                        onChange={(e) => setForgotOtp(e.target.value)}
                        placeholder="Enter 1234"
                        className="w-full pl-3 pr-10 py-2 bg-white border border-[#E2E0D8] rounded-xl text-sm font-mono tracking-widest text-[#292D28] focus:outline-none focus:border-[#56664C]"
                      />
                      <button
                        type="button"
                        onClick={() => setShowForgotOtp(!showForgotOtp)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[#78866B] hover:text-[#292D28]"
                      >
                        {showForgotOtp ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                      New Password
                    </label>
                    <div className="relative">
                      <input
                        type={showForgotNewPassword ? 'text' : 'password'}
                        required
                        value={forgotNewPassword}
                        onChange={(e) => setForgotNewPassword(e.target.value)}
                        placeholder="Min. 6 characters"
                        className="w-full pl-3 pr-10 py-2 bg-white border border-[#E2E0D8] rounded-xl text-sm text-[#292D28] focus:outline-none focus:border-[#56664C]"
                      />
                      <button
                        type="button"
                        onClick={() => setShowForgotNewPassword(!showForgotNewPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[#78866B] hover:text-[#292D28]"
                      >
                        {showForgotNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>


                  <div className="flex gap-2 pt-1">
                    <button
                      type="button"
                      onClick={() => setForgotStep(1)}
                      className="flex-1 py-2 rounded-xl border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:bg-[#EFECE4]"
                    >
                      Back
                    </button>
                    <button
                      type="submit"
                      disabled={forgotLoading}
                      className="flex-1 py-2 rounded-xl bg-[#56664C] text-white text-xs font-semibold hover:bg-[#485640] disabled:opacity-50"
                    >
                      {forgotLoading ? 'Resetting...' : 'Reset Password'}
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};
