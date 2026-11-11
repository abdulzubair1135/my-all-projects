import React from 'react';
import { useApp } from '../context/AppContext';
import { UserTable } from '../components/common/UserTable';
import { UserCheck } from 'lucide-react';

export const FollowingPage: React.FC = () => {
  const { activeSnapshot, setCurrentPage } = useApp();

  if (!activeSnapshot) {
    return (
      <div className="text-center py-16 space-y-4">
        <UserCheck className="w-12 h-12 text-[#94A3B8] mx-auto" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">No Following Data Available</h3>
        <p className="text-xs text-[#94A3B8]">Please import your Instagram export to view your following list.</p>
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
        users={activeSnapshot.following}
        title="Following"
        subtitle={`All accounts you are currently following in snapshot: ${activeSnapshot.name}`}
        emptyMessage="No following records found in this snapshot."
      />
    </div>
  );
};
