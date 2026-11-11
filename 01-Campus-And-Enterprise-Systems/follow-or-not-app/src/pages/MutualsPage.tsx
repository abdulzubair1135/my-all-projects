import React from 'react';
import { useApp } from '../context/AppContext';
import { UserTable } from '../components/common/UserTable';
import { Repeat } from 'lucide-react';

export const MutualsPage: React.FC = () => {
  const { comparison, activeSnapshot, setCurrentPage } = useApp();

  if (!activeSnapshot || !comparison) {
    return (
      <div className="text-center py-16 space-y-4">
        <Repeat className="w-12 h-12 text-[#94A3B8] mx-auto" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">No Data Loaded</h3>
        <p className="text-xs text-[#94A3B8]">Import your Instagram export to view your mutual followers.</p>
        <button
          onClick={() => setCurrentPage('import')}
          className="px-4 py-2 bg-[#8B5CF6] text-white text-xs font-semibold rounded-xl"
        >
          Import Data
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      <UserTable
        users={comparison.mutuals}
        title="Mutual Followers"
        subtitle="Accounts where both of you follow each other"
        badgeLabel="Mutual"
        badgeType="success"
        emptyMessage="No mutual connections found in this snapshot."
      />
    </div>
  );
};
