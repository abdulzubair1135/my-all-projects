import { describe, it, expect, vi } from 'vitest';
import { ExportService } from '../services/ExportService';
import type { InstagramUser } from '../types';

describe('ExportService', () => {
  it('correctly creates and triggers a CSV blob download link', () => {
    const mockUsers: InstagramUser[] = [
      {
        username: 'tech_guru',
        originalUsername: 'Tech_Guru',
        profileUrl: 'https://www.instagram.com/tech_guru/',
        timestamp: 1698765432000,
      },
    ];

    let clicked = false;
    let downloadedFilename = '';

    // Mock DOM elements
    const originalCreateElement = document.createElement.bind(document);
    vi.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
      const el = originalCreateElement(tagName);
      if (tagName === 'a') {
        el.click = () => {
          clicked = true;
        };
        const origSetAttr = el.setAttribute.bind(el);
        el.setAttribute = (name: string, val: string) => {
          if (name === 'download') downloadedFilename = val;
          return origSetAttr(name, val);
        };
      }
      return el;
    });

    ExportService.exportUsersToCsv('test_followers', mockUsers);

    expect(clicked).toBe(true);
    expect(downloadedFilename).toBe('test_followers.csv');
  });
});
