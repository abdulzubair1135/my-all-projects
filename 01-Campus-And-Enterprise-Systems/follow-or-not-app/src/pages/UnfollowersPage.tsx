import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { UserTable } from '../components/common/UserTable';
import { UserMinus, AlertCircle, UploadCloud } from 'lucide-react';

export const UnfollowersPage: React.FC = () => {
  const { comparison, previousSnapshot, activeSnapshot, setCurrentPage } = useApp();
  const [selectedUsernames, setSelectedUsernames] = useState<Set<string>>(new Set());

  if (!activeSnapshot || !comparison) {
    return (
      <div className="text-center py-16 space-y-4">
        <UserMinus className="w-12 h-12 text-[#94A3B8] mx-auto" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">No Data Loaded</h3>
        <p className="text-xs text-[#94A3B8]">Import an Instagram export to detect unfollowers.</p>
        <button
          onClick={() => setCurrentPage('import')}
          className="px-4 py-2 bg-[#8B5CF6] text-white text-xs font-semibold rounded-xl"
        >
          Import Data
        </button>
      </div>
    );
  }

  if (!comparison.hasPreviousSnapshot || !previousSnapshot) {
    return (
      <div className="max-w-2xl mx-auto bg-[#151B27] border border-[#252B38] rounded-2xl p-8 text-center space-y-4 my-8">
        <div className="w-12 h-12 rounded-2xl bg-[#F59E0B]/15 text-[#F59E0B] flex items-center justify-center mx-auto">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-[#F8FAFC]">
          Historical Baseline Established
        </h3>
        <p className="text-xs text-[#94A3B8] leading-relaxed">
          True unfollower detection requires at least <strong className="text-[#F8FAFC]">two snapshots</strong> taken at different times.
          Currently, FollowTrack has recorded your snapshot from{' '}
          <strong className="text-[#F8FAFC]">
            {new Date(activeSnapshot.createdAt).toLocaleDateString()}
          </strong>.
        </p>
        <p className="text-xs text-[#94A3B8] leading-relaxed">
          When you download your next export from Instagram (in a few days or weeks), upload it to FollowTrack.
          Any account that was present today but missing in your next export will be identified right here with zero false positives.
        </p>

        <div className="pt-2 flex items-center justify-center gap-3">
          <button
            onClick={() => setCurrentPage('import')}
            className="px-4 py-2 rounded-xl bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-xs font-semibold shadow-md shadow-[#8B5CF6]/20 transition-all flex items-center space-x-1.5"
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload Another Snapshot</span>
          </button>
        </div>
      </div>
    );
  }

  const handleToggleSelect = (username: string) => {
    setSelectedUsernames((prev) => {
      const next = new Set(prev);
      if (next.has(username)) next.delete(username);
      else next.add(username);
      return next;
    });
  };

  const handleSelectAll = (usernames: string[]) => {
    setSelectedUsernames(new Set(usernames));
  };

  const handleDeselectAll = () => {
    setSelectedUsernames(new Set());
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Baseline comparison banner */}
      <div className="bg-[#10141D] border border-[#252B38] rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#EF4444]/15 text-[#EF4444] flex items-center justify-center font-bold">
            <UserMinus className="w-4 h-4" />
          </div>
          <div>
            <span className="font-bold text-[#F8FAFC]">
              Detection Baseline: {previousSnapshot.name} &rarr; {activeSnapshot.name}
            </span>
            <p className="text-[11px] text-[#94A3B8]">
              Previous: {new Date(previousSnapshot.createdAt).toLocaleDateString()} | Detected:{' '}
              {new Date(activeSnapshot.createdAt).toLocaleDateString()}
            </p>
          </div>
        </div>

        <button
          onClick={() => setCurrentPage('history')}
          className="text-[#8B5CF6] hover:underline font-medium self-start sm:self-auto"
        >
          Change comparison snapshots
        </button>
      </div>

      <UserTable
        users={comparison.unfollowers}
        title="People Who Unfollowed You"
        subtitle={`Accounts present in ${previousSnapshot.name} but absent in ${activeSnapshot.name}`}
        showSelection={true}
        selectedUsernames={selectedUsernames}
        onToggleSelect={handleToggleSelect}
        onSelectAll={handleSelectAll}
        onDeselectAll={handleDeselectAll}
        badgeLabel="Unfollowed"
        badgeType="danger"
        emptyMessage="Great news! No accounts unfollowed you between these two snapshots."
      />
    </div>
  );
};
