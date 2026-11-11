import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { SystemSettings } from '../types';
import {
  Settings as SettingsIcon,
  ShieldCheck,
  Database,
  RefreshCw,
  Save,
  Bell,
  Building2,
  Mail,
  AlertTriangle,
  CheckCircle2,
  Lock,
  Cpu
} from 'lucide-react';

export const Settings: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form State
  const [organizationName, setOrganizationName] = useState('ProjectFlow Enterprise');
  const [contactEmail, setContactEmail] = useState('admin@projectflow.io');
  const [syncInterval, setSyncInterval] = useState('15');
  const [maxBatchSize, setMaxBatchSize] = useState('100');
  const [offlineGracePeriod, setOfflineGracePeriod] = useState('72');
  const [riskSeverityThreshold, setRiskSeverityThreshold] = useState('MEDIUM');
  const [fcmEnabled, setFcmEnabled] = useState(true);
  const [fcmSenderId, setFcmSenderId] = useState('768921827461');
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const fetchSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const cfg = await api.getSettings();
      if (cfg) {
        setOrganizationName(cfg.organizationName || 'ProjectFlow Enterprise');
        setContactEmail(cfg.contactEmail || 'admin@projectflow.io');
        setSyncInterval(String(cfg.syncIntervalMinutes || 15));
        setMaxBatchSize(String(cfg.maxBatchSize || 100));
        setOfflineGracePeriod(String(cfg.offlineGracePeriodHours || 72));
        setRiskSeverityThreshold(cfg.riskSeverityThreshold || 'MEDIUM');
        setFcmEnabled(cfg.fcmEnabled !== false);
        setFcmSenderId(cfg.fcmSenderId || '768921827461');
        setLastUpdated(cfg.updatedAt || null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load system settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await api.updateSettings({
        organizationName,
        contactEmail,
        syncIntervalMinutes: parseInt(syncInterval) || 15,
        maxBatchSize: parseInt(maxBatchSize) || 100,
        offlineGracePeriodHours: parseInt(offlineGracePeriod) || 72,
        riskSeverityThreshold,
        fcmEnabled,
        fcmSenderId
      });
      setLastUpdated(updated.updatedAt || new Date().toISOString());
      setSuccess('Enterprise settings successfully updated and saved.');
      setTimeout(() => setSuccess(null), 4000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#292D28] tracking-tight flex items-center gap-2.5">
            <SettingsIcon className="w-6 h-6 text-[#56664C]" />
            Enterprise System Configuration
          </h2>
          <p className="text-sm text-[#78866B]">
            Tenant identity, offline engine synchronization thresholds, push gateway, and security rules.
          </p>
        </div>
        <button
          onClick={fetchSettings}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#FAFAF7] border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:text-[#292D28] hover:bg-[#EFECE4] transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#56664C]' : ''}`} />
          Reload
        </button>
      </div>

      {success && (
        <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Organization & Tenant Identity */}
        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-[#292D28]">
            <Building2 className="w-4 h-4 text-[#56664C]" />
            Organization & Contact Profile
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                Organization Title
              </label>
              <input
                type="text"
                required
                value={organizationName}
                onChange={(e) => setOrganizationName(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                Security Admin Email
              </label>
              <input
                type="email"
                required
                value={contactEmail}
                onChange={(e) => setContactEmail(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
              />
            </div>
          </div>
        </div>

        {/* Sync & Offline Engine */}
        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-[#292D28]">
            <RefreshCw className="w-4 h-4 text-[#56664C]" />
            Offline Synchronization Engine
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                Periodic Sync (Minutes)
              </label>
              <input
                type="number"
                min="1"
                max="120"
                value={syncInterval}
                onChange={(e) => setSyncInterval(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs font-mono text-[#292D28] focus:outline-none focus:border-[#56664C]"
              />
              <span className="text-[10px] text-[#78866B] mt-1 block">Android background poll cadence</span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                Batch Change Limit
              </label>
              <input
                type="number"
                min="10"
                max="500"
                value={maxBatchSize}
                onChange={(e) => setMaxBatchSize(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs font-mono text-[#292D28] focus:outline-none focus:border-[#56664C]"
              />
              <span className="text-[10px] text-[#78866B] mt-1 block">Max mutations in one payload</span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                Offline Grace (Hours)
              </label>
              <input
                type="number"
                min="1"
                max="720"
                value={offlineGracePeriod}
                onChange={(e) => setOfflineGracePeriod(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs font-mono text-[#292D28] focus:outline-none focus:border-[#56664C]"
              />
              <span className="text-[10px] text-[#78866B] mt-1 block">Cache expiry window for disconnected mode</span>
            </div>
          </div>
        </div>

        {/* Risk Radar & Push Notifications */}
        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-[#292D28]">
            <Cpu className="w-4 h-4 text-[#56664C]" />
            Risk Radar & Notification Gateway
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                Minimum Risk Severity Alert
              </label>
              <select
                value={riskSeverityThreshold}
                onChange={(e) => setRiskSeverityThreshold(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
              >
                <option value="LOW">LOW (Alert on all potential anomalies)</option>
                <option value="MEDIUM">MEDIUM (Standard production filter)</option>
                <option value="HIGH">HIGH (Escalate only severe slippages)</option>
                <option value="CRITICAL">CRITICAL (Blocking milestones only)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                FCM Push Notifications
              </label>
              <div className="flex items-center gap-3 mt-1.5">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={fcmEnabled}
                    onChange={(e) => setFcmEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-[#E2E0D8] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[#E2E0D8] after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#56664C]"></div>
                </label>
                <span className="text-xs font-medium text-[#292D28]">
                  {fcmEnabled ? 'FCM Dispatcher Active' : 'Push Dispatcher Paused'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Security & Isolation Status */}
        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-[#292D28]">
            <ShieldCheck className="w-4 h-4 text-[#56664C]" />
            Tenant Security & Access Rules
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-lg bg-white border border-[#E2E0D8]">
              <div className="font-semibold text-[#292D28]">Workspace Isolation</div>
              <div className="text-[#5A6258] mt-1">Cross-tenant queries are blocked at the repository layer.</div>
              <div className="mt-3 text-[11px] font-mono text-[#56664C] font-semibold">ACTIVE (STRICT)</div>
            </div>
            <div className="p-4 rounded-lg bg-white border border-[#E2E0D8]">
              <div className="font-semibold text-[#292D28]">Stateless JWT Authentication</div>
              <div className="text-[#5A6258] mt-1">Cryptographic token validation with Bearer token header.</div>
              <div className="mt-3 text-[11px] font-mono text-[#56664C] font-semibold">ENABLED (30 DAYS)</div>
            </div>
          </div>
        </div>

        {/* Persistence Status */}
        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-6 shadow-sm space-y-2">
          <div className="flex items-center gap-2 text-sm font-bold text-[#292D28]">
            <Database className="w-4 h-4 text-[#56664C]" />
            Database Persistence Dialect
          </div>
          <div className="text-xs text-[#5A6258] space-y-1">
            <p>
              Connected Backend: <span className="font-mono font-semibold text-[#292D28]">Supabase PostgreSQL Cloud</span> with connection pooling and SSL mode.
            </p>
            {lastUpdated && (
              <p className="text-[11px] text-[#78866B] font-mono">
                Configuration Last Persisted: {new Date(lastUpdated).toLocaleString()}
              </p>
            )}
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </form>
    </div>
  );
};
