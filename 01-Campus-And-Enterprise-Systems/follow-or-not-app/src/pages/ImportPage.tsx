import React, { useState, useRef } from 'react';
import { useApp } from '../context/AppContext';
import { InstagramImportService } from '../services/InstagramImportService';
import { storageService } from '../services/StorageService';
import { SampleDataService } from '../services/SampleDataService';
import type { ImportProgress, Snapshot } from '../types';
import {
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Sparkles,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react';

export const ImportPage: React.FC = () => {
  const { setCurrentPage, refreshData, addToast } = useApp();
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState<ImportProgress | null>(null);
  const [customSnapshotName, setCustomSnapshotName] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleProcessFiles = async (files: FileList | File[]) => {
    if (!files || files.length === 0) return;
    setErrorMsg(null);

    const fileArray = Array.from(files);
    const isZip = fileArray.length === 1 && fileArray[0].name.toLowerCase().endsWith('.zip');

    try {
      let followers: any[] = [];
      let following: any[] = [];
      let filesProcessed: string[] = [];

      if (isZip) {
        const result = await InstagramImportService.processZipFile(fileArray[0], (p) => {
          setProgress(p);
        });
        followers = result.followers;
        following = result.following;
        filesProcessed = result.filesProcessed;
      } else {
        // Multiple JSON files dropped
        const result = await InstagramImportService.processMultipleJsonFiles(fileArray, (p) => {
          setProgress(p);
        });
        followers = result.followers;
        following = result.following;
        filesProcessed = result.filesProcessed;
      }

      // Create and save Snapshot
      setProgress({
        step: 'creating_snapshot',
        progress: 95,
        title: 'Saving Snapshot',
        description: 'Writing data securely to local browser IndexedDB...',
      });

      const snapshotId = `snap_${Date.now()}`;
      const name =
        customSnapshotName.trim() ||
        `Export ${new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;

      const newSnapshot: Snapshot = {
        id: snapshotId,
        name,
        createdAt: Date.now(),
        followers,
        following,
        followersCount: followers.length,
        followingCount: following.length,
        sourceFile: isZip ? fileArray[0].name : `${fileArray.length} JSON files`,
      };

      await storageService.saveSnapshot(newSnapshot);
      await refreshData();

      setProgress({
        step: 'completed',
        progress: 100,
        title: 'Import Complete!',
        description: `Successfully analyzed ${followers.length} followers and ${following.length} following.`,
        details: {
          followersFound: followers.length,
          followingFound: following.length,
          filesFound: filesProcessed,
        },
      });

      addToast({
        type: 'success',
        title: 'Snapshot Saved',
        message: `${name}: ${followers.length} followers, ${following.length} following.`,
      });

      setTimeout(() => {
        setCurrentPage('dashboard');
      }, 1500);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to import files.';
      setErrorMsg(msg);
      setProgress({
        step: 'error',
        progress: 100,
        title: 'Import Failed',
        description: msg,
        error: msg,
      });
      addToast({
        type: 'error',
        title: 'Import Error',
        message: msg,
      });
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleProcessFiles(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleLoadDemo = async () => {
    try {
      const { snapshot1, snapshot2 } = SampleDataService.getSampleSnapshots();
      await storageService.saveSnapshot(snapshot1);
      await storageService.saveSnapshot(snapshot2);
      await refreshData();
      addToast({
        type: 'success',
        title: 'Demo Snapshots Ready',
        message: 'Imported baseline and comparison snapshots.',
      });
      setCurrentPage('dashboard');
    } catch {
      addToast({
        type: 'error',
        title: 'Failed',
        message: 'Could not load demo snapshots.',
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-extrabold text-[#F8FAFC]">Import Instagram Data</h2>
        <p className="text-sm text-[#94A3B8] mt-1">
          Upload your official Instagram data export ZIP or extracted JSON files. Everything is processed locally in your browser.
        </p>
      </div>

      {/* Snapshot Label Config */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <label className="text-xs font-semibold text-[#F8FAFC] block">
            Snapshot Name (Optional)
          </label>
          <span className="text-[11px] text-[#94A3B8]">
            Give this snapshot a label (e.g. "Export End of Month", "Before Campaign")
          </span>
        </div>
        <input
          type="text"
          value={customSnapshotName}
          onChange={(e) => setCustomSnapshotName(e.target.value)}
          placeholder="e.g. Export Oct 31"
          className="bg-[#10141D] text-[#F8FAFC] placeholder-[#94A3B8] text-xs px-3.5 py-2.5 rounded-xl border border-[#252B38] focus:outline-none focus:border-[#8B5CF6] sm:w-64"
        />
      </div>

      {/* Upload Dropzone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        className={`bg-[#151B27] border-2 border-dashed rounded-3xl p-10 md:p-14 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-[#8B5CF6] bg-[#8B5CF6]/5 scale-[0.99]'
            : 'border-[#252B38] hover:border-[#8B5CF6]/50 hover:bg-[#1C2433]/30'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip,.json,.html"
          multiple
          className="hidden"
          onChange={(e) => {
            if (e.target.files) handleProcessFiles(e.target.files);
          }}
        />

        <div className="max-w-md mx-auto space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-[#8B5CF6]/20 to-[#6366F1]/20 border border-[#8B5CF6]/30 text-[#8B5CF6] flex items-center justify-center mx-auto shadow-lg shadow-[#8B5CF6]/10">
            <UploadCloud className="w-8 h-8" />
          </div>

          <div>
            <h3 className="text-lg font-bold text-[#F8FAFC]">
              Drop your Instagram Export ZIP or JSON files here
            </h3>
            <p className="text-xs text-[#94A3B8] mt-1.5 leading-relaxed">
              Supports full <code className="text-[#8B5CF6]">.zip</code> archives or multiple individual{' '}
              <code className="text-[#8B5CF6]">followers_*.json</code> and <code className="text-[#8B5CF6]">following.json</code> files.
            </p>
          </div>

          <div className="pt-2">
            <span className="inline-flex items-center px-4 py-2 rounded-xl bg-[#8B5CF6] text-white text-xs font-semibold shadow-md shadow-[#8B5CF6]/20 hover:bg-[#7C3AED] transition-all">
              Browse Files on Computer
            </span>
          </div>

          <p className="text-[11px] text-[#94A3B8] pt-2">
            Never uploads to external servers. Safe client-side execution.
          </p>
        </div>
      </div>

      {/* Progress Box (when importing) */}
      {progress && (
        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 shadow-xl space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {progress.step === 'completed' ? (
                <CheckCircle2 className="w-6 h-6 text-[#22C55E]" />
              ) : progress.step === 'error' ? (
                <AlertCircle className="w-6 h-6 text-[#EF4444]" />
              ) : (
                <RefreshCw className="w-6 h-6 text-[#8B5CF6] animate-spin" />
              )}
              <div>
                <h4 className="text-sm font-bold text-[#F8FAFC]">{progress.title}</h4>
                <p className="text-xs text-[#94A3B8]">{progress.description}</p>
              </div>
            </div>
            <span className="text-xs font-mono font-bold text-[#8B5CF6]">
              {progress.progress}%
            </span>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-[#10141D] rounded-full h-2 overflow-hidden border border-[#252B38]">
            <div
              className={`h-full transition-all duration-300 ${
                progress.step === 'error'
                  ? 'bg-[#EF4444]'
                  : progress.step === 'completed'
                  ? 'bg-[#22C55E]'
                  : 'bg-gradient-to-r from-[#8B5CF6] to-[#6366F1]'
              }`}
              style={{ width: `${progress.progress}%` }}
            />
          </div>

          {progress.details && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs">
              <div className="bg-[#10141D] p-3 rounded-xl border border-[#252B38]">
                <span className="text-[#94A3B8] block text-[10px]">Followers Found</span>
                <span className="text-base font-bold text-[#F8FAFC]">
                  {progress.details.followersFound}
                </span>
              </div>
              <div className="bg-[#10141D] p-3 rounded-xl border border-[#252B38]">
                <span className="text-[#94A3B8] block text-[10px]">Following Found</span>
                <span className="text-base font-bold text-[#F8FAFC]">
                  {progress.details.followingFound}
                </span>
              </div>
              <div className="bg-[#10141D] p-3 rounded-xl border border-[#252B38] col-span-2 sm:col-span-1">
                <span className="text-[#94A3B8] block text-[10px]">Files Identified</span>
                <span className="text-base font-bold text-[#8B5CF6]">
                  {progress.details.filesFound.length}
                </span>
              </div>
            </div>
          )}

          {errorMsg && (
            <div className="p-3 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-xl text-xs text-[#EF4444]">
              {errorMsg}
            </div>
          )}
        </div>
      )}

      {/* Demo Data Quick Action */}
      <div className="bg-gradient-to-r from-[#8B5CF6]/10 to-[#6366F1]/10 border border-[#8B5CF6]/30 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#8B5CF6]/20 text-[#8B5CF6] flex items-center justify-center shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-[#F8FAFC]">
              Don't have your Instagram ZIP export handy?
            </h4>
            <p className="text-xs text-[#94A3B8] mt-0.5">
              Load realistic sample data containing two historical snapshots to immediately explore unfollowers, mutuals, and charts.
            </p>
          </div>
        </div>

        <button
          onClick={handleLoadDemo}
          className="px-4 py-2.5 rounded-xl bg-[#8B5CF6] hover:bg-[#7C3AED] text-xs font-semibold text-white shadow-md shadow-[#8B5CF6]/20 shrink-0 transition-colors"
        >
          Load Realistic Demo Snapshots
        </button>
      </div>

      {/* Step-by-Step Instructions */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 space-y-4">
        <div className="flex items-center space-x-2">
          <HelpCircle className="w-4 h-4 text-[#8B5CF6]" />
          <h3 className="text-sm font-bold text-[#F8FAFC]">
            How to Download Your Official Instagram Data Export
          </h3>
        </div>

        <ol className="text-xs text-[#94A3B8] space-y-3 list-decimal list-inside leading-relaxed pl-1">
          <li>
            Open the <strong className="text-[#F8FAFC]">Instagram app</strong> or visit{' '}
            <strong className="text-[#F8FAFC]">instagram.com</strong> on your computer.
          </li>
          <li>
            Go to your Profile &rarr; Menu (3 lines) &rarr; <strong className="text-[#F8FAFC]">Accounts Center</strong> &rarr;{' '}
            <strong className="text-[#F8FAFC]">Your information and permissions</strong>.
          </li>
          <li>
            Click <strong className="text-[#F8FAFC]">Download your information</strong> &rarr; Select{' '}
            <strong className="text-[#F8FAFC]">Download or transfer information</strong>.
          </li>
          <li>
            Select <strong className="text-[#F8FAFC]">Some of your information</strong> and choose{' '}
            <strong className="text-[#F8FAFC]">Followers and following</strong>.
          </li>
          <li>
            Select <strong className="text-[#F8FAFC]">Download to device</strong>, and choose{' '}
            <strong className="text-[#8B5CF6]">Format: JSON</strong> (recommended) or HTML, and Date range:{' '}
            <strong className="text-[#F8FAFC]">All time</strong>.
          </li>
          <li>
            When Meta emails you that your download is ready (usually 5–15 minutes), download the ZIP file and drop it right into FollowTrack!
          </li>
        </ol>

        <div className="pt-2 flex items-center space-x-2 text-[11px] text-[#22C55E]">
          <ShieldCheck className="w-4 h-4 shrink-0" />
          <span>This is 100% compliant with Instagram Terms of Service and requires zero credentials.</span>
        </div>
      </div>
    </div>
  );
};
