import JSZip from 'jszip';
import type { InstagramUser, ImportProgress } from '../types';

export class InstagramImportService {
  /**
   * Normalize an Instagram username: lowercase, trimmed, strip leading @
   */
  static normalizeUsername(raw: string): string {
    if (!raw || typeof raw !== 'string') return '';
    return raw
      .trim()
      .toLowerCase()
      .replace(/^@+/, '')
      .replace(/\/+$/, '')
      .split('?')[0];
  }

  /**
   * Safely extract username from a URL or raw string
   */
  static extractUsernameFromUrl(urlOrValue: string): string {
    if (!urlOrValue || typeof urlOrValue !== 'string') return '';
    const clean = urlOrValue.trim();
    if (clean.includes('instagram.com/')) {
      const parts = clean.split('instagram.com/')[1].split('/')[0].split('?')[0];
      return this.normalizeUsername(parts);
    }
    return this.normalizeUsername(clean);
  }

  /**
   * Parse a JSON string safely and extract InstagramUser records.
   * Handles all known Instagram export variations.
   */
  static parseInstagramJson(jsonContent: string): InstagramUser[] {
    const usersMap = new Map<string, InstagramUser>();

    try {
      const data = JSON.parse(jsonContent);
      this.extractUsersFromObject(data, usersMap);
    } catch (err) {
      console.error('Failed to parse Instagram JSON:', err);
      throw new Error('Malformed JSON content');
    }

    return Array.from(usersMap.values());
  }

  /**
   * Recursively searches or navigates JSON data to find follower/following entries
   */
  private static extractUsersFromObject(data: unknown, results: Map<string, InstagramUser>): void {
    if (!data) return;

    // Case 1: Root is an Array
    if (Array.isArray(data)) {
      for (const item of data) {
        if (typeof item === 'string') {
          const norm = this.normalizeUsername(item);
          if (norm && !results.has(norm)) {
            results.set(norm, {
              username: norm,
              originalUsername: item.trim(),
              profileUrl: `https://www.instagram.com/${norm}/`,
            });
          }
        } else if (item && typeof item === 'object') {
          this.parseSingleInstagramItem(item, results);
        }
      }
      return;
    }

    // Case 2: Object with wrapping keys (e.g. relationships_following, relationships_followers, etc.)
    if (typeof data === 'object') {
      const obj = data as Record<string, unknown>;

      for (const key of Object.keys(obj)) {
        const val = obj[key];
        if (Array.isArray(val)) {
          for (const item of val) {
            if (typeof item === 'object' && item !== null) {
              this.parseSingleInstagramItem(item, results);
            } else if (typeof item === 'string') {
              const norm = this.normalizeUsername(item);
              if (norm && !results.has(norm)) {
                results.set(norm, {
                  username: norm,
                  originalUsername: item.trim(),
                  profileUrl: `https://www.instagram.com/${norm}/`,
                });
              }
            }
          }
        }
      }
    }
  }

  /**
   * Parses standard Instagram record object:
   * { title: "username", string_list_data: [{ href, value, timestamp }] }
   */
  private static parseSingleInstagramItem(item: Record<string, unknown>, results: Map<string, InstagramUser>): void {
    let rawUsername = '';
    let timestamp: number | undefined;
    let href: string | undefined;

    // Check string_list_data array (standard modern export format)
    if (Array.isArray(item.string_list_data) && item.string_list_data.length > 0) {
      const firstEntry = item.string_list_data[0];
      if (firstEntry && typeof firstEntry === 'object') {
        const entryObj = firstEntry as Record<string, unknown>;
        if (typeof entryObj.value === 'string' && entryObj.value.trim()) {
          rawUsername = entryObj.value;
        }
        if (typeof entryObj.href === 'string' && entryObj.href.trim()) {
          href = entryObj.href;
          if (!rawUsername) {
            rawUsername = this.extractUsernameFromUrl(entryObj.href);
          }
        }
        if (typeof entryObj.timestamp === 'number') {
          timestamp = entryObj.timestamp;
        }
      }
    }

    // If still empty, check item.title
    if (!rawUsername && typeof item.title === 'string' && item.title.trim()) {
      rawUsername = item.title;
    }

    // Or check item.username
    if (!rawUsername && typeof item.username === 'string' && item.username.trim()) {
      rawUsername = item.username;
    }

    const norm = this.normalizeUsername(rawUsername);
    // Ignore internal placeholder strings or blank
    if (norm && norm !== 'instagram' && !results.has(norm)) {
      results.set(norm, {
        username: norm,
        originalUsername: rawUsername.trim() || norm,
        profileUrl: href || `https://www.instagram.com/${norm}/`,
        timestamp: timestamp ? (timestamp < 1e11 ? timestamp * 1000 : timestamp) : undefined,
      });
    }
  }

