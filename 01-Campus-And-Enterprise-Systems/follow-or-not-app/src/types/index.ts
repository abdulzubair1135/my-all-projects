export interface InstagramUser {
  username: string; // Normalized lowercase
  originalUsername: string; // Preserved casing
  profileUrl: string;
  timestamp?: number; // Unix timestamp in seconds or ms
  detectionDate?: number; // When first detected in followtrack
  isVerified?: boolean;
}

export interface Snapshot {
  id: string;
  name: string;
  createdAt: number; // Unix timestamp ms
  followers: InstagramUser[];
  following: InstagramUser[];
  followersCount: number;
  followingCount: number;
  sourceFile?: string;
  notes?: string;
}

export interface ComparisonResult {
  currentSnapshot: Snapshot;
  previousSnapshot?: Snapshot;
  unfollowers: InstagramUser[]; // In prev followers, not in current followers
  newFollowers: InstagramUser[]; // In current followers, not in prev followers
  notFollowingBack: InstagramUser[]; // In current following, not in current followers
  fans: InstagramUser[]; // In current followers, not in current following
  mutuals: InstagramUser[]; // Intersection of current followers & following
  newFollowing: InstagramUser[]; // In current following, not in prev following
  removedFollowing: InstagramUser[]; // In prev following, not in current following
  netFollowerGrowth: number;
  netFollowingGrowth: number;
  hasPreviousSnapshot: boolean;
}

export interface ManualUnfollowRecord {
  username: string;
  timestamp: number;
  status: 'unfollowed' | 'skipped' | 'whitelist';
  notes?: string;
}

export type ImportStep =
  | 'idle'
  | 'validating'
  | 'extracting'
  | 'scanning'
  | 'parsing_followers'
  | 'parsing_following'
  | 'deduplicating'
  | 'creating_snapshot'
  | 'completed'
  | 'error';

export interface ImportProgress {
  step: ImportStep;
  progress: number; // 0 - 100
  title: string;
  description: string;
  details?: {
    followersFound: number;
    followingFound: number;
    filesFound: string[];
  };
  error?: string;
}

export interface AppSettings {
  theme: 'dark' | 'light';
  autoComparePrevious: boolean;
  exportDateFormat: 'ISO' | 'local';
  confirmUnfollowActions: boolean;
}

export type PageView =
  | 'landing'
  | 'dashboard'
  | 'import'
  | 'followers'
  | 'following'
  | 'unfollowers'
  | 'not-following-back'
  | 'fans'
  | 'mutuals'
  | 'history'
  | 'analytics'
  | 'smart-unfollow'
  | 'reports'
  | 'settings'
  | 'privacy';
