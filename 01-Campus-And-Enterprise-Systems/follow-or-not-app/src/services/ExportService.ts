import type { InstagramUser, ComparisonResult } from '../types';

export class ExportService {
  /**
   * Generates and triggers download of a CSV file for a given list of Instagram users.
   */
  static exportUsersToCsv(filename: string, users: InstagramUser[], listTitle?: string): void {
    const headers = ['Username', 'Profile URL', 'Original Name', 'Follow Date', 'Detection Date'];
    const titleRow = listTitle ? [`# List: ${listTitle}`] : [];
    const rows = users.map((u) => [
      `"${u.username}"`,
      `"${u.profileUrl}"`,
      `"${u.originalUsername || u.username}"`,
      `"${u.timestamp ? new Date(u.timestamp).toISOString() : 'N/A'}"`,
      `"${u.detectionDate ? new Date(u.detectionDate).toISOString() : 'N/A'}"`,
    ]);

    const csvContent = [...titleRow, headers.join(','), ...rows.map((r) => r.join(','))].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename.replace(/\.csv$/, '')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Generates an executive summary CSV for the entire comparison
   */
  static exportSummaryCsv(comparison: ComparisonResult): void {
    const lines = [
      'Category,Count,Details',
      `Total Followers,${comparison.currentSnapshot.followersCount},"Current followers count"`,
      `Total Following,${comparison.currentSnapshot.followingCount},"Current following count"`,
      `Not Following Back,${comparison.notFollowingBack.length},"Accounts you follow who do not follow back"`,
      `Fans,${comparison.fans.length},"Accounts following you whom you don't follow back"`,
      `Mutual Followers,${comparison.mutuals.length},"Mutual connections"`,
      `Unfollowers,${comparison.unfollowers.length},"Accounts that unfollowed since previous snapshot"`,
      `New Followers,${comparison.newFollowers.length},"Accounts that newly followed since previous snapshot"`,
      `Net Follower Growth,${comparison.netFollowerGrowth},"Difference in followers count"`,
      `Snapshot Date,"${new Date(comparison.currentSnapshot.createdAt).toLocaleString()}","Snapshot timestamp"`,
      `Previous Snapshot Date,"${comparison.previousSnapshot ? new Date(comparison.previousSnapshot.createdAt).toLocaleString() : 'N/A'}","Reference baseline timestamp"`,
    ];

    const blob = new Blob([lines.join('\r\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `followtrack_summary_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Triggers the browser print dialog formatted with print stylesheets for PDF saving
   */
  static triggerPrintReport(): void {
    window.print();
  }
}
