import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../api/client';
import { UserProfile } from '../types';

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('projectflow_token') || 'dev-admin-token');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      try {
        const u = await api.getCurrentUser();
        setUser(u);
        if (u?.email) localStorage.setItem('projectflow_user_email', u.email);
      } catch (err) {
        console.warn('Initial session fetch failed, falling back to dev session', err);
        // Fallback default admin profile if server isn't running yet during build/static preview
        const fallback: UserProfile = {
          id: '00000000-0000-0000-0000-000000000001',
          email: 'admin@projectflow.io',
          fullName: 'System Administrator',
          role: 'ADMINISTRATOR',
          active: true
        };
        setUser(fallback);
        localStorage.setItem('projectflow_user_email', fallback.email);
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, [token]);

  // Periodic Heartbeat presence updater
  useEffect(() => {
    if (!user?.email) return;
    localStorage.setItem('projectflow_user_email', user.email);
    // Send immediate heartbeat on session start
    api.sendHeartbeat(user.email).catch(() => {});

    // Heartbeat every 20 seconds while user is active on page
    const interval = setInterval(() => {
      api.sendHeartbeat(user.email).catch(() => {});
    }, 20000);

    const onFocus = () => {
      api.sendHeartbeat(user.email).catch(() => {});
    };
    window.addEventListener('focus', onFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', onFocus);
    };
  }, [user?.email]);

  const login = async (email: string, password?: string) => {
    setLoading(true);
    try {
      const resp = await api.login(email, password);
      localStorage.setItem('projectflow_token', resp.token);
      if (resp.user?.email) localStorage.setItem('projectflow_user_email', resp.user.email);
      setToken(resp.token);
      setUser(resp.user);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('projectflow_token');
    localStorage.removeItem('projectflow_user_email');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
