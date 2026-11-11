import { openDB, type IDBPDatabase } from 'idb';
import type { Snapshot, ManualUnfollowRecord, AppSettings } from '../types';

const DB_NAME = 'followtrack_db';
const DB_VERSION = 1;

interface FollowTrackDB {
  snapshots: {
    key: string;
    value: Snapshot;
    indexes: { 'by-date': number };
  };
  manual_actions: {
    key: string;
    value: ManualUnfollowRecord;
    indexes: { 'by-date': number };
  };
}

class StorageService {
  private dbPromise: Promise<IDBPDatabase<FollowTrackDB>> | null = null;

  private async getDB(): Promise<IDBPDatabase<FollowTrackDB>> {
    if (!this.dbPromise) {
      this.dbPromise = openDB<FollowTrackDB>(DB_NAME, DB_VERSION, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('snapshots')) {
            const snapshotStore = db.createObjectStore('snapshots', { keyPath: 'id' });
            snapshotStore.createIndex('by-date', 'createdAt');
          }
          if (!db.objectStoreNames.contains('manual_actions')) {
            const manualStore = db.createObjectStore('manual_actions', { keyPath: 'username' });
            manualStore.createIndex('by-date', 'timestamp');
          }
        },
      });
    }
    return this.dbPromise;
  }

  // --- Snapshots ---
  async saveSnapshot(snapshot: Snapshot): Promise<void> {
    const db = await this.getDB();
    await db.put('snapshots', snapshot);
  }

  async getAllSnapshots(): Promise<Snapshot[]> {
    const db = await this.getDB();
    const snapshots = await db.getAllFromIndex('snapshots', 'by-date');
    // Sort descending (newest first)
    return snapshots.reverse();
  }

  async getSnapshotById(id: string): Promise<Snapshot | undefined> {
    const db = await this.getDB();
    return db.get('snapshots', id);
  }

  async deleteSnapshot(id: string): Promise<void> {
    const db = await this.getDB();
    await db.delete('snapshots', id);
  }

  async updateSnapshot(snapshot: Snapshot): Promise<void> {
    const db = await this.getDB();
    await db.put('snapshots', snapshot);
  }

  // --- Manual Actions ---
  async saveManualAction(record: ManualUnfollowRecord): Promise<void> {
    const db = await this.getDB();
    await db.put('manual_actions', record);
  }

  async getAllManualActions(): Promise<ManualUnfollowRecord[]> {
    const db = await this.getDB();
    return db.getAll('manual_actions');
  }

  async removeManualAction(username: string): Promise<void> {
    const db = await this.getDB();
    await db.delete('manual_actions', username.toLowerCase().trim());
  }

  // --- Backup & Restore ---
  async exportAllData(): Promise<string> {
    const snapshots = await this.getAllSnapshots();
    const manualActions = await this.getAllManualActions();
    const settings = this.getSettings();

    const backup = {
      app: 'FollowTrack',
      version: '1.0.0',
      exportedAt: Date.now(),
      snapshots,
      manualActions,
      settings,
    };

    return JSON.stringify(backup, null, 2);
  }

  async importBackup(jsonString: string): Promise<{ snapshotCount: number; actionCount: number }> {
    try {
      const data = JSON.parse(jsonString);
      if (!data || !Array.isArray(data.snapshots)) {
        throw new Error('Invalid backup format: missing snapshots array');
      }

      const db = await this.getDB();
      const tx = db.transaction(['snapshots', 'manual_actions'], 'readwrite');

      for (const snap of data.snapshots) {
        if (snap.id && Array.isArray(snap.followers) && Array.isArray(snap.following)) {
          await tx.objectStore('snapshots').put(snap);
        }
      }

      if (Array.isArray(data.manualActions)) {
        for (const action of data.manualActions) {
          if (action.username) {
            await tx.objectStore('manual_actions').put(action);
          }
        }
      }

      await tx.done;

      if (data.settings) {
        this.saveSettings(data.settings);
      }

      return {
        snapshotCount: data.snapshots.length,
        actionCount: (data.manualActions || []).length,
      };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error during import';
      throw new Error(`Failed to restore backup: ${msg}`);
    }
  }

  async clearAllData(): Promise<void> {
    const db = await this.getDB();
    const tx = db.transaction(['snapshots', 'manual_actions'], 'readwrite');
    await tx.objectStore('snapshots').clear();
    await tx.objectStore('manual_actions').clear();
    await tx.done;
    localStorage.removeItem('followtrack_settings');
  }

  // --- LocalStorage Settings ---
  getSettings(): AppSettings {
    try {
      const saved = localStorage.getItem('followtrack_settings');
      if (saved) {
        return JSON.parse(saved);
      }
    } catch {
      // fallback
    }
    return {
      theme: 'dark',
      autoComparePrevious: true,
      exportDateFormat: 'ISO',
      confirmUnfollowActions: true,
    };
  }

  saveSettings(settings: AppSettings): void {
    try {
      localStorage.setItem('followtrack_settings', JSON.stringify(settings));
    } catch {
      // ignore
    }
  }
}

export const storageService = new StorageService();
