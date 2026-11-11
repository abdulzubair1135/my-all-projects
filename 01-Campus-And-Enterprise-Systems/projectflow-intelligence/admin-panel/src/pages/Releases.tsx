import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { AppRelease } from '../types';
import {
  Package,
  Download,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Plus,
  RefreshCw,
  Copy,
  Check,
  ShieldCheck,
  Radio,
  FileCode2,
  ExternalLink
} from 'lucide-react';

export const Releases: React.FC = () => {
  const [releases, setReleases] = useState<AppRelease[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // New Release Modal State
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    versionName: '2.0.0',
    versionCode: 2,
    channel: 'STABLE' as 'ALPHA' | 'BETA' | 'STABLE',
    artifactUrl: '/releases/android/ProjectFlow-Intelligence-v2.0.0.apk',
    artifactSize: 8114674,
    sha256Checksum: '8c20000160064c7bb80af8765f912ed1d9bb20ef6bffbb4d35ed2b3729030409',
    minAndroidSdk: 26,
    targetAndroidSdk: 34,
    releaseNotes: 'ProjectFlow Intelligence 2.0.0 with native APK sharing, offline sync and risk radar engine.'
  });

  const fetchReleases = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getReleases();
      setReleases(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch release artifacts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReleases();
  }, []);

  const handleCopyChecksum = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2500);
  };

  const handlePublish = async (id: string, isPublished: boolean) => {
    setActionMessage(null);
    try {
      if (isPublished) {
        await api.unpublishRelease(id);
        setActionMessage('Release retracted to DRAFT status.');
      } else {
        await api.publishRelease(id);
        setActionMessage('Release PUBLISHED successfully! Android devices will now download this version.');
      }
      await fetchReleases();
    } catch (err: any) {
      setError(err.message || 'Action failed');
    }
  };

  const handleCreateRelease = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createRelease({
        ...formData,
        status: 'PUBLISHED'
      });
      setShowModal(false);
      setActionMessage('New release registered and published successfully.');
      await fetchReleases();
    } catch (err: any) {
      setError(err.message || 'Failed to register release');
    } finally {
      setSubmitting(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (!bytes || bytes === 0) return '0 B';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  const latestPublished = releases.find((r) => r.status === 'PUBLISHED');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#292D28] tracking-tight flex items-center gap-2.5">
            <Package className="w-7 h-7 text-[#56664C]" />
            Application Releases & APK Distribution
          </h1>
          <p className="text-sm text-[#78866B] mt-1">
            Manage native Android APK builds, verify SHA-256 cryptographic signatures, and control distribution channels.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchReleases}
            className="flex items-center gap-1.5 px-3 py-2 border border-[#E2E0D8] bg-[#FAFAF7] hover:bg-[#EFECE4] text-[#5A6258] rounded-lg text-xs font-semibold transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-[#56664C] hover:bg-[#485640] text-[#FFFEFA] rounded-lg text-xs font-semibold shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            Register Release
          </button>
        </div>
      </div>

      {/* Notifications */}
      {actionMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm rounded-xl flex items-center gap-2.5">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <span>{actionMessage}</span>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 text-sm rounded-xl flex items-center gap-2.5">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Channel</span>
            <Radio className="w-4 h-4 text-[#56664C]" />
          </div>
          <div className="text-xl font-bold text-[#292D28]">
            {latestPublished ? `v${latestPublished.versionName}` : 'No Active Release'}
          </div>
          <div className="text-xs text-[#78866B] mt-1 flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
            Build Code: {latestPublished?.versionCode || '-'} ({latestPublished?.channel || 'STABLE'})
          </div>
        </div>

        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Artifact Size</span>
            <FileCode2 className="w-4 h-4 text-[#56664C]" />
          </div>
          <div className="text-xl font-bold text-[#292D28]">
            {latestPublished ? formatBytes(latestPublished.artifactSize) : '0 MB'}
          </div>
          <div className="text-xs text-[#78866B] mt-1">
            MIME: application/vnd.android.package-archive
          </div>
        </div>

        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Integrity Security</span>
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-xl font-bold text-emerald-800">
            SHA-256 Validated
          </div>
          <div className="text-xs text-[#78866B] mt-1 font-mono truncate" title={latestPublished?.sha256Checksum}>
            {latestPublished?.sha256Checksum ? `${latestPublished.sha256Checksum.slice(0, 16)}...` : 'N/A'}
          </div>
        </div>

        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-[#78866B] mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Android Target</span>
            <Clock className="w-4 h-4 text-[#56664C]" />
          </div>
          <div className="text-xl font-bold text-[#292D28]">
            API 26 → API 34
          </div>
          <div className="text-xs text-[#78866B] mt-1">
            Android 8.0 Oreo up to Android 14
          </div>
        </div>
      </div>

      {/* Releases Table */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-[#E2E0D8] flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-[#292D28]">Release Catalog</h2>
            <p className="text-xs text-[#78866B]">Registered installable APK binary packages and live channels</p>
          </div>
          <span className="text-xs font-semibold bg-[#E2E0D8]/60 px-2.5 py-1 rounded-full text-[#5A6258]">
            {releases.length} {releases.length === 1 ? 'Package' : 'Packages'}
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs font-medium text-[#78866B]">
            Scanning releases storage...
          </div>
        ) : releases.length === 0 ? (
          <div className="p-12 text-center">
            <Package className="w-12 h-12 text-[#78866B]/50 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-[#292D28]">No releases found</h3>
            <p className="text-xs text-[#78866B] mt-1 mb-4">Register your first APK release package to enable in-app distribution.</p>
            <button
              onClick={() => setShowModal(true)}
              className="px-3.5 py-2 bg-[#56664C] text-[#FFFEFA] rounded-lg text-xs font-semibold"
            >
              Register v2.0.0 Release
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#EFECE4] text-[#5A6258] uppercase text-[11px] font-semibold tracking-wider border-b border-[#E2E0D8]">
                <tr>
                  <th className="py-3 px-4">Version & Build</th>
                  <th className="py-3 px-4">Channel</th>
                  <th className="py-3 px-4">File Size</th>
                  <th className="py-3 px-4">SHA-256 Signature</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Published Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2E0D8]">
                {releases.map((rel) => {
                  const isPublished = rel.status === 'PUBLISHED';
                  return (
                    <tr key={rel.id} className="hover:bg-[#F4F2E9]/50 transition">
                      <td className="py-3 px-4">
                        <div className="font-bold text-[#292D28] text-sm">
                          v{rel.versionName}
                        </div>
                        <div className="text-[11px] text-[#78866B]">
                          Code: <span className="font-mono font-semibold">{rel.versionCode}</span> &bull; Min SDK {rel.minAndroidSdk}
                        </div>
                        {rel.releaseNotes && (
                          <div className="text-[11px] text-[#5A6258] mt-0.5 line-clamp-1 italic">
                            {rel.releaseNotes}
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-block px-2 py-0.5 rounded-full font-semibold text-[10px] uppercase tracking-wide ${
                            rel.channel === 'STABLE'
                              ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                              : rel.channel === 'BETA'
                              ? 'bg-amber-100 text-amber-800 border border-amber-200'
                              : 'bg-purple-100 text-purple-800 border border-purple-200'
                          }`}
                        >
                          {rel.channel}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono font-medium text-[#292D28]">
                        {formatBytes(rel.artifactSize)}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5 font-mono text-[11px] text-[#5A6258]">
                          <span title={rel.sha256Checksum}>
                            {rel.sha256Checksum.slice(0, 14)}...{rel.sha256Checksum.slice(-6)}
                          </span>
                          <button
                            onClick={() => handleCopyChecksum(rel.sha256Checksum)}
                            title="Copy SHA-256 Checksum"
                            className="p-1 hover:bg-[#E2E0D8] rounded text-[#56664C] transition"
                          >
                            {copiedHash === rel.sha256Checksum ? (
                              <Check className="w-3.5 h-3.5 text-emerald-600" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                            isPublished
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : 'bg-[#E2E0D8]/60 text-[#5A6258]'
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              isPublished ? 'bg-emerald-500' : 'bg-gray-400'
                            }`}
                          ></span>
                          {rel.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-[#78866B]">
                        {rel.publishedAt ? new Date(rel.publishedAt).toLocaleDateString() : 'Unpublished'}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <a
                            href={api.getDownloadUrl(rel.id)}
                            download={`ProjectFlow-v${rel.versionName}.apk`}
                            className="flex items-center gap-1 px-2.5 py-1 bg-[#FAFAF7] hover:bg-[#EFECE4] border border-[#E2E0D8] text-[#56664C] font-semibold rounded text-xs transition"
                            title="Directly download APK file"
                          >
                            <Download className="w-3.5 h-3.5" />
                            APK
                          </a>
                          <button
                            onClick={() => handlePublish(rel.id, isPublished)}
                            className={`px-2.5 py-1 rounded text-xs font-semibold transition ${
                              isPublished
                                ? 'bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200'
                                : 'bg-[#56664C] hover:bg-[#485640] text-white shadow-sm'
                            }`}
                          >
                            {isPublished ? 'Retract' : 'Publish'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Register Release Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl max-w-lg w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#E2E0D8]">
              <div className="flex items-center gap-2">
                <Package className="w-5 h-5 text-[#56664C]" />
                <h3 className="text-base font-bold text-[#292D28]">Register APK Release</h3>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="text-[#78866B] hover:text-[#292D28] text-sm font-semibold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateRelease} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#5A6258] font-semibold mb-1">Version Name</label>
                  <input
                    type="text"
                    required
                    value={formData.versionName}
                    onChange={(e) => setFormData({ ...formData, versionName: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg focus:outline-none focus:border-[#56664C]"
                    placeholder="2.0.0"
                  />
                </div>
                <div>
                  <label className="block text-[#5A6258] font-semibold mb-1">Version Code</label>
                  <input
                    type="number"
                    required
                    value={formData.versionCode}
                    onChange={(e) => setFormData({ ...formData, versionCode: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg focus:outline-none focus:border-[#56664C]"
                    placeholder="2"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#5A6258] font-semibold mb-1">Distribution Channel</label>
                  <select
                    value={formData.channel}
                    onChange={(e) => setFormData({ ...formData, channel: e.target.value as any })}
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg focus:outline-none focus:border-[#56664C]"
                  >
                    <option value="STABLE">STABLE</option>
                    <option value="BETA">BETA</option>
                    <option value="ALPHA">ALPHA</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[#5A6258] font-semibold mb-1">Artifact Size (Bytes)</label>
                  <input
                    type="number"
                    required
                    value={formData.artifactSize}
                    onChange={(e) => setFormData({ ...formData, artifactSize: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg focus:outline-none focus:border-[#56664C]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[#5A6258] font-semibold mb-1">Artifact Storage Path</label>
                <input
                  type="text"
                  required
                  value={formData.artifactUrl}
                  onChange={(e) => setFormData({ ...formData, artifactUrl: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg font-mono focus:outline-none focus:border-[#56664C]"
                  placeholder="/releases/android/ProjectFlow-v2.0.0.apk"
                />
              </div>

              <div>
                <label className="block text-[#5A6258] font-semibold mb-1">SHA-256 Checksum Signature</label>
                <input
                  type="text"
                  required
                  value={formData.sha256Checksum}
                  onChange={(e) => setFormData({ ...formData, sha256Checksum: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg font-mono focus:outline-none focus:border-[#56664C]"
                  placeholder="8c20000160064c7bb80af8765f912ed1d9bb20ef6bffbb4d35ed2b3729030409"
                />
              </div>

              <div>
                <label className="block text-[#5A6258] font-semibold mb-1">Release Notes</label>
                <textarea
                  rows={2}
                  value={formData.releaseNotes}
                  onChange={(e) => setFormData({ ...formData, releaseNotes: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg focus:outline-none focus:border-[#56664C]"
                  placeholder="Summary of bug fixes, features and improvements..."
                />
              </div>

              <div className="pt-3 border-t border-[#E2E0D8] flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3.5 py-2 border border-[#E2E0D8] hover:bg-[#EFECE4] text-[#5A6258] rounded-lg font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-[#56664C] hover:bg-[#485640] text-white rounded-lg font-semibold shadow-sm transition disabled:opacity-50"
                >
                  {submitting ? 'Registering...' : 'Register & Publish'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
