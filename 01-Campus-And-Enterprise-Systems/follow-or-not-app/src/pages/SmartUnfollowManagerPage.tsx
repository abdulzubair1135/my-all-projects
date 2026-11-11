import React, { useState, useMemo } from 'react';
import { useApp } from '../context/AppContext';
import { ConfirmModal } from '../components/common/ConfirmModal';
import {
  UserCog,
  ExternalLink,
  ShieldAlert,
  CheckCircle2,
  BookmarkCheck,
  Search,
  CheckSquare,
  Square,
  RotateCcw,
} from 'lucide-react';
import type { InstagramUser } from '../types';

export const SmartUnfollowManagerPage: React.FC = () => {
  const { comparison, activeSnapshot, manualActions, markManualAction, removeManualAction, addToast, setCurrentPage } = useApp();

  const [search, setSearch] = useState('');
  const [filterMode, setFilterMode] = useState<'all' | 'pending' | 'unfollowed' | 'whitelist'>('pending');
  const [selectedUsernames, setSelectedUsernames] = useState<Set<string>>(new Set());
  const [confirmModalData, setConfirmModalData] = useState<{
    isOpen: boolean;
    type: 'mark_unfollowed' | 'batch_unfollow' | 'whitelist';
    user?: InstagramUser;
  }>({ isOpen: false, type: 'mark_unfollowed' });

  // Base list of accounts not following back
  const notFollowingBackList = comparison ? comparison.notFollowingBack : [];

  // Filter accounts
  const filteredAccounts = useMemo(() => {
    let list = notFollowingBackList;

    if (search.trim()) {
      const q = search.toLowerCase().trim();
      list = list.filter((u) => u.username.includes(q) || (u.originalUsername && u.originalUsername.toLowerCase().includes(q)));
    }

    if (filterMode === 'pending') {
      list = list.filter((u) => !manualActions.has(u.username));
    } else if (filterMode === 'unfollowed') {
      list = list.filter((u) => manualActions.get(u.username)?.status === 'unfollowed');
    } else if (filterMode === 'whitelist') {
      list = list.filter((u) => manualActions.get(u.username)?.status === 'whitelist');
    }

    return list;
  }, [notFollowingBackList, search, filterMode, manualActions]);

  const toggleSelect = (username: string) => {
    setSelectedUsernames((prev) => {
      const next = new Set(prev);
      if (next.has(username)) next.delete(username);
      else next.add(username);
      return next;
    });
  };

  const handleSelectAll = () => {
    setSelectedUsernames(new Set(filteredAccounts.map((u) => u.username)));
  };

  const handleDeselectAll = () => {
    setSelectedUsernames(new Set());
  };

  const handleOpenProfileAndConfirm = (user: InstagramUser) => {
    window.open(user.profileUrl, '_blank', 'noopener,noreferrer');
    // Open modal to confirm manual action
    setConfirmModalData({
      isOpen: true,
      type: 'mark_unfollowed',
      user,
    });
  };

  const handleWhitelistAccount = async (user: InstagramUser) => {
    await markManualAction(user.username, 'whitelist', 'Added to safe whitelist');
    addToast({
      type: 'success',
      title: 'Whitelisted',
      message: `@${user.username} will be preserved in your following list.`,
    });
  };

  const handleBatchMarkUnfollowed = () => {
    if (selectedUsernames.size === 0) return;
    setConfirmModalData({
      isOpen: true,
      type: 'batch_unfollow',
    });
  };

  const handleConfirmAction = async () => {
    if (confirmModalData.type === 'mark_unfollowed' && confirmModalData.user) {
      await markManualAction(confirmModalData.user.username, 'unfollowed', 'Manually unfollowed on Instagram');
      addToast({
        type: 'success',
        title: 'Marked as Unfollowed',
        message: `@${confirmModalData.user.username} marked in local audit log.`,
      });
      // Remove from selection if present
      setSelectedUsernames((prev) => {
        const next = new Set(prev);
        next.delete(confirmModalData.user!.username);
        return next;
      });
    } else if (confirmModalData.type === 'batch_unfollow') {
      for (const username of selectedUsernames) {
        await markManualAction(username, 'unfollowed', 'Batch marked as unfollowed');
      }
      addToast({
        type: 'success',
        title: 'Batch Completed',
        message: `Marked ${selectedUsernames.size} accounts as unfollowed.`,
      });
      setSelectedUsernames(new Set());
    }

    setConfirmModalData({ isOpen: false, type: 'mark_unfollowed' });
  };

  if (!activeSnapshot || !comparison) {
    return (
      <div className="text-center py-16 space-y-4">
        <UserCog className="w-12 h-12 text-[#94A3B8] mx-auto" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">No Data Loaded</h3>
        <p className="text-xs text-[#94A3B8]">Import your Instagram data to manage accounts not following back.</p>
        <button
          onClick={() => setCurrentPage('import')}
          className="px-4 py-2 bg-[#8B5CF6] text-white text-xs font-semibold rounded-xl"
        >
          Import Data
        </button>
      </div>
    );
  }

  const unfollowedCount = Array.from(manualActions.values()).filter((a) => a.status === 'unfollowed').length;
  const whitelistedCount = Array.from(manualActions.values()).filter((a) => a.status === 'whitelist').length;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-extrabold text-[#F8FAFC]">Smart Unfollow Manager</h2>
        <p className="text-sm text-[#94A3B8] mt-1">
          Safely curate non-reciprocal follows with our guided manual workflow and rate-limit guardrails.
        </p>
      </div>

      {/* Safety & Platform Advisory Notice */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5 space-y-3">
        <div className="flex items-center space-x-2.5 text-sm font-bold text-[#F8FAFC]">
          <ShieldAlert className="w-5 h-5 text-[#8B5CF6] shrink-0" />
          <span>Safe Personal Instagram Curating Guide</span>
        </div>
        <p className="text-xs text-[#94A3B8] leading-relaxed">
          Instagram’s platform does not support automated background mass-unfollowing. Automated bot extensions that click on your behalf put your account at high risk of shadowbanning or permanent action blocks. FollowTrack guides you through a safe manual review with direct profile links and local audit logging.
        </p>
        <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-[#22C55E]">
          <span className="flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Recommended Pace: 10–15 unfollows per session</span>
          </span>
          <span className="flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Actions tracked purely on your local machine</span>
          </span>
        </div>
      </div>

      {/* Stats Counter Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
        <div className="bg-[#151B27] border border-[#252B38] rounded-xl p-3.5">
          <span className="text-[10px] text-[#94A3B8] block">Not Following Back</span>
          <span className="text-xl font-bold text-[#F8FAFC]">{notFollowingBackList.length}</span>
        </div>
        <div className="bg-[#151B27] border border-[#252B38] rounded-xl p-3.5">
          <span className="text-[10px] text-[#94A3B8] block">Pending Review</span>
          <span className="text-xl font-bold text-[#F59E0B]">
            {notFollowingBackList.length - unfollowedCount - whitelistedCount}
          </span>
        </div>
        <div className="bg-[#151B27] border border-[#252B38] rounded-xl p-3.5">
          <span className="text-[10px] text-[#94A3B8] block">Marked Unfollowed</span>
          <span className="text-xl font-bold text-[#EF4444]">{unfollowedCount}</span>
        </div>
        <div className="bg-[#151B27] border border-[#252B38] rounded-xl p-3.5">
          <span className="text-[10px] text-[#94A3B8] block">Whitelisted (Keep)</span>
          <span className="text-xl font-bold text-[#22C55E]">{whitelistedCount}</span>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl overflow-hidden shadow-xl">
        {/* Filter bar */}
        <div className="p-4 border-b border-[#252B38] flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setFilterMode('pending')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                filterMode === 'pending'
                  ? 'bg-[#8B5CF6] text-white'
                  : 'bg-[#10141D] text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Pending ({notFollowingBackList.length - unfollowedCount - whitelistedCount})
            </button>
            <button
              onClick={() => setFilterMode('all')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                filterMode === 'all'
                  ? 'bg-[#8B5CF6] text-white'
                  : 'bg-[#10141D] text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              All ({notFollowingBackList.length})
            </button>
            <button
              onClick={() => setFilterMode('unfollowed')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                filterMode === 'unfollowed'
                  ? 'bg-[#8B5CF6] text-white'
                  : 'bg-[#10141D] text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Marked Unfollowed ({unfollowedCount})
            </button>
            <button
              onClick={() => setFilterMode('whitelist')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                filterMode === 'whitelist'
                  ? 'bg-[#8B5CF6] text-white'
                  : 'bg-[#10141D] text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
            >
              Whitelisted ({whitelistedCount})
            </button>
          </div>

          <div className="flex items-center space-x-2.5">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search username..."
                className="bg-[#10141D] text-[#F8FAFC] placeholder-[#94A3B8] text-xs pl-8 pr-3 py-1.5 rounded-xl border border-[#252B38] focus:outline-none focus:border-[#8B5CF6]"
              />
            </div>

            {selectedUsernames.size > 0 && (
              <button
                onClick={handleBatchMarkUnfollowed}
                className="px-3 py-1.5 rounded-xl bg-[#EF4444] hover:bg-[#DC2626] text-white text-xs font-semibold transition-colors shadow-md shadow-[#EF4444]/20"
              >
                Mark Selected ({selectedUsernames.size}) as Unfollowed
              </button>
            )}
          </div>
        </div>

        {/* Selection bar */}
        <div className="px-5 py-2.5 bg-[#10141D]/60 border-b border-[#252B38] flex items-center justify-between text-xs text-[#94A3B8]">
          <div className="flex items-center space-x-3">
            <button
              onClick={selectedUsernames.size === filteredAccounts.length ? handleDeselectAll : handleSelectAll}
              className="flex items-center space-x-2 text-[#F8FAFC] hover:text-[#8B5CF6] transition-colors"
            >
              {selectedUsernames.size === filteredAccounts.length && filteredAccounts.length > 0 ? (
                <CheckSquare className="w-4 h-4 text-[#8B5CF6]" />
              ) : (
                <Square className="w-4 h-4 text-[#94A3B8]" />
              )}
              <span>
                {selectedUsernames.size === filteredAccounts.length && filteredAccounts.length > 0
                  ? 'Deselect All'
                  : 'Select All Filtered'}
              </span>
            </button>
            <span>•</span>
            <span>{selectedUsernames.size} accounts selected</span>
          </div>

          {selectedUsernames.size > 0 && (
            <button onClick={handleDeselectAll} className="text-[#EF4444] hover:underline">
              Clear
            </button>
          )}
        </div>

        {/* List of Accounts */}
        <div className="divide-y divide-[#252B38]/60">
          {filteredAccounts.length === 0 ? (
            <div className="py-16 text-center text-xs text-[#94A3B8]">
              No accounts match the selected filter.
            </div>
          ) : (
            filteredAccounts.map((user) => {
              const isSelected = selectedUsernames.has(user.username);
              const manualRecord = manualActions.get(user.username);

              return (
                <div
                  key={user.username}
                  className={`p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-[#1C2433]/40 transition-colors ${
                    isSelected ? 'bg-[#8B5CF6]/5' : ''
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => toggleSelect(user.username)}
                      className="text-[#94A3B8] hover:text-[#8B5CF6] p-1"
                    >
                      {isSelected ? (
                        <CheckSquare className="w-4 h-4 text-[#8B5CF6]" />
                      ) : (
                        <Square className="w-4 h-4 text-[#94A3B8]" />
                      )}
                    </button>

                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-[#F59E0B] to-[#EF4444] flex items-center justify-center font-bold text-white text-xs shrink-0 shadow-xs">
                      {user.username.substring(0, 1).toUpperCase()}
                    </div>

                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-bold text-[#F8FAFC]">
                          @{user.originalUsername || user.username}
                        </span>
                        {manualRecord && (
                          <span
                            className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                              manualRecord.status === 'unfollowed'
                                ? 'bg-[#EF4444]/15 text-[#EF4444]'
                                : 'bg-[#22C55E]/15 text-[#22C55E]'
                            }`}
                          >
                            {manualRecord.status === 'unfollowed' ? 'Unfollowed Locally' : 'Whitelisted'}
                          </span>
                        )}
                      </div>
                      <span className="text-[11px] text-[#94A3B8]">
                        Does not follow you back
                      </span>
                    </div>
                  </div>

                  {/* Actions for this user */}
                  <div className="flex items-center space-x-2 self-end sm:self-auto">
                    {/* Open profile on IG */}
                    <button
                      onClick={() => handleOpenProfileAndConfirm(user)}
                      className="px-3 py-1.5 rounded-xl bg-[#10141D] hover:bg-[#1C2433] text-xs font-semibold text-[#8B5CF6] border border-[#252B38] flex items-center space-x-1.5 transition-colors"
                    >
                      <span>Open & Unfollow</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>

                    {/* Whitelist button */}
                    {(!manualRecord || manualRecord.status !== 'whitelist') && (
                      <button
                        onClick={() => handleWhitelistAccount(user)}
                        className="p-1.5 rounded-xl text-[#94A3B8] hover:text-[#22C55E] hover:bg-[#10141D] transition-colors"
                        title="Add to Whitelist (Don't unfollow)"
                      >
                        <BookmarkCheck className="w-4 h-4" />
                      </button>
                    )}

                    {/* Reset manual state */}
                    {manualRecord && (
                      <button
                        onClick={() => removeManualAction(user.username)}
                        className="p-1.5 rounded-xl text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#10141D] transition-colors"
                        title="Reset state"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Confirmation Modal */}
      <ConfirmModal
        isOpen={confirmModalData.isOpen}
        title={
          confirmModalData.type === 'batch_unfollow'
            ? `Mark ${selectedUsernames.size} Accounts as Unfollowed?`
            : `Did you unfollow @${confirmModalData.user?.username}?`
        }
        message={
          confirmModalData.type === 'batch_unfollow'
            ? `This updates your local audit trail to record these ${selectedUsernames.size} accounts as unfollowed. Remember to pace manual unfollows on Instagram.`
            : `Instagram profile opened in a new tab. After clicking "Unfollow" on their Instagram profile, confirm here to mark them as unfollowed in your local FollowTrack database.`
        }
        confirmLabel="Yes, Mark Unfollowed"
        cancelLabel="Not Yet / Cancel"
        onCancel={() => setConfirmModalData({ isOpen: false, type: 'mark_unfollowed' })}
        onConfirm={handleConfirmAction}
      />
    </div>
  );
};
