import { describe, it, expect } from 'vitest';
import { InstagramImportService } from '../services/InstagramImportService';
import JSZip from 'jszip';

describe('InstagramImportService', () => {
  describe('Username Normalization & Extraction', () => {
    it('normalizes username casing, removes whitespace, and strips leading @', () => {
      expect(InstagramImportService.normalizeUsername('@JohnDoe ')).toBe('johndoe');
      expect(InstagramImportService.normalizeUsername('@@Cool_User.99 ')).toBe('cool_user.99');
      expect(InstagramImportService.normalizeUsername('   Sarah_Designs/ ')).toBe('sarah_designs');
      expect(InstagramImportService.normalizeUsername('alex?utm_source=ig')).toBe('alex');
    });

    it('extracts username accurately from Instagram profile URLs', () => {
      expect(
        InstagramImportService.extractUsernameFromUrl('https://www.instagram.com/natgeo/')
      ).toBe('natgeo');
      expect(
        InstagramImportService.extractUsernameFromUrl('https://instagram.com/verge?igsh=123')
      ).toBe('verge');
    });
  });

  describe('JSON Parsing Engine', () => {
    it('parses standard modern Instagram followers format (array of objects with string_list_data)', () => {
      const sampleFollowersJson = JSON.stringify([
        {
          title: '',
          media_list_data: [],
          string_list_data: [
            {
              href: 'https://www.instagram.com/user_one',
              value: 'user_one',
              timestamp: 1698765432,
            },
          ],
        },
        {
          title: '',
          media_list_data: [],
          string_list_data: [
            {
              href: 'https://www.instagram.com/user_two',
              value: 'user_two',
              timestamp: 1698765999,
            },
          ],
        },
      ]);

      const users = InstagramImportService.parseInstagramJson(sampleFollowersJson);
      expect(users).toHaveLength(2);
      expect(users[0].username).toBe('user_one');
      expect(users[1].username).toBe('user_two');
      expect(users[0].profileUrl).toBe('https://www.instagram.com/user_one');
      expect(users[0].timestamp).toBe(1698765432000);
    });

    it('parses wrapped object format with relationships_following key', () => {
      const sampleFollowingJson = JSON.stringify({
        relationships_following: [
          {
            title: 'influencer_pro',
            media_list_data: [],
            string_list_data: [
              {
                href: 'https://www.instagram.com/influencer_pro',
                value: 'influencer_pro',
                timestamp: 1690000000,
              },
            ],
          },
        ],
      });

      const users = InstagramImportService.parseInstagramJson(sampleFollowingJson);
      expect(users).toHaveLength(1);
      expect(users[0].username).toBe('influencer_pro');
    });

    it('deduplicates accounts if duplicate entries appear in JSON', () => {
      const duplicateJson = JSON.stringify([
        {
          string_list_data: [{ value: 'DuplicateUser' }],
        },
        {
          string_list_data: [{ value: 'duplicateuser' }],
        },
        {
          string_list_data: [{ value: ' @duplicateuser ' }],
        },
      ]);

      const users = InstagramImportService.parseInstagramJson(duplicateJson);
      expect(users).toHaveLength(1);
      expect(users[0].username).toBe('duplicateuser');
    });

    it('parses HTML exports safely as fallback', () => {
      const htmlContent = `
        <!DOCTYPE html>
        <html>
          <body>
            <div><a href="https://www.instagram.com/html_user_1/">html_user_1</a></div>
            <div><a href="https://www.instagram.com/html_user_2/">html_user_2</a></div>
          </body>
        </html>
      `;

      const users = InstagramImportService.parseInstagramHtml(htmlContent);
      expect(users).toHaveLength(2);
      expect(users[0].username).toBe('html_user_1');
      expect(users[1].username).toBe('html_user_2');
    });
  });

  describe('ZIP Extraction & File Resolution', () => {
    it('extracts and parses ZIP archive containing followers_1.json and following.json', async () => {
      const zip = new JSZip();

      // Create simulated followers_1.json
      const followersData = [
        { string_list_data: [{ value: 'alice', href: 'https://www.instagram.com/alice' }] },
        { string_list_data: [{ value: 'bob', href: 'https://www.instagram.com/bob' }] },
      ];
      zip.file('followers_and_following/followers_1.json', JSON.stringify(followersData));

      // Create simulated following.json
      const followingData = {
        relationships_following: [
          { string_list_data: [{ value: 'bob', href: 'https://www.instagram.com/bob' }] },
          { string_list_data: [{ value: 'charlie', href: 'https://www.instagram.com/charlie' }] },
        ],
      };
      zip.file('followers_and_following/following.json', JSON.stringify(followingData));

      const zipBlob = await zip.generateAsync({ type: 'blob' });
      const testFile = new File([zipBlob], 'instagram_export.zip', { type: 'application/zip' });

      const result = await InstagramImportService.processZipFile(testFile);
      expect(result.followers).toHaveLength(2);
      expect(result.following).toHaveLength(2);
      expect(result.followers.map((u) => u.username)).toEqual(['alice', 'bob']);
      expect(result.following.map((u) => u.username)).toEqual(['bob', 'charlie']);
    });
  });
});
