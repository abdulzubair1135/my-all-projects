import React from 'react';
import { useApp } from '../context/AppContext';
import { UserTable } from '../components/common/UserTable';
import { Heart } from 'lucide-react';

export const FansPage: React.FC = () => {
  const { comparison, activeSnapshot, setCurrentPage } = useApp();

  if (!activeSnapshot || !comparison) {
    return (
      <div className="text-center py-16 space-y-4">
        <Heart className="w-12 h-12 text-[#94A3B8] mx-auto" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">No Data Loaded</h3>
        <p className="text-xs text-[#94A3B8]">Import your Instagram export to discover your fans.</p>
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
        users={comparison.fans}
        title="Your Fans"
        subtitle="Accounts following you whom you do not follow back"
        badgeLabel="Fan"
        badgeType="info"
        emptyMessage="You currently follow back everyone who follows you."
      />
    </div>
  );
};
