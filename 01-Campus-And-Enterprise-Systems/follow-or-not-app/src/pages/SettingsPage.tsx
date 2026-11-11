import React, { useState, useRef } from 'react';
import { useApp } from '../context/AppContext';
import { storageService } from '../services/StorageService';
import { ConfirmModal } from '../components/common/ConfirmModal';
import {
  Trash2,
  Download,
  Upload,
  HardDrive,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { settings, updateSettings, addToast, refreshData, setCurrentPage } = useApp();
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleExportBackup = async () => {
    try {
      const backupJson = await storageService.exportAllData();
      const blob = new Blob([backupJson], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `followtrack_backup_${Date.now()}.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      addToast({
        type: 'success',
        title: 'Backup Downloaded',
        message: 'All snapshots and preferences exported to JSON file.',
      });
    } catch {
      addToast({
        type: 'error',
        title: 'Export Failed',
        message: 'Could not export database.',
      });
    }
  };

  const handleImportBackup = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const result = await storageService.importBackup(text);
      await refreshData();
      addToast({
        type: 'success',
        title: 'Backup Restored',
        message: `Restored ${result.snapshotCount} snapshots and ${result.actionCount} manual records.`,
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to parse backup';
      addToast({
        type: 'error',
        title: 'Restore Failed',
        message: msg,
      });
    }
    // reset input
    e.target.value = '';
  };

  const handleClearAllData = async () => {
    await storageService.clearAllData();
    await refreshData();
    setShowClearConfirm(false);
    addToast({
      type: 'success',
      title: 'Data Cleared',
      message: 'All snapshots and local data have been completely deleted.',
    });
    setCurrentPage('landing');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-extrabold text-[#F8FAFC]">Application Settings</h2>
        <p className="text-sm text-[#94A3B8] mt-1">
          Manage your local database, backup snapshots, and adjust preferences.
        </p>
      </div>

      {/* Preferences Section */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 shadow-xl space-y-6">
        <h3 className="text-base font-bold text-[#F8FAFC]">Preferences</h3>

        <div className="space-y-4">
          <div className="flex items-center justify-between pb-4 border-b border-[#252B38]">
            <div>
              <span className="text-sm font-semibold text-[#F8FAFC] block">
                Automatic Snapshot Comparison
              </span>
              <span className="text-xs text-[#94A3B8]">
                Automatically select the previous snapshot as baseline comparison
              </span>
            </div>
            <button
              onClick={() =>
                updateSettings({ autoComparePrevious: !settings.autoComparePrevious })
              }
              className={`w-11 h-6 rounded-full transition-colors relative ${
                settings.autoComparePrevious ? 'bg-[#8B5CF6]' : 'bg-[#252B38]'
              }`}
            >
              <div
                className={`w-4 h-4 rounded-full bg-white transition-transform absolute top-1 ${
                  settings.autoComparePrevious ? 'left-6' : 'left-1'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between pb-4 border-b border-[#252B38]">
            <div>
              <span className="text-sm font-semibold text-[#F8FAFC] block">
                Confirm Manual Unfollow Actions
              </span>
              <span className="text-xs text-[#94A3B8]">
                Show confirmation modal when opening Instagram profiles in Smart Unfollow Manager
              </span>
            </div>
            <button
              onClick={() =>
                updateSettings({ confirmUnfollowActions: !settings.confirmUnfollowActions })
              }
              className={`w-11 h-6 rounded-full transition-colors relative ${
                settings.confirmUnfollowActions ? 'bg-[#8B5CF6]' : 'bg-[#252B38]'
              }`}
            >
              <div
                className={`w-4 h-4 rounded-full bg-white transition-transform absolute top-1 ${
                  settings.confirmUnfollowActions ? 'left-6' : 'left-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Backup and Restore */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center space-x-2">
          <HardDrive className="w-5 h-5 text-[#8B5CF6]" />
          <h3 className="text-base font-bold text-[#F8FAFC]">Data Backup & Migration</h3>
        </div>
        <p className="text-xs text-[#94A3B8] leading-relaxed">
          Your data is stored exclusively in this browser's IndexedDB. Export a JSON backup to move your snapshots to another computer or browser, or restore an earlier backup.
        </p>

        <div className="pt-2 flex flex-wrap gap-3">
          <button
            onClick={handleExportBackup}
            className="px-4 py-2.5 rounded-xl bg-[#10141D] hover:bg-[#1C2433] text-xs font-semibold text-[#F8FAFC] border border-[#252B38] flex items-center space-x-2 transition-colors"
          >
            <Download className="w-4 h-4 text-[#8B5CF6]" />
            <span>Export Database Backup (.json)</span>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            className="hidden"
            onChange={handleImportBackup}
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2.5 rounded-xl bg-[#10141D] hover:bg-[#1C2433] text-xs font-semibold text-[#F8FAFC] border border-[#252B38] flex items-center space-x-2 transition-colors"
          >
            <Upload className="w-4 h-4 text-[#6366F1]" />
            <span>Restore Backup (.json)</span>
          </button>
        </div>
      </div>

      {/* Danger Zone: Clear Data */}
      <div className="bg-[#151B27] border border-[#EF4444]/30 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center space-x-2 text-[#EF4444]">
          <Trash2 className="w-5 h-5" />
          <h3 className="text-base font-bold">Danger Zone: Erase All Data</h3>
        </div>
        <p className="text-xs text-[#94A3B8] leading-relaxed">
          Permanently remove all snapshots, historical calculations, manual unfollow records, and preferences from your browser.
        </p>

        <button
          onClick={() => setShowClearConfirm(true)}
          className="px-4 py-2.5 rounded-xl bg-[#EF4444] hover:bg-[#DC2626] text-xs font-semibold text-white shadow-md shadow-[#EF4444]/20 transition-colors"
        >
          Erase All FollowTrack Data
        </button>
      </div>

      {/* About Box */}
      <div className="bg-[#10141D] border border-[#252B38] rounded-2xl p-5 flex items-center justify-between text-xs text-[#94A3B8]">
        <div>
          <span className="font-bold text-[#F8FAFC]">FollowTrack v1.0.0</span>
          <p className="text-[11px] mt-0.5">Built with React, Vite, TypeScript & IndexedDB</p>
        </div>
        <button
          onClick={() => setCurrentPage('privacy')}
          className="text-[#8B5CF6] hover:underline font-medium"
        >
          Read Security Guarantee
        </button>
      </div>

      {/* Confirmation Modal */}
      <ConfirmModal
        isOpen={showClearConfirm}
        title="Erase All Local Data?"
        message="This will completely clear your IndexedDB database and delete all saved Instagram snapshots. Make sure you have exported a backup if you wish to retain your history."
        confirmLabel="Erase Everything"
        isDestructive={true}
        onCancel={() => setShowClearConfirm(false)}
        onConfirm={handleClearAllData}
      />
    </div>
  );
};
