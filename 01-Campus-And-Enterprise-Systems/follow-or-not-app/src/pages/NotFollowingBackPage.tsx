import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { UserTable } from '../components/common/UserTable';
import { UserX, UserCog } from 'lucide-react';

export const NotFollowingBackPage: React.FC = () => {
  const { comparison, activeSnapshot, setCurrentPage } = useApp();
  const [selectedUsernames, setSelectedUsernames] = useState<Set<string>>(new Set());

  if (!activeSnapshot || !comparison) {
    return (
      <div className="text-center py-16 space-y-4">
        <UserX className="w-12 h-12 text-[#94A3B8] mx-auto" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">No Data Loaded</h3>
        <p className="text-xs text-[#94A3B8]">Import an Instagram export to see who does not follow you back.</p>
        <button
          onClick={() => setCurrentPage('import')}
          className="px-4 py-2 bg-[#8B5CF6] text-white text-xs font-semibold rounded-xl"
        >
          Import Data
        </button>
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
      {/* Top Banner with Quick Transfer to Unfollow Manager */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-[#F8FAFC]">
              Accounts That Don't Follow You Back
            </h3>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-[#F59E0B]/15 text-[#F59E0B]">
              {comparison.notFollowingBack.length} accounts
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-1 leading-relaxed">
            You are following these accounts, but they do not follow you in return.
            Use our Smart Unfollow Manager to curate these safely at your own pace without automated bot risk.
          </p>
        </div>

        <button
          onClick={() => setCurrentPage('smart-unfollow')}
          className="px-4 py-2.5 rounded-xl bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-xs font-semibold shadow-md shadow-[#8B5CF6]/20 transition-all flex items-center space-x-2 self-start md:self-auto shrink-0"
        >
          <UserCog className="w-4 h-4" />
          <span>Open Smart Unfollow Manager</span>
        </button>
      </div>

      <UserTable
        users={comparison.notFollowingBack}
        title="Not Following Back"
        subtitle={`From snapshot: ${activeSnapshot.name}`}
        showSelection={true}
        selectedUsernames={selectedUsernames}
        onToggleSelect={handleToggleSelect}
        onSelectAll={handleSelectAll}
        onDeselectAll={handleDeselectAll}
        badgeLabel="Doesn't follow back"
        badgeType="warning"
        emptyMessage="Congratulations! Everyone you follow is following you back."
      />
    </div>
  );
};
