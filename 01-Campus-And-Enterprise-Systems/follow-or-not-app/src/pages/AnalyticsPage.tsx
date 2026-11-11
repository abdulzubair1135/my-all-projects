import React from 'react';
import { useApp } from '../context/AppContext';
import {
  Repeat,
  Heart,
  UserX,
  Users,
  Activity,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export const AnalyticsPage: React.FC = () => {
  const { snapshots, activeSnapshot, comparison, setCurrentPage } = useApp();

  if (!activeSnapshot || !comparison) {
    return (
      <div className="text-center py-16 space-y-4">
        <Activity className="w-12 h-12 text-[#94A3B8] mx-auto" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">No Analytics Available</h3>
        <p className="text-xs text-[#94A3B8]">Import your Instagram data to generate follower growth analytics.</p>
        <button
          onClick={() => setCurrentPage('import')}
          className="px-4 py-2 bg-[#8B5CF6] text-white text-xs font-semibold rounded-xl"
        >
          Import Data
        </button>
      </div>
    );
  }

  // Calculate Key Rates
  const followerCount = activeSnapshot.followersCount || 1;
  const followingCount = activeSnapshot.followingCount || 1;

  // Reciprocity Rate: % of accounts you follow that follow you back
  const reciprocityRate = ((comparison.mutuals.length / followingCount) * 100).toFixed(1);

  // Audience Retention: % of your followers who are mutuals
  const mutualAudienceRate = ((comparison.mutuals.length / followerCount) * 100).toFixed(1);

  // Fan Ratio: % of your followers whom you don't follow back
  const fanRatio = ((comparison.fans.length / followerCount) * 100).toFixed(1);

  // Growth Trend Data across all snapshots
  const growthData = [...snapshots].reverse().map((s) => ({
    name: new Date(s.createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    Followers: s.followersCount,
    Following: s.followingCount,
    SnapshotName: s.name,
  }));

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-extrabold text-[#F8FAFC]">Follower Growth & Analytics</h2>
        <p className="text-sm text-[#94A3B8] mt-1">
          Deep behavioral metrics, audience reciprocity, and historical growth velocity.
        </p>
      </div>

      {/* Analytics Ratios */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
              Reciprocity Rate
            </span>
            <Repeat className="w-4 h-4 text-[#22C55E]" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-[#F8FAFC]">{reciprocityRate}%</span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-2">
            Of the people you follow, {reciprocityRate}% follow you back.
          </p>
        </div>

        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
              Audience Retention
            </span>
            <Users className="w-4 h-4 text-[#8B5CF6]" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-[#F8FAFC]">{mutualAudienceRate}%</span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-2">
            {mutualAudienceRate}% of your follower base are mutual connections.
          </p>
        </div>

        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
              Fan Audience Share
            </span>
            <Heart className="w-4 h-4 text-[#6366F1]" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-[#F8FAFC]">{fanRatio}%</span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-2">
            {comparison.fans.length} fans follow your content without you following back.
          </p>
        </div>

        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
              Unreturned Follow Ratio
            </span>
            <UserX className="w-4 h-4 text-[#F59E0B]" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-[#F8FAFC]">
              {(((comparison.notFollowingBack.length) / followingCount) * 100).toFixed(1)}%
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-2">
            {comparison.notFollowingBack.length} of your follows are one-directional.
          </p>
        </div>
      </div>

      {/* Main Area Chart: Follower and Following Evolution */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-base font-bold text-[#F8FAFC]">Account Trajectory</h3>
            <p className="text-xs text-[#94A3B8]">
              Follower and following curves tracked over successive snapshots
            </p>
          </div>
          <span className="text-xs text-[#8B5CF6] font-medium bg-[#10141D] px-3 py-1 rounded-full border border-[#252B38] self-start sm:self-auto">
            {snapshots.length} Data Points
          </span>
        </div>

        <div className="h-72 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={growthData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorFollowers" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="colorFollowing" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#252B38" />
              <XAxis dataKey="name" stroke="#94A3B8" fontSize={12} tickLine={false} />
              <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#10141D',
                  borderColor: '#252B38',
                  borderRadius: '12px',
                  color: '#F8FAFC',
                  fontSize: '12px',
                }}
              />
              <Area
                type="monotone"
                dataKey="Followers"
                stroke="#8B5CF6"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorFollowers)"
              />
              <Area
                type="monotone"
                dataKey="Following"
                stroke="#6366F1"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorFollowing)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-center space-x-6 text-xs text-[#94A3B8] pt-2">
          <span className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-[#8B5CF6]"></span>
            <span>Followers</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-[#6366F1]"></span>
            <span>Following</span>
          </span>
        </div>
      </div>
    </div>
  );
};
