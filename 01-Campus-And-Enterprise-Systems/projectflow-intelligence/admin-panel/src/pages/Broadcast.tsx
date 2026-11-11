import React, { useState } from 'react';
import {
  Radio,
  Send,
  BellRing,
  CheckCircle2,
  AlertCircle,
  Smartphone,
  Sparkles,
  History
} from 'lucide-react';
import { api } from '../api/client';

interface BroadcastLog {
  id: string;
  title: string;
  body: string;
  type: string;
  sentAt: string;
  recipientCount: number;
}

export const Broadcast: React.FC = () => {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [notifType, setNotifType] = useState('ANNOUNCEMENT');
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [history, setHistory] = useState<BroadcastLog[]>([
    {
      id: '1',
      title: 'ProjectFlow Android v2.0 Released',
      body: 'Offline sync and real-time deterministic risk radar now active.',
      type: 'RELEASE_NOTICE',
      sentAt: new Date(Date.now() - 7200000).toISOString(),
      recipientCount: 8
    }
  ]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !body.trim() || loading) return;

    setLoading(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      const resp = await api.sendBroadcastNotification({
        title: title.trim(),
        body: body.trim(),
        type: notifType
      });

      setSuccessMsg(`Push broadcast dispatched successfully! ${resp.message || ''}`);
      setHistory([
        {
          id: Date.now().toString(),
          title: title.trim(),
          body: body.trim(),
          type: notifType,
          sentAt: new Date().toISOString(),
          recipientCount: 8
        },
        ...history
      ]);
      setTitle('');
      setBody('');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to dispatch push broadcast notification.');
    } finally {
      setLoading(false);
    }
  };

  const applyTemplate = (t: string, b: string, type: string) => {
    setTitle(t);
    setBody(b);
    setNotifType(type);
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#292D28] tracking-tight flex items-center gap-2.5">
            <Radio className="w-6 h-6 text-[#56664C]" />
            Push Notification Dispatcher
          </h1>
          <p className="text-xs text-[#78866B] mt-1">
            Broadcast instant push alerts to team member Android smartphones via Google Firebase Cloud Messaging (FCM).
          </p>
        </div>

        <div className="flex items-center gap-2 bg-[#FAFAF7] border border-[#E2E0D8] px-3 py-1.5 rounded-xl shadow-xs">
          <Smartphone className="w-4 h-4 text-[#56664C]" />
          <span className="text-xs font-semibold text-[#292D28]">FCM Gateway Active</span>
        </div>
      </div>

      {/* Success Alert */}
      {successMsg && (
        <div className="p-4 rounded-xl bg-green-50 border border-green-200 text-green-800 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-green-600" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Error Alert */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Composer Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Form */}
        <div className="lg:col-span-2 bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl p-6 shadow-sm">
          <h2 className="text-sm font-bold text-[#292D28] mb-4 flex items-center gap-2">
            <BellRing className="w-4 h-4 text-[#56664C]" />
            Compose Broadcast Directive
          </h2>

          <form onSubmit={handleSend} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">
                Notification Headline
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Sprint Delivery Deadline Approaching"
                className="w-full px-3.5 py-2.5 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">
                Message Body
              </label>
              <textarea
                required
                rows={4}
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Provide explicit directive, deliverable review deadline, or release announcement for squad devices..."
                className="w-full px-3.5 py-2.5 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C] resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">
                  Notification Category
                </label>
                <select
                  value={notifType}
                  onChange={(e) => setNotifType(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                >
                  <option value="ANNOUNCEMENT">System Directive / Announcement</option>
                  <option value="TASK_ALERT">Critical Task Alert</option>
                  <option value="RELEASE_NOTICE">Mobile Release Update</option>
                  <option value="RISK_WARNING">Risk Radar Warning</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">
                  Target Audience
                </label>
                <div className="px-3 py-2 bg-[#F4F2E9]/60 border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] font-semibold">
                  All Active Mobile App Devices (Broadcast)
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !title.trim() || !body.trim()}
              className="w-full py-3 px-4 rounded-xl bg-[#56664C] hover:bg-[#485640] text-[#F4F2E9] text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-md hover:shadow-lg disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              <span>{loading ? 'Transmitting FCM Broadcast...' : 'Broadcast to Connected Devices'}</span>
            </button>
          </form>
        </div>

        {/* Right: Quick Templates & Mobile Preview */}
        <div className="space-y-4">
          {/* Quick Dispatch Templates */}
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl p-5 shadow-sm">
            <h3 className="text-xs font-bold text-[#292D28] uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#56664C]" />
              Quick Templates
            </h3>
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => applyTemplate(
                  'Sprint Milestone Review',
                  'Team squad sprint review is scheduled. Please update your assigned task statuses on mobile.',
                  'TASK_ALERT'
                )}
                className="w-full p-2.5 rounded-xl border border-[#E2E0D8] bg-white hover:bg-[#F4F2E9] text-left transition-colors"
              >
                <div className="text-xs font-bold text-[#292D28]">Sprint Milestone Review</div>
                <div className="text-[11px] text-[#78866B]">Prompts team to submit task deliverables</div>
              </button>

              <button
                type="button"
                onClick={() => applyTemplate(
                  'New Android APK Release Available',
                  'A new version of ProjectFlow Android is available for installation in the Releases tab.',
                  'RELEASE_NOTICE'
                )}
                className="w-full p-2.5 rounded-xl border border-[#E2E0D8] bg-white hover:bg-[#F4F2E9] text-left transition-colors"
              >
                <div className="text-xs font-bold text-[#292D28]">New APK Build Ready</div>
                <div className="text-[11px] text-[#78866B]">Notifies team of client app update</div>
              </button>

              <button
                type="button"
                onClick={() => applyTemplate(
                  'High Risk Task Detected',
                  'Deterministic Risk Radar detected an upcoming milestone delay. Immediate action required.',
                  'RISK_WARNING'
                )}
                className="w-full p-2.5 rounded-xl border border-[#E2E0D8] bg-white hover:bg-[#F4F2E9] text-left transition-colors"
              >
                <div className="text-xs font-bold text-[#292D28]">Risk Alert Directive</div>
                <div className="text-[11px] text-[#78866B]">Alerts squad of critical project risks</div>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Broadcast Transmission History */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl p-6 shadow-sm">
        <h2 className="text-sm font-bold text-[#292D28] mb-4 flex items-center gap-2">
          <History className="w-4 h-4 text-[#56664C]" />
          Recent Broadcast Dispatch Log
        </h2>

        <div className="divide-y divide-[#E2E0D8]/70">
          {history.map((log) => (
            <div key={log.id} className="py-3 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold text-[#292D28]">{log.title}</span>
                  <span className="text-[10px] font-mono font-bold bg-[#56664C]/10 text-[#56664C] px-2 py-0.5 rounded">
                    {log.type}
                  </span>
                </div>
                <p className="text-xs text-[#5A6258]">{log.body}</p>
              </div>
              <div className="text-right text-[11px] text-[#78866B] shrink-0 ml-4">
                <div>{new Date(log.sentAt).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</div>
                <div className="font-semibold text-[#47745A]">Delivered</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