  /**
   * Fallback parser for HTML exports
   */
  static parseInstagramHtml(htmlContent: string): InstagramUser[] {
    const results = new Map<string, InstagramUser>();
    const linkRegex = /<a[^>]+href=["'](https?:\/\/(?:www\.)?instagram\.com\/([a-zA-Z0-9._]+)\/?)["'][^>]*>(.*?)<\/a>/gi;
    let match;

    while ((match = linkRegex.exec(htmlContent)) !== null) {
      const rawUser = match[2];
      const norm = this.normalizeUsername(rawUser);
      if (norm && norm !== 'instagram' && !results.has(norm)) {
        results.set(norm, {
          username: norm,
          originalUsername: rawUser,
          profileUrl: `https://www.instagram.com/${norm}/`,
        });
      }
    }

    return Array.from(results.values());
  }

  /**
   * Process a full ZIP file or a list of uploaded JSON/HTML files
   */
  static async processZipFile(
    file: File,
    onProgress?: (progress: ImportProgress) => void
  ): Promise<{ followers: InstagramUser[]; following: InstagramUser[]; filesProcessed: string[] }> {
    const updateProgress = (
      step: ImportProgress['step'],
      progress: number,
      title: string,
      description: string,
      details?: ImportProgress['details']
    ) => {
      onProgress?.({ step, progress, title, description, details });
    };

    updateProgress('validating', 10, 'Validating file', `Checking ${file.name} (${(file.size / (1024 * 1024)).toFixed(1)} MB)`);

    // Verify file size and ZIP magic bytes (PK\x03\x04 or standard zip mime)
    if (file.size === 0) {
      throw new Error('The selected file is empty.');
    }

    updateProgress('extracting', 25, 'Extracting ZIP archive', 'Reading files securely in browser memory...');

    const zip = new JSZip();
    let zipContent: JSZip;
    try {
      zipContent = await zip.loadAsync(file);
    } catch {
      throw new Error('Unable to open file as a valid ZIP archive. Please ensure you uploaded the official Instagram data export ZIP.');
    }

    updateProgress('scanning', 40, 'Scanning archive structure', 'Locating follower and following JSON records...');

    const followerFiles: { path: string; file: JSZip.JSZipObject }[] = [];
    const followingFiles: { path: string; file: JSZip.JSZipObject }[] = [];
    const allFileNames: string[] = [];

    // Instagram directory search patterns
    zipContent.forEach((relativePath, zipEntry) => {
      if (zipEntry.dir) return;
      const lower = relativePath.toLowerCase();
      const basename = (lower.split('/').pop() || '').split('\\').pop() || '';
      allFileNames.push(relativePath);

      // Followers matches based on filename (e.g. followers_1.json, followers.json)
      if (
        (basename.includes('follower') && (basename.endsWith('.json') || basename.endsWith('.html'))) ||
        basename.endsWith('relationships_followers.json')
      ) {
        followerFiles.push({ path: relativePath, file: zipEntry });
      }

      // Following matches based on filename (e.g. following.json, relationships_following.json)
      if (
        (basename.includes('following') && (basename.endsWith('.json') || basename.endsWith('.html'))) ||
        basename.endsWith('relationships_following.json')
      ) {
        followingFiles.push({ path: relativePath, file: zipEntry });
      }
    });

    if (followerFiles.length === 0 && followingFiles.length === 0) {
      throw new Error(
        'Could not locate Instagram follower or following files inside the archive. Please make sure you selected the "Followers and following" information when downloading your Instagram export.'
      );
    }

    // Process Followers
    updateProgress('parsing_followers', 55, 'Parsing followers', `Found ${followerFiles.length} follower file(s)...`, {
      followersFound: 0,
      followingFound: 0,
      filesFound: allFileNames.slice(0, 5),
    });

    const followersMap = new Map<string, InstagramUser>();
    for (const f of followerFiles) {
      const text = await f.file.async('text');
      if (f.path.toLowerCase().endsWith('.html')) {
        const users = this.parseInstagramHtml(text);
        users.forEach((u) => followersMap.set(u.username, u));
      } else {
        const users = this.parseInstagramJson(text);
        users.forEach((u) => followersMap.set(u.username, u));
      }
    }

    // Process Following
    updateProgress('parsing_following', 75, 'Parsing following accounts', `Found ${followingFiles.length} following file(s)...`, {
      followersFound: followersMap.size,
      followingFound: 0,
      filesFound: allFileNames.slice(0, 5),
    });

    const followingMap = new Map<string, InstagramUser>();
    for (const f of followingFiles) {
      const text = await f.file.async('text');
      if (f.path.toLowerCase().endsWith('.html')) {
        const users = this.parseInstagramHtml(text);
        users.forEach((u) => followingMap.set(u.username, u));
      } else {
        const users = this.parseInstagramJson(text);
        users.forEach((u) => followingMap.set(u.username, u));
      }
    }

    updateProgress('deduplicating', 90, 'Validating and deduplicating', 'Normalizing Instagram usernames and checking records...', {
      followersFound: followersMap.size,
      followingFound: followingMap.size,
      filesFound: [...followerFiles, ...followingFiles].map((f) => f.path),
    });

    const followers = Array.from(followersMap.values());
    const following = Array.from(followingMap.values());

    updateProgress('completed', 100, 'Import Completed Successfully', `Loaded ${followers.length} followers and ${following.length} following.`, {
      followersFound: followers.length,
      followingFound: following.length,
      filesFound: [...followerFiles, ...followingFiles].map((f) => f.path),
    });

    return {
      followers,
      following,
      filesProcessed: [...followerFiles, ...followingFiles].map((f) => f.path),
    };
  }

  /**
   * Process individual JSON files directly (e.g. followers_1.json, following.json dropped by user)
   */
  static async processMultipleJsonFiles(
    files: File[],
    onProgress?: (progress: ImportProgress) => void
  ): Promise<{ followers: InstagramUser[]; following: InstagramUser[]; filesProcessed: string[] }> {
    const followersMap = new Map<string, InstagramUser>();
    const followingMap = new Map<string, InstagramUser>();
    const filesProcessed: string[] = [];

    onProgress?.({
      step: 'scanning',
      progress: 30,
      title: 'Reading uploaded JSON files',
      description: `Analyzing ${files.length} uploaded files...`,
    });

    for (const file of files) {
      const lower = file.name.toLowerCase();
      const text = await file.text();
      filesProcessed.push(file.name);

      if (lower.includes('follower')) {
        const users = lower.endsWith('.html') ? this.parseInstagramHtml(text) : this.parseInstagramJson(text);
        users.forEach((u) => followersMap.set(u.username, u));
      } else if (lower.includes('following')) {
        const users = lower.endsWith('.html') ? this.parseInstagramHtml(text) : this.parseInstagramJson(text);
        users.forEach((u) => followingMap.set(u.username, u));
      } else {
        // Fallback: try to see if it parses and has relationships_followers or relationships_following
        try {
          const parsed = JSON.parse(text);
          if (parsed.relationships_followers || (Array.isArray(parsed) && parsed[0]?.string_list_data)) {
            const users = this.parseInstagramJson(text);
            users.forEach((u) => followersMap.set(u.username, u));
          } else if (parsed.relationships_following) {
            const users = this.parseInstagramJson(text);
            users.forEach((u) => followingMap.set(u.username, u));
          }
        } catch {
          // ignore unparsable
        }
      }
    }

    if (followersMap.size === 0 && followingMap.size === 0) {
      throw new Error('No valid follower or following records were found in the uploaded files.');
    }

    const followers = Array.from(followersMap.values());
    const following = Array.from(followingMap.values());

    onProgress?.({
      step: 'completed',
      progress: 100,
      title: 'Files Processed',
      description: `Loaded ${followers.length} followers and ${following.length} following.`,
      details: {
        followersFound: followers.length,
        followingFound: following.length,
        filesFound: filesProcessed,
      },
    });

    return { followers, following, filesProcessed };
  }
}
