import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { FollowerComparisonService } from '../services/FollowerComparisonService';
import { ConfirmModal } from '../components/common/ConfirmModal';
import {
  History,
  Trash2,
  Layers,
  ExternalLink,
} from 'lucide-react';
import type { ComparisonResult } from '../types';

export const HistoryPage: React.FC = () => {
  const {
    snapshots,
    activeSnapshot,
    setActiveSnapshotId,
    deleteSnapshot,
    setCurrentPage,
  } = useApp();

  const [compareSnapAId, setCompareSnapAId] = useState<string>(
    snapshots.length > 1 ? snapshots[1].id : snapshots[0]?.id || ''
  );
  const [compareSnapBId, setCompareSnapBId] = useState<string>(
    snapshots[0]?.id || ''
  );
  const [snapshotToDelete, setSnapshotToDelete] = useState<string | null>(null);

  const snapA = snapshots.find((s) => s.id === compareSnapAId);
  const snapB = snapshots.find((s) => s.id === compareSnapBId);

  const customComparison: ComparisonResult | null =
    snapA && snapB
      ? FollowerComparisonService.compareTwoSnapshots(snapA, snapB)
      : null;

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-extrabold text-[#F8FAFC]">Snapshot History & Comparison</h2>
        <p className="text-sm text-[#94A3B8] mt-1">
          Review saved exports, compare any two points in time, and audit your follower retention.
        </p>
      </div>

      {snapshots.length === 0 ? (
        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-10 text-center space-y-3">
          <History className="w-10 h-10 text-[#94A3B8] mx-auto" />
          <h3 className="text-base font-bold text-[#F8FAFC]">No Snapshots Recorded</h3>
          <p className="text-xs text-[#94A3B8]">Import your Instagram data to start building your history.</p>
          <button
            onClick={() => setCurrentPage('import')}
            className="px-4 py-2 bg-[#8B5CF6] text-white text-xs font-semibold rounded-xl"
          >
            Import Data
          </button>
        </div>
      ) : (
        <>
          {/* Custom Snapshot Comparison Engine */}
          <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 shadow-xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#252B38] pb-4">
              <div>
                <h3 className="text-base font-bold text-[#F8FAFC]">Custom Comparison Tool</h3>
                <p className="text-xs text-[#94A3B8]">
                  Select an earlier baseline snapshot and compare against a later target snapshot
                </p>
              </div>
              <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-[#8B5CF6]/15 text-[#8B5CF6] border border-[#8B5CF6]/30 self-start sm:self-auto">
                Set-Based Differencing Engine
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#94A3B8] mb-1.5">
                  Earlier Snapshot (Baseline A):
                </label>
                <select
                  value={compareSnapAId}
                  onChange={(e) => setCompareSnapAId(e.target.value)}
                  className="w-full bg-[#10141D] text-[#F8FAFC] border border-[#252B38] rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-[#8B5CF6]"
                >
                  {snapshots.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({new Date(s.createdAt).toLocaleDateString()}) - {s.followersCount} followers
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#94A3B8] mb-1.5">
                  Later Snapshot (Target B):
                </label>
                <select
                  value={compareSnapBId}
                  onChange={(e) => setCompareSnapBId(e.target.value)}
                  className="w-full bg-[#10141D] text-[#F8FAFC] border border-[#252B38] rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-[#8B5CF6]"
                >
                  {snapshots.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({new Date(s.createdAt).toLocaleDateString()}) - {s.followersCount} followers
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Comparison Metrics Output */}
            {customComparison && snapA && snapB && (
              <div className="bg-[#10141D] border border-[#252B38] rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between text-xs text-[#94A3B8]">
                  <span>
                    Comparing: <strong className="text-[#F8FAFC]">{snapA.name}</strong> &rarr;{' '}
                    <strong className="text-[#F8FAFC]">{snapB.name}</strong>
                  </span>
                  <span>
                    {Math.round(
                      Math.abs(snapB.createdAt - snapA.createdAt) / (1000 * 60 * 60 * 24)
                    )}{' '}
                    days apart
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-[#151B27] p-3 rounded-xl border border-[#252B38]">
                    <span className="text-[10px] text-[#94A3B8] block">New Followers Gained</span>
                    <span className="text-xl font-bold text-[#22C55E]">
                      +{customComparison.newFollowers.length}
                    </span>
                  </div>

                  <div className="bg-[#151B27] p-3 rounded-xl border border-[#252B38]">
                    <span className="text-[10px] text-[#94A3B8] block">Followers Lost (Unfollowed)</span>
                    <span className="text-xl font-bold text-[#EF4444]">
                      -{customComparison.unfollowers.length}
                    </span>
                  </div>

                  <div className="bg-[#151B27] p-3 rounded-xl border border-[#252B38]">
                    <span className="text-[10px] text-[#94A3B8] block">Net Follower Growth</span>
                    <span
                      className={`text-xl font-bold ${
                        customComparison.netFollowerGrowth >= 0 ? 'text-[#22C55E]' : 'text-[#EF4444]'
                      }`}
                    >
                      {customComparison.netFollowerGrowth >= 0 ? '+' : ''}
                      {customComparison.netFollowerGrowth}
                    </span>
                  </div>

                  <div className="bg-[#151B27] p-3 rounded-xl border border-[#252B38]">
                    <span className="text-[10px] text-[#94A3B8] block">Net Following Change</span>
                    <span
                      className={`text-xl font-bold ${
                        customComparison.netFollowingGrowth >= 0 ? 'text-[#6366F1]' : 'text-[#94A3B8]'
                      }`}
                    >
                      {customComparison.netFollowingGrowth >= 0 ? '+' : ''}
                      {customComparison.netFollowingGrowth}
                    </span>
                  </div>
                </div>

                {/* Quick list of unfollowers identified in this comparison */}
                {customComparison.unfollowers.length > 0 && (
                  <div className="pt-2">
                    <span className="text-xs font-semibold text-[#EF4444] block mb-2">
                      Accounts lost between {snapA.name} and {snapB.name}:
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {customComparison.unfollowers.slice(0, 10).map((u) => (
                        <a
                          key={u.username}
                          href={u.profileUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs px-2.5 py-1 rounded-lg bg-[#151B27] border border-[#EF4444]/30 text-[#F8FAFC] hover:text-[#EF4444] transition-colors inline-flex items-center space-x-1"
                        >
                          <span>@{u.username}</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      ))}
                      {customComparison.unfollowers.length > 10 && (
                        <span className="text-xs text-[#94A3B8] self-center">
                          +{customComparison.unfollowers.length - 10} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* All Snapshots Table */}
          <div className="bg-[#151B27] border border-[#252B38] rounded-2xl overflow-hidden shadow-xl">
            <div className="p-5 border-b border-[#252B38] flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-[#F8FAFC]">All Stored Snapshots</h3>
                <p className="text-xs text-[#94A3B8]">
                  {snapshots.length} total snapshots recorded in browser IndexedDB
                </p>
              </div>
              <button
                onClick={() => setCurrentPage('import')}
                className="px-3.5 py-1.5 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-xs font-semibold rounded-xl transition-colors"
              >
                + Add Snapshot
              </button>
            </div>

            <div className="divide-y divide-[#252B38]">
              {snapshots.map((snap) => {
                const isActive = activeSnapshot?.id === snap.id;

                return (
                  <div
                    key={snap.id}
                    className={`p-4 md:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 transition-colors ${
                      isActive ? 'bg-[#8B5CF6]/5' : 'hover:bg-[#1C2433]/40'
                    }`}
                  >
                    <div className="flex items-start space-x-3.5">
                      <div className="w-10 h-10 rounded-xl bg-[#10141D] border border-[#252B38] flex items-center justify-center font-bold text-xs text-[#8B5CF6] shrink-0 mt-0.5">
                        <Layers className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h4 className="text-sm font-bold text-[#F8FAFC]">{snap.name}</h4>
                          {isActive && (
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#22C55E]/15 text-[#22C55E]">
                              Active View
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-[#94A3B8] mt-0.5">
                          {new Date(snap.createdAt).toLocaleString()} • {snap.followersCount} followers •{' '}
                          {snap.followingCount} following
                        </p>
                        {snap.sourceFile && (
                          <span className="text-[11px] text-[#94A3B8] font-mono">
                            Source: {snap.sourceFile}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 self-end md:self-auto">
                      {!isActive && (
                        <button
                          onClick={() => setActiveSnapshotId(snap.id)}
                          className="px-3 py-1.5 rounded-xl bg-[#10141D] hover:bg-[#1C2433] text-xs font-medium text-[#F8FAFC] border border-[#252B38] transition-colors"
                        >
                          Make Active
                        </button>
                      )}

                      <button
                        onClick={() => setSnapshotToDelete(snap.id)}
                        className="p-1.5 rounded-xl text-[#94A3B8] hover:text-[#EF4444] hover:bg-[#10141D] transition-colors"
                        title="Delete snapshot"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={Boolean(snapshotToDelete)}
        title="Delete Snapshot?"
        message="Are you sure you want to delete this snapshot? Historical comparison data relying on this snapshot will be affected. This cannot be undone."
        confirmLabel="Delete"
        isDestructive={true}
        onCancel={() => setSnapshotToDelete(null)}
        onConfirm={async () => {
          if (snapshotToDelete) {
            await deleteSnapshot(snapshotToDelete);
            setSnapshotToDelete(null);
          }
        }}
      />
    </div>
  );
};
