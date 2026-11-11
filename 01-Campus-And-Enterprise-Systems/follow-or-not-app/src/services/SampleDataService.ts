import type { Snapshot, InstagramUser } from '../types';

export class SampleDataService {
  static getSampleSnapshots(): { snapshot1: Snapshot; snapshot2: Snapshot } {
    const twoWeeksAgo = Date.now() - 14 * 24 * 60 * 60 * 1000;
    const now = Date.now();

    // Base mutuals
    const mutualUsers: InstagramUser[] = [
      { username: 'sarah.designs', originalUsername: 'Sarah.Designs', profileUrl: 'https://www.instagram.com/sarah.designs/', timestamp: twoWeeksAgo - 30 * 86400000 },
      { username: 'alex_tech', originalUsername: 'Alex_Tech', profileUrl: 'https://www.instagram.com/alex_tech/', timestamp: twoWeeksAgo - 45 * 86400000 },
      { username: 'marcus_travels', originalUsername: 'Marcus_Travels', profileUrl: 'https://www.instagram.com/marcus_travels/', timestamp: twoWeeksAgo - 20 * 86400000 },
      { username: 'elena_lens', originalUsername: 'Elena_Lens', profileUrl: 'https://www.instagram.com/elena_lens/', timestamp: twoWeeksAgo - 60 * 86400000 },
      { username: 'david_crypto', originalUsername: 'David_Crypto', profileUrl: 'https://www.instagram.com/david_crypto/', timestamp: twoWeeksAgo - 15 * 86400000 },
      { username: 'clara_style', originalUsername: 'Clara_Style', profileUrl: 'https://www.instagram.com/clara_style/', timestamp: twoWeeksAgo - 10 * 86400000 },
      { username: 'pixel_artisan', originalUsername: 'Pixel_Artisan', profileUrl: 'https://www.instagram.com/pixel_artisan/', timestamp: twoWeeksAgo - 80 * 86400000 },
      { username: 'studio_koto', originalUsername: 'Studio_Koto', profileUrl: 'https://www.instagram.com/studio_koto/', timestamp: twoWeeksAgo - 25 * 86400000 },
      { username: 'nature.wanderer', originalUsername: 'Nature.Wanderer', profileUrl: 'https://www.instagram.com/nature.wanderer/', timestamp: twoWeeksAgo - 90 * 86400000 },
      { username: 'daily_coffee_roast', originalUsername: 'Daily_Coffee_Roast', profileUrl: 'https://www.instagram.com/daily_coffee_roast/', timestamp: twoWeeksAgo - 5 * 86400000 },
    ];

    // Accounts YOU follow who DO NOT follow you back
    const notFollowingBackUsers: InstagramUser[] = [
      { username: 'natgeo', originalUsername: 'NatGeo', profileUrl: 'https://www.instagram.com/natgeo/', timestamp: twoWeeksAgo - 120 * 86400000, isVerified: true },
      { username: 'verge', originalUsername: 'Verge', profileUrl: 'https://www.instagram.com/verge/', timestamp: twoWeeksAgo - 100 * 86400000, isVerified: true },
      { username: 'wired', originalUsername: 'WIRED', profileUrl: 'https://www.instagram.com/wired/', timestamp: twoWeeksAgo - 95 * 86400000, isVerified: true },
      { username: 'ghost_agency_co', originalUsername: 'ghost_agency_co', profileUrl: 'https://www.instagram.com/ghost_agency_co/', timestamp: twoWeeksAgo - 40 * 86400000 },
      { username: 'hypebeast_drop', originalUsername: 'Hypebeast_Drop', profileUrl: 'https://www.instagram.com/hypebeast_drop/', timestamp: twoWeeksAgo - 30 * 86400000 },
      { username: 'crypto_whale_tracker', originalUsername: 'crypto_whale_tracker', profileUrl: 'https://www.instagram.com/crypto_whale_tracker/', timestamp: twoWeeksAgo - 18 * 86400000 },
      { username: 'silicon_valley_insider', originalUsername: 'silicon_valley_insider', profileUrl: 'https://www.instagram.com/silicon_valley_insider/', timestamp: twoWeeksAgo - 65 * 86400000 },
      { username: 'minimal_architecture', originalUsername: 'minimal_architecture', profileUrl: 'https://www.instagram.com/minimal_architecture/', timestamp: twoWeeksAgo - 50 * 86400000 },
    ];

    // Accounts that follow you, but YOU don't follow back (Fans)
    const fanUsers: InstagramUser[] = [
      { username: 'johnny_runner', originalUsername: 'Johnny_Runner', profileUrl: 'https://www.instagram.com/johnny_runner/', timestamp: twoWeeksAgo - 12 * 86400000 },
      { username: 'amanda_reads', originalUsername: 'Amanda_Reads', profileUrl: 'https://www.instagram.com/amanda_reads/', timestamp: twoWeeksAgo - 40 * 86400000 },
      { username: 'baking_with_zoe', originalUsername: 'Baking_With_Zoe', profileUrl: 'https://www.instagram.com/baking_with_zoe/', timestamp: twoWeeksAgo - 22 * 86400000 },
      { username: 'urban_skater_88', originalUsername: 'Urban_Skater_88', profileUrl: 'https://www.instagram.com/urban_skater_88/', timestamp: twoWeeksAgo - 55 * 86400000 },
      { username: 'synthwave_beats', originalUsername: 'Synthwave_Beats', profileUrl: 'https://www.instagram.com/synthwave_beats/', timestamp: twoWeeksAgo - 33 * 86400000 },
      { username: 'pottery_vibes', originalUsername: 'Pottery_Vibes', profileUrl: 'https://www.instagram.com/pottery_vibes/', timestamp: twoWeeksAgo - 14 * 86400000 },
    ];

    // Unfollowers: Were in Snapshot 1, removed in Snapshot 2
    const unfollowerUsers: InstagramUser[] = [
      { username: 'daniel_drops', originalUsername: 'Daniel_Drops', profileUrl: 'https://www.instagram.com/daniel_drops/', timestamp: twoWeeksAgo - 40 * 86400000 },
      { username: 'mia_fitness_coach', originalUsername: 'Mia_Fitness_Coach', profileUrl: 'https://www.instagram.com/mia_fitness_coach/', timestamp: twoWeeksAgo - 25 * 86400000 },
      { username: 'vintage_collector_uk', originalUsername: 'vintage_collector_uk', profileUrl: 'https://www.instagram.com/vintage_collector_uk/', timestamp: twoWeeksAgo - 60 * 86400000 },
      { username: 'tokyo_nights_life', originalUsername: 'Tokyo_Nights_Life', profileUrl: 'https://www.instagram.com/tokyo_nights_life/', timestamp: twoWeeksAgo - 15 * 86400000 },
    ];

    // New Followers: Not in Snapshot 1, added in Snapshot 2
    const newFollowerUsers: InstagramUser[] = [
      { username: 'julian_cinema', originalUsername: 'Julian_Cinema', profileUrl: 'https://www.instagram.com/julian_cinema/', timestamp: now - 3 * 86400000 },
      { username: 'sam_react_dev', originalUsername: 'Sam_React_Dev', profileUrl: 'https://www.instagram.com/sam_react_dev/', timestamp: now - 5 * 86400000 },
      { username: 'cozy_nordic_home', originalUsername: 'Cozy_Nordic_Home', profileUrl: 'https://www.instagram.com/cozy_nordic_home/', timestamp: now - 8 * 86400000 },
      { username: 'f1_fanatic_hub', originalUsername: 'F1_Fanatic_Hub', profileUrl: 'https://www.instagram.com/f1_fanatic_hub/', timestamp: now - 2 * 86400000 },
      { username: 'nora_illustrates', originalUsername: 'Nora_Illustrates', profileUrl: 'https://www.instagram.com/nora_illustrates/', timestamp: now - 1 * 86400000 },
    ];

    // SNAPSHOT 1 (2 weeks ago)
    const snap1Followers = [...mutualUsers, ...fanUsers, ...unfollowerUsers];
    const snap1Following = [...mutualUsers, ...notFollowingBackUsers];

    const snapshot1: Snapshot = {
      id: 'demo-snapshot-oct-15',
      name: 'Instagram Export (Oct 15)',
      createdAt: twoWeeksAgo,
      followers: snap1Followers,
      following: snap1Following,
      followersCount: snap1Followers.length,
      followingCount: snap1Following.length,
      sourceFile: 'instagram_export_oct15.zip',
      notes: 'Initial baseline export',
    };

    // SNAPSHOT 2 (Today)
    // Removed unfollowerUsers, Added newFollowerUsers
    const snap2Followers = [...mutualUsers, ...fanUsers, ...newFollowerUsers];
    const snap2Following = [...mutualUsers, ...notFollowingBackUsers];

    const snapshot2: Snapshot = {
      id: 'demo-snapshot-oct-31',
      name: 'Instagram Export (Current)',
      createdAt: now,
      followers: snap2Followers,
      following: snap2Following,
      followersCount: snap2Followers.length,
      followingCount: snap2Following.length,
      sourceFile: 'instagram_export_current.zip',
      notes: 'Recent bi-weekly comparison export',
    };

    return { snapshot1, snapshot2 };
  }
}
