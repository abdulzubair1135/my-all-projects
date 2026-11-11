import React from 'react';
import {
  ShieldCheck,
  Lock,
  ServerOff,
  CheckCircle,
  HardDrive,
  FileCheck,
} from 'lucide-react';

export const PrivacyPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div>
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#22C55E]/10 border border-[#22C55E]/20 text-[#22C55E] text-xs font-semibold mb-3">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Zero Server Uploads • Zero Credentials Required</span>
        </div>
        <h2 className="text-2xl md:text-3xl font-extrabold text-[#F8FAFC]">
          Privacy & Security Architecture
        </h2>
        <p className="text-sm text-[#94A3B8] mt-1 leading-relaxed">
          How FollowTrack completely guarantees your account safety, personal data sovereignty, and compliance.
        </p>
      </div>

      {/* 4 Pillars of FollowTrack Privacy */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-[#22C55E]/15 text-[#22C55E] flex items-center justify-center">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-[#F8FAFC]">Zero Passwords or Session Cookies</h3>
          <p className="text-xs text-[#94A3B8] leading-relaxed">
            FollowTrack will never ask for your Instagram password, two-factor code, or browser session cookies. Apps that require logging into your Instagram account risk account suspension and credential leakage.
          </p>
        </div>

        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-[#8B5CF6]/15 text-[#8B5CF6] flex items-center justify-center">
            <ServerOff className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-[#F8FAFC]">100% Client-Side In-Memory Engine</h3>
          <p className="text-xs text-[#94A3B8] leading-relaxed">
            When you upload your Instagram export ZIP or JSON file, JSZip and native JavaScript JSON parsers extract the records directly inside your browser memory. Not a single byte is sent over the internet.
          </p>
        </div>

        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-[#6366F1]/15 text-[#6366F1] flex items-center justify-center">
            <HardDrive className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-[#F8FAFC]">IndexedDB Sandboxed Storage</h3>
          <p className="text-xs text-[#94A3B8] leading-relaxed">
            Snapshots and historical records are persisted locally inside your browser's sandboxed IndexedDB database. Only you have access to your saved files. You can export a JSON backup or purge everything at any time.
          </p>
        </div>

        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-[#F59E0B]/15 text-[#F59E0B] flex items-center justify-center">
            <FileCheck className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-[#F8FAFC]">ZIP Sanitization & Security</h3>
          <p className="text-xs text-[#94A3B8] leading-relaxed">
            Our extraction pipeline validates zip entries, guards against path-traversal attacks (Zip Slip), limits memory allocations, and isolates parsed fields so no untrusted scripts or markup can execute.
          </p>
        </div>
      </div>

      {/* Comparison: FollowTrack vs Dangerous Bot Apps */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-[#252B38]">
          <h3 className="text-base font-bold text-[#F8FAFC]">
            Comparison: FollowTrack vs. Generic Instagram Follower Apps
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#252B38] bg-[#10141D] text-[#94A3B8]">
                <th className="p-4">Feature / Consideration</th>
                <th className="p-4 text-[#8B5CF6]">FollowTrack</th>
                <th className="p-4 text-[#EF4444]">Traditional Tracker Apps</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#252B38]">
              <tr>
                <td className="p-4 font-semibold text-[#F8FAFC]">Instagram Password Required?</td>
                <td className="p-4 text-[#22C55E] font-medium flex items-center space-x-1.5">
                  <CheckCircle className="w-4 h-4" />
                  <span>Never (0% credential risk)</span>
                </td>
                <td className="p-4 text-[#EF4444]">Yes (Stores your login credentials)</td>
              </tr>
              <tr>
                <td className="p-4 font-semibold text-[#F8FAFC]">Data Sent to External Servers?</td>
                <td className="p-4 text-[#22C55E] font-medium flex items-center space-x-1.5">
                  <CheckCircle className="w-4 h-4" />
                  <span>No (100% browser-based)</span>
                </td>
                <td className="p-4 text-[#EF4444]">Yes (Stored on unknown remote servers)</td>
              </tr>
              <tr>
                <td className="p-4 font-semibold text-[#F8FAFC]">Account Ban / Block Risk?</td>
                <td className="p-4 text-[#22C55E] font-medium flex items-center space-x-1.5">
                  <CheckCircle className="w-4 h-4" />
                  <span>Zero (Uses official Meta data export)</span>
                </td>
                <td className="p-4 text-[#EF4444]">Extremely High (Instagram detects bot logins)</td>
              </tr>
              <tr>
                <td className="p-4 font-semibold text-[#F8FAFC]">Works for Private Accounts?</td>
                <td className="p-4 text-[#22C55E] font-medium flex items-center space-x-1.5">
                  <CheckCircle className="w-4 h-4" />
                  <span>Yes (Full export support)</span>
                </td>
                <td className="p-4 text-[#94A3B8]">Often blocked or restricted</td>
              </tr>
              <tr>
                <td className="p-4 font-semibold text-[#F8FAFC]">Account Registration Required?</td>
                <td className="p-4 text-[#22C55E] font-medium flex items-center space-x-1.5">
                  <CheckCircle className="w-4 h-4" />
                  <span>No account needed</span>
                </td>
                <td className="p-4 text-[#EF4444]">Requires email / phone / signup</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
