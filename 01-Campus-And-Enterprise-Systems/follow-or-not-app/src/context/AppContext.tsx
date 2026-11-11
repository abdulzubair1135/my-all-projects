import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import type {
  Snapshot,
  ComparisonResult,
  ManualUnfollowRecord,
  AppSettings,
  PageView,
} from '../types';
import { storageService } from '../services/StorageService';
import { FollowerComparisonService } from '../services/FollowerComparisonService';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

interface AppContextType {
  // Navigation
  currentPage: PageView;
  setCurrentPage: (page: PageView) => void;

  // Snapshots
  snapshots: Snapshot[];
  activeSnapshot: Snapshot | null;
  previousSnapshot: Snapshot | null;
  setActiveSnapshotId: (id: string) => void;
  setPreviousSnapshotId: (id: string | null) => void;
  loadSnapshots: () => Promise<void>;
  deleteSnapshot: (id: string) => Promise<void>;

  // Comparison
  comparison: ComparisonResult | null;

  // Manual actions
  manualActions: Map<string, ManualUnfollowRecord>;
  markManualAction: (username: string, status: 'unfollowed' | 'skipped' | 'whitelist', notes?: string) => Promise<void>;
  removeManualAction: (username: string) => Promise<void>;

  // Settings
  settings: AppSettings;
  updateSettings: (newSettings: Partial<AppSettings>) => void;

  // Toasts
  toasts: ToastMessage[];
  addToast: (toast: Omit<ToastMessage, 'id'>) => void;
  removeToast: (id: string) => void;

  // Loading state
  isLoading: boolean;
  refreshData: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentPage, setCurrentPage] = useState<PageView>('landing');
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [activeSnapshotId, setActiveSnapshotIdState] = useState<string | null>(null);
  const [previousSnapshotId, setPreviousSnapshotIdState] = useState<string | null>(null);
  const [manualActions, setManualActions] = useState<Map<string, ManualUnfollowRecord>>(new Map());
  const [settings, setSettings] = useState<AppSettings>(storageService.getSettings());
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Toast dispatchers
  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(
    (toast: Omit<ToastMessage, 'id'>) => {
      const id = Math.random().toString(36).substring(2, 9);
      const newToast = { ...toast, id };
      setToasts((prev) => [...prev, newToast]);

      const duration = toast.duration ?? 4000;
      setTimeout(() => {
        removeToast(id);
      }, duration);
    },
    [removeToast]
  );

  // Load all initial data from IndexedDB
  const loadSnapshots = useCallback(async () => {
    try {
      setIsLoading(true);
      const snaps = await storageService.getAllSnapshots();
      setSnapshots(snaps);

      // If we have snapshots, pick the newest as active
      if (snaps.length > 0) {
        setActiveSnapshotIdState((prev) => {
          if (prev && snaps.some((s) => s.id === prev)) return prev;
          return snaps[0].id;
        });

        // Set previous snapshot as second newest by default
        setPreviousSnapshotIdState((prev) => {
          if (prev && snaps.some((s) => s.id === prev)) return prev;
          return snaps.length > 1 ? snaps[1].id : null;
        });
      } else {
        setActiveSnapshotIdState(null);
        setPreviousSnapshotIdState(null);
      }

      // Load manual actions
      const actions = await storageService.getAllManualActions();
      const actionMap = new Map<string, ManualUnfollowRecord>();
      actions.forEach((a) => actionMap.set(a.username.toLowerCase(), a));
      setManualActions(actionMap);
    } catch (err) {
      console.error('Failed to load local data:', err);
      addToast({
        type: 'error',
        title: 'Storage Error',
        message: 'Could not access IndexedDB storage.',
      });
    } finally {
      setIsLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    loadSnapshots();
  }, [loadSnapshots]);

  const refreshData = useCallback(async () => {
    await loadSnapshots();
  }, [loadSnapshots]);

  const deleteSnapshot = useCallback(
    async (id: string) => {
      try {
        await storageService.deleteSnapshot(id);
        addToast({
          type: 'success',
          title: 'Snapshot Deleted',
          message: 'The snapshot was removed from local storage.',
        });
        await loadSnapshots();
      } catch {
        addToast({
          type: 'error',
          title: 'Error',
          message: 'Failed to delete snapshot.',
        });
      }
    },
    [addToast, loadSnapshots]
  );

  const markManualAction = useCallback(
    async (username: string, status: 'unfollowed' | 'skipped' | 'whitelist', notes?: string) => {
      const record: ManualUnfollowRecord = {
        username: username.toLowerCase().trim(),
        timestamp: Date.now(),
        status,
        notes,
      };
      await storageService.saveManualAction(record);
      setManualActions((prev) => {
        const next = new Map(prev);
        next.set(record.username, record);
        return next;
      });
    },
    []
  );

  const removeManualAction = useCallback(async (username: string) => {
    const norm = username.toLowerCase().trim();
    await storageService.removeManualAction(norm);
    setManualActions((prev) => {
      const next = new Map(prev);
      next.delete(norm);
      return next;
    });
  }, []);

  const updateSettings = useCallback((newSettings: Partial<AppSettings>) => {
    setSettings((prev) => {
      const updated = { ...prev, ...newSettings };
      storageService.saveSettings(updated);
      return updated;
    });
  }, []);

  const activeSnapshot = useMemo(() => {
    if (!activeSnapshotId) return snapshots[0] || null;
    return snapshots.find((s) => s.id === activeSnapshotId) || snapshots[0] || null;
  }, [snapshots, activeSnapshotId]);

  const previousSnapshot = useMemo(() => {
    if (!previousSnapshotId) {
      if (!activeSnapshot) return null;
      // Find snapshot created right before the active snapshot
      const activeIdx = snapshots.findIndex((s) => s.id === activeSnapshot.id);
      return activeIdx >= 0 && activeIdx < snapshots.length - 1 ? snapshots[activeIdx + 1] : null;
    }
    return snapshots.find((s) => s.id === previousSnapshotId) || null;
  }, [snapshots, previousSnapshotId, activeSnapshot]);

  const comparison = useMemo(() => {
    if (!activeSnapshot) return null;
    return FollowerComparisonService.compare(activeSnapshot, previousSnapshot || undefined);
  }, [activeSnapshot, previousSnapshot]);

  return (
    <AppContext.Provider
      value={{
        currentPage,
        setCurrentPage,
        snapshots,
        activeSnapshot,
        previousSnapshot,
        setActiveSnapshotId: setActiveSnapshotIdState,
        setPreviousSnapshotId: setPreviousSnapshotIdState,
        loadSnapshots,
        deleteSnapshot,
        comparison,
        manualActions,
        markManualAction,
        removeManualAction,
        settings,
        updateSettings,
        toasts,
        addToast,
        removeToast,
        isLoading,
        refreshData,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
