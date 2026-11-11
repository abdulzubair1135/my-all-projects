import { describe, it, expect } from 'vitest';
import { FollowerComparisonService } from '../services/FollowerComparisonService';
import type { Snapshot, InstagramUser } from '../types';

const createUser = (username: string): InstagramUser => ({
  username: username.toLowerCase(),
  originalUsername: username,
  profileUrl: `https://www.instagram.com/${username.toLowerCase()}/`,
});

describe('FollowerComparisonService', () => {
  it('correctly calculates notFollowingBack, fans, and mutuals for a single snapshot', () => {
    // Current snapshot:
    // Followers: alice, bob, charlie
    // Following: bob, charlie, david, emma
    const currentSnapshot: Snapshot = {
      id: 'snap-1',
      name: 'Snapshot 1',
      createdAt: 1000,
      followers: [createUser('alice'), createUser('bob'), createUser('charlie')],
      following: [createUser('bob'), createUser('charlie'), createUser('david'), createUser('emma')],
      followersCount: 3,
      followingCount: 4,
    };

    const result = FollowerComparisonService.compare(currentSnapshot);

    // Mutuals: bob, charlie
    expect(result.mutuals.map((u) => u.username).sort()).toEqual(['bob', 'charlie']);

    // Not following back: david, emma
    expect(result.notFollowingBack.map((u) => u.username).sort()).toEqual(['david', 'emma']);

    // Fans: alice
    expect(result.fans.map((u) => u.username)).toEqual(['alice']);

    // Since no previous snapshot, hasPreviousSnapshot is false
    expect(result.hasPreviousSnapshot).toBe(false);
    expect(result.unfollowers).toHaveLength(0);
    expect(result.newFollowers).toHaveLength(0);
  });

  it('accurately identifies unfollowers and new followers when comparing two snapshots', () => {
    // Previous Snapshot:
    // Followers: user1, user2, user3 (user3 will unfollow)
    // Following: user1, userA
    const previousSnapshot: Snapshot = {
      id: 'snap-prev',
      name: 'Previous Snapshot',
      createdAt: 1000,
      followers: [createUser('user1'), createUser('user2'), createUser('user3')],
      following: [createUser('user1'), createUser('userA')],
      followersCount: 3,
      followingCount: 2,
    };

    // Current Snapshot:
    // Followers: user1, user2, user4 (user4 is new, user3 is gone)
    // Following: user1, userB (userA unfollowed by me, userB newly followed)
    const currentSnapshot: Snapshot = {
      id: 'snap-curr',
      name: 'Current Snapshot',
      createdAt: 2000,
      followers: [createUser('user1'), createUser('user2'), createUser('user4')],
      following: [createUser('user1'), createUser('userB')],
      followersCount: 3,
      followingCount: 2,
    };

    const result = FollowerComparisonService.compare(currentSnapshot, previousSnapshot);

    expect(result.hasPreviousSnapshot).toBe(true);

    // Unfollowers: Previous Followers - Current Followers = user3
    expect(result.unfollowers.map((u) => u.username)).toEqual(['user3']);

    // New Followers: Current Followers - Previous Followers = user4
    expect(result.newFollowers.map((u) => u.username)).toEqual(['user4']);

    // Removed Following: Previous Following - Current Following = userA
    expect(result.removedFollowing.map((u) => u.username)).toEqual(['usera']);

    // New Following: Current Following - Previous Following = userB
    expect(result.newFollowing.map((u) => u.username)).toEqual(['userb']);

    // Net growth
    expect(result.netFollowerGrowth).toBe(0);
  });

  it('compares two arbitrary snapshots regardless of order via compareTwoSnapshots', () => {
    const snapA: Snapshot = {
      id: 'a',
      name: 'A',
      createdAt: 100,
      followers: [createUser('u1'), createUser('u2')],
      following: [],
      followersCount: 2,
      followingCount: 0,
    };

    const snapB: Snapshot = {
      id: 'b',
      name: 'B',
      createdAt: 200,
      followers: [createUser('u1'), createUser('u3'), createUser('u4')],
      following: [],
      followersCount: 3,
      followingCount: 0,
    };

    const comparison = FollowerComparisonService.compareTwoSnapshots(snapA, snapB);
    expect(comparison.newFollowers.map((u) => u.username).sort()).toEqual(['u3', 'u4']);
    expect(comparison.unfollowers.map((u) => u.username)).toEqual(['u2']);
    expect(comparison.netFollowerGrowth).toBe(1);
  });
});
