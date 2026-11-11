import React from 'react';
import { useApp } from '../context/AppContext';
import { StatCard } from '../components/common/StatCard';
import {
  Users,
  UserCheck,
  UserMinus,
  UserX,
  Repeat,
  TrendingUp,
  AlertCircle,
  ExternalLink,
  ArrowRight,
  Clock,
  Layers,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const {
    comparison,
    activeSnapshot,
    previousSnapshot,
    snapshots,
    setCurrentPage,
  } = useApp();

  if (!activeSnapshot || !comparison) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16 space-y-4">
        <div className="w-16 h-16 rounded-3xl bg-[#8B5CF6]/15 text-[#8B5CF6] flex items-center justify-center mx-auto">
          <Layers className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-[#F8FAFC]">No Snapshots Yet</h2>
        <p className="text-sm text-[#94A3B8]">
          Upload your Instagram data export to view your follower analytics and track changes.
        </p>
        <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={() => setCurrentPage('import')}
            className="px-5 py-2.5 rounded-xl bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-xs font-semibold shadow-lg shadow-[#8B5CF6]/20 transition-all"
          >
            Import Instagram Export
          </button>
        </div>
      </div>
    );
  }

  // Distribution Data for Recharts
  const distributionData = [
    { name: 'Mutual Followers', value: comparison.mutuals.length, color: '#22C55E' },
    { name: 'Not Following Back', value: comparison.notFollowingBack.length, color: '#F59E0B' },
    { name: 'Your Fans', value: comparison.fans.length, color: '#6366F1' },
  ];

  // Snapshot overview bars
  const snapshotTimeline = snapshots.slice(0, 5).reverse().map((s) => ({
    name: s.name.length > 12 ? s.name.substring(0, 10) + '...' : s.name,
    Followers: s.followersCount,
    Following: s.followingCount,
  }));

  return (
    <div className="space-y-8 pb-12">
      {/* Snapshot Context Alert if only 1 snapshot exists */}
      {!comparison.hasPreviousSnapshot && (
        <div className="bg-[#151B27] border border-[#F59E0B]/30 rounded-2xl p-4 flex items-start space-x-3 text-xs">
          <AlertCircle className="w-5 h-5 text-[#F59E0B] shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-[#F8FAFC]">
              Single Snapshot Active: Baseline Established
            </p>
            <p className="text-[#94A3B8]">
              You have loaded 1 snapshot ({activeSnapshot.name}). Static metrics like{' '}
              <strong className="text-[#F8FAFC]">Not Following Back</strong> ({comparison.notFollowingBack.length}),{' '}
              <strong className="text-[#F8FAFC]">Mutuals</strong> ({comparison.mutuals.length}), and{' '}
              <strong className="text-[#F8FAFC]">Fans</strong> ({comparison.fans.length}) are fully calculated.
              To detect <strong className="text-[#EF4444]">Unfollowers</strong> and <strong className="text-[#22C55E]">New Followers</strong>, import a second snapshot in the future or compare with an earlier export.
            </p>
          </div>
        </div>
      )}

      {/* Snapshot Header Info */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#151B27] border border-[#252B38] rounded-2xl p-5">
        <div className="flex items-center space-x-3.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#8B5CF6] to-[#6366F1] flex items-center justify-center font-extrabold text-white text-base shadow-lg shadow-[#8B5CF6]/20">
            {activeSnapshot.name.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-[#F8FAFC]">{activeSnapshot.name}</h2>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#22C55E]/15 text-[#22C55E]">
                Active
              </span>
            </div>
            <p className="text-xs text-[#94A3B8] mt-0.5 flex items-center space-x-2">
              <Clock className="w-3.5 h-3.5 text-[#94A3B8]" />
              <span>Imported {new Date(activeSnapshot.createdAt).toLocaleString()}</span>
              {activeSnapshot.sourceFile && (
                <>
                  <span>•</span>
                  <span>{activeSnapshot.sourceFile}</span>
                </>
              )}
            </p>
          </div>
        </div>

        {comparison.hasPreviousSnapshot && previousSnapshot && (
          <div className="flex items-center space-x-3 bg-[#10141D] border border-[#252B38] rounded-xl px-3 py-2 text-xs">
            <span className="text-[#94A3B8]">Comparing with:</span>
            <span className="font-semibold text-[#8B5CF6]">{previousSnapshot.name}</span>
            <span className="text-[10px] text-[#94A3B8]">
              ({new Date(previousSnapshot.createdAt).toLocaleDateString()})
            </span>
          </div>
        )}
      </div>

      {/* 6 Core Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard
          title="Total Followers"
          value={activeSnapshot.followersCount}
          subtext="Followers in snapshot"
          icon={Users}
          colorScheme="primary"
          onClick={() => setCurrentPage('followers')}
        />

        <StatCard
          title="Total Following"
          value={activeSnapshot.followingCount}
          subtext="Accounts you follow"
          icon={UserCheck}
          colorScheme="secondary"
          onClick={() => setCurrentPage('following')}
        />

        <StatCard
          title="Unfollowers"
          value={comparison.hasPreviousSnapshot ? comparison.unfollowers.length : '--'}
          subtext={comparison.hasPreviousSnapshot ? 'Left since last snapshot' : 'Requires 2 snapshots'}
          icon={UserMinus}
          colorScheme="danger"
          badge={
            comparison.hasPreviousSnapshot && comparison.unfollowers.length > 0
              ? { text: `-${comparison.unfollowers.length}`, variant: 'negative' }
              : undefined
          }
          onClick={() => setCurrentPage('unfollowers')}
        />

        <StatCard
          title="New Followers"
          value={comparison.hasPreviousSnapshot ? comparison.newFollowers.length : '--'}
          subtext={comparison.hasPreviousSnapshot ? 'Gained since last snapshot' : 'Requires 2 snapshots'}
          icon={TrendingUp}
          colorScheme="success"
          badge={
            comparison.hasPreviousSnapshot && comparison.newFollowers.length > 0
              ? { text: `+${comparison.newFollowers.length}`, variant: 'positive' }
              : undefined
          }
          onClick={() => setCurrentPage('analytics')}
        />

        <StatCard
          title="Not Following Back"
          value={comparison.notFollowingBack.length}
          subtext="You follow, they don't"
          icon={UserX}
          colorScheme="warning"
          onClick={() => setCurrentPage('not-following-back')}
        />

        <StatCard
          title="Mutual Followers"
          value={comparison.mutuals.length}
          subtext="Both follow each other"
          icon={Repeat}
          colorScheme="success"
          onClick={() => setCurrentPage('mutuals')}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Relationship Distribution Pie Chart */}
        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-[#F8FAFC]">Relationship Distribution</h3>
              <span className="text-[11px] text-[#94A3B8]">Current Snapshot</span>
            </div>

            <div className="h-48 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={distributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {distributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#10141D',
                      borderColor: '#252B38',
                      borderRadius: '12px',
                      color: '#F8FAFC',
                      fontSize: '12px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-4 border-t border-[#252B38] text-center text-xs">
            <div>
              <div className="flex items-center justify-center space-x-1.5 mb-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#22C55E]"></span>
                <span className="text-[#94A3B8] text-[10px]">Mutuals</span>
              </div>
              <span className="font-bold text-[#F8FAFC]">{comparison.mutuals.length}</span>
            </div>
            <div>
              <div className="flex items-center justify-center space-x-1.5 mb-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]"></span>
                <span className="text-[#94A3B8] text-[10px]">Not Back</span>
              </div>
              <span className="font-bold text-[#F8FAFC]">{comparison.notFollowingBack.length}</span>
            </div>
            <div>
              <div className="flex items-center justify-center space-x-1.5 mb-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#6366F1]"></span>
                <span className="text-[#94A3B8] text-[10px]">Fans</span>
              </div>
              <span className="font-bold text-[#F8FAFC]">{comparison.fans.length}</span>
            </div>
          </div>
        </div>

        {/* Snapshot Timeline Bar Chart */}
        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5 shadow-xl lg:col-span-2 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-[#F8FAFC]">Snapshots Growth Trend</h3>
              <p className="text-[11px] text-[#94A3B8]">Followers vs Following over recorded snapshots</p>
            </div>
            <button
              onClick={() => setCurrentPage('history')}
              className="text-xs text-[#8B5CF6] hover:underline flex items-center space-x-1"
            >
              <span>View History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={snapshotTimeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#252B38" />
                <XAxis dataKey="name" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#10141D',
                    borderColor: '#252B38',
                    borderRadius: '12px',
                    color: '#F8FAFC',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="Followers" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Following" fill="#6366F1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-center space-x-6 pt-3 text-xs text-[#94A3B8]">
            <span className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-sm bg-[#8B5CF6]"></span>
              <span>Followers</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-sm bg-[#6366F1]"></span>
              <span>Following</span>
            </span>
          </div>
        </div>
      </div>

      {/* Previews: Unfollowers & Not Following Back */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Unfollowers Preview */}
        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <UserMinus className="w-4 h-4 text-[#EF4444]" />
                <h3 className="text-sm font-bold text-[#F8FAFC]">Recent Unfollowers</h3>
              </div>
              <button
                onClick={() => setCurrentPage('unfollowers')}
                className="text-xs text-[#8B5CF6] hover:underline"
              >
                View all ({comparison.unfollowers.length})
              </button>
            </div>

            {comparison.unfollowers.length === 0 ? (
              <div className="py-8 text-center text-xs text-[#94A3B8]">
                {comparison.hasPreviousSnapshot
                  ? 'No unfollowers detected between these snapshots! 🎉'
                  : 'Import another snapshot in the future to detect when someone unfollows you.'}
              </div>
            ) : (
              <div className="space-y-2">
                {comparison.unfollowers.slice(0, 5).map((user) => (
                  <div
                    key={user.username}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-[#10141D] border border-[#252B38]"
                  >
                    <div className="flex items-center space-x-2.5">
                      <div className="w-7 h-7 rounded-full bg-[#EF4444]/15 text-[#EF4444] flex items-center justify-center font-bold text-xs">
                        {user.username.substring(0, 1).toUpperCase()}
                      </div>
                      <span className="text-xs font-semibold text-[#F8FAFC]">
                        @{user.originalUsername || user.username}
                      </span>
                    </div>

                    <a
                      href={user.profileUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-[#8B5CF6] hover:underline flex items-center space-x-1"
                    >
                      <span>Profile</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>

          {comparison.unfollowers.length > 5 && (
            <button
              onClick={() => setCurrentPage('unfollowers')}
              className="mt-4 w-full py-2 bg-[#10141D] hover:bg-[#1C2433] rounded-xl text-xs font-medium text-[#F8FAFC] border border-[#252B38] transition-colors"
            >
              See all {comparison.unfollowers.length} unfollowers &rarr;
            </button>
          )}
        </div>

        {/* Not Following Back Preview */}
        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <UserX className="w-4 h-4 text-[#F59E0B]" />
                <h3 className="text-sm font-bold text-[#F8FAFC]">Not Following You Back</h3>
              </div>
              <button
                onClick={() => setCurrentPage('not-following-back')}
                className="text-xs text-[#8B5CF6] hover:underline"
              >
                View all ({comparison.notFollowingBack.length})
              </button>
            </div>

            {comparison.notFollowingBack.length === 0 ? (
              <div className="py-8 text-center text-xs text-[#94A3B8]">
                Everyone you follow is following you back!
              </div>
            ) : (
              <div className="space-y-2">
                {comparison.notFollowingBack.slice(0, 5).map((user) => (
                  <div
                    key={user.username}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-[#10141D] border border-[#252B38]"
                  >
                    <div className="flex items-center space-x-2.5">
                      <div className="w-7 h-7 rounded-full bg-[#F59E0B]/15 text-[#F59E0B] flex items-center justify-center font-bold text-xs">
                        {user.username.substring(0, 1).toUpperCase()}
                      </div>
                      <span className="text-xs font-semibold text-[#F8FAFC]">
                        @{user.originalUsername || user.username}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <a
                        href={user.profileUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-[#8B5CF6] hover:underline flex items-center space-x-1"
                      >
                        <span>Profile</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-4 flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage('smart-unfollow')}
              className="flex-1 py-2 bg-[#8B5CF6] hover:bg-[#7C3AED] rounded-xl text-xs font-semibold text-white shadow-md shadow-[#8B5CF6]/20 transition-all text-center"
            >
              Open Smart Unfollow Manager
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
