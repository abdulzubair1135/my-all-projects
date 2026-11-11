import type { Snapshot, ComparisonResult, InstagramUser } from '../types';

export class FollowerComparisonService {
  /**
   * Compare a current snapshot with an optional previous snapshot.
   * Uses high-performance Set-based lookups with normalized usernames.
   */
  static compare(currentSnapshot: Snapshot, previousSnapshot?: Snapshot): ComparisonResult {
    // Current sets
    const currentFollowersSet = new Set(currentSnapshot.followers.map((u) => u.username));
    const currentFollowingSet = new Set(currentSnapshot.following.map((u) => u.username));

    // C. Not Following Back: Current Following - Current Followers
    const notFollowingBack: InstagramUser[] = [];
    for (const user of currentSnapshot.following) {
      if (!currentFollowersSet.has(user.username)) {
        notFollowingBack.push(user);
      }
    }

    // D. Fans: Current Followers - Current Following
    const fans: InstagramUser[] = [];
    for (const user of currentSnapshot.followers) {
      if (!currentFollowingSet.has(user.username)) {
        fans.push(user);
      }
    }

    // E. Mutual Followers: Current Followers INTERSECTION Current Following
    const mutuals: InstagramUser[] = [];
    for (const user of currentSnapshot.followers) {
      if (currentFollowingSet.has(user.username)) {
        mutuals.push(user);
      }
    }

    // Previous comparison
    const unfollowers: InstagramUser[] = [];
    const newFollowers: InstagramUser[] = [];
    const newFollowing: InstagramUser[] = [];
    const removedFollowing: InstagramUser[] = [];

    if (previousSnapshot) {
      const prevFollowersSet = new Set(previousSnapshot.followers.map((u) => u.username));
      const prevFollowingSet = new Set(previousSnapshot.following.map((u) => u.username));

      // A. Unfollowers: Previous Followers - Current Followers
      for (const prevUser of previousSnapshot.followers) {
        if (!currentFollowersSet.has(prevUser.username)) {
          unfollowers.push({
            ...prevUser,
            detectionDate: currentSnapshot.createdAt,
          });
        }
      }

      // B. New Followers: Current Followers - Previous Followers
      for (const currUser of currentSnapshot.followers) {
        if (!prevFollowersSet.has(currUser.username)) {
          newFollowers.push({
            ...currUser,
            detectionDate: currentSnapshot.createdAt,
          });
        }
      }

      // F. New Following: Current Following - Previous Following
      for (const currUser of currentSnapshot.following) {
        if (!prevFollowingSet.has(currUser.username)) {
          newFollowing.push(currUser);
        }
      }

      // G. Removed Following: Previous Following - Current Following
      for (const prevUser of previousSnapshot.following) {
        if (!currentFollowingSet.has(prevUser.username)) {
          removedFollowing.push(prevUser);
        }
      }
    }

    const netFollowerGrowth = previousSnapshot
      ? currentSnapshot.followersCount - previousSnapshot.followersCount
      : 0;

    const netFollowingGrowth = previousSnapshot
      ? currentSnapshot.followingCount - previousSnapshot.followingCount
      : 0;

    return {
      currentSnapshot,
      previousSnapshot,
      unfollowers,
      newFollowers,
      notFollowingBack,
      fans,
      mutuals,
      newFollowing,
      removedFollowing,
      netFollowerGrowth,
      netFollowingGrowth,
      hasPreviousSnapshot: Boolean(previousSnapshot),
    };
  }

  /**
   * Compare any two arbitrary snapshots (Snapshot A -> Snapshot B)
   */
  static compareTwoSnapshots(baseSnapshot: Snapshot, targetSnapshot: Snapshot): ComparisonResult {
    // Base is treated as earlier, Target as newer
    return this.compare(targetSnapshot, baseSnapshot);
  }
}
