import React from 'react';
import { useApp } from '../context/AppContext';
import { ExportService } from '../services/ExportService';
import {
  FileText,
  Download,
  Printer,
  FileSpreadsheet,
  Users,
  UserCheck,
  UserMinus,
  UserX,
  Heart,
  Repeat,
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const { comparison, activeSnapshot, previousSnapshot, addToast, setCurrentPage } = useApp();

  if (!activeSnapshot || !comparison) {
    return (
      <div className="text-center py-16 space-y-4">
        <FileText className="w-12 h-12 text-[#94A3B8] mx-auto" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">No Report Data Available</h3>
        <p className="text-xs text-[#94A3B8]">Import your Instagram data to generate reports.</p>
        <button
          onClick={() => setCurrentPage('import')}
          className="px-4 py-2 bg-[#8B5CF6] text-white text-xs font-semibold rounded-xl"
        >
          Import Data
        </button>
      </div>
    );
  }

  const handleExportCsv = (type: 'followers' | 'following' | 'unfollowers' | 'notFollowingBack' | 'fans' | 'mutuals') => {
    let list = activeSnapshot.followers;
    let filename = `instagram_followers_${Date.now()}`;
    let title = 'Followers';

    if (type === 'following') {
      list = activeSnapshot.following;
      filename = `instagram_following_${Date.now()}`;
      title = 'Following';
    } else if (type === 'unfollowers') {
      list = comparison.unfollowers;
      filename = `instagram_unfollowers_${Date.now()}`;
      title = 'Unfollowers';
    } else if (type === 'notFollowingBack') {
      list = comparison.notFollowingBack;
      filename = `instagram_not_following_back_${Date.now()}`;
      title = 'Not Following Back';
    } else if (type === 'fans') {
      list = comparison.fans;
      filename = `instagram_fans_${Date.now()}`;
      title = 'Fans';
    } else if (type === 'mutuals') {
      list = comparison.mutuals;
      filename = `instagram_mutual_followers_${Date.now()}`;
      title = 'Mutual Followers';
    }

    ExportService.exportUsersToCsv(filename, list, title);
    addToast({
      type: 'success',
      title: 'CSV Downloaded',
      message: `Exported ${list.length} accounts to ${filename}.csv`,
    });
  };

  const handleExportSummaryCsv = () => {
    ExportService.exportSummaryCsv(comparison);
    addToast({
      type: 'success',
      title: 'Summary CSV Downloaded',
      message: 'Generated comprehensive comparison summary CSV.',
    });
  };

  const handlePrintPdf = () => {
    window.print();
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="no-print">
        <h2 className="text-2xl font-extrabold text-[#F8FAFC]">Export Reports & Backups</h2>
        <p className="text-sm text-[#94A3B8] mt-1">
          Download formatted CSV spreadsheets or generate a print-ready executive PDF report.
        </p>
      </div>

      {/* CSV Export Suite */}
      <div className="no-print bg-[#151B27] border border-[#252B38] rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <FileSpreadsheet className="w-5 h-5 text-[#8B5CF6]" />
            <h3 className="text-base font-bold text-[#F8FAFC]">CSV Spreadsheet Downloads</h3>
          </div>
          <button
            onClick={handleExportSummaryCsv}
            className="px-3.5 py-1.5 rounded-xl bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-xs font-semibold shadow-md shadow-[#8B5CF6]/20 transition-colors flex items-center space-x-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Master Summary CSV</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-2">
          <button
            onClick={() => handleExportCsv('followers')}
            className="p-4 rounded-xl bg-[#10141D] hover:bg-[#1C2433] border border-[#252B38] flex items-center justify-between text-left transition-colors group"
          >
            <div className="flex items-center space-x-3">
              <Users className="w-4 h-4 text-[#8B5CF6]" />
              <div>
                <span className="text-xs font-bold text-[#F8FAFC] block">Followers</span>
                <span className="text-[10px] text-[#94A3B8]">
                  {activeSnapshot.followersCount} accounts
                </span>
              </div>
            </div>
            <Download className="w-3.5 h-3.5 text-[#94A3B8] group-hover:text-[#8B5CF6]" />
          </button>

          <button
            onClick={() => handleExportCsv('following')}
            className="p-4 rounded-xl bg-[#10141D] hover:bg-[#1C2433] border border-[#252B38] flex items-center justify-between text-left transition-colors group"
          >
            <div className="flex items-center space-x-3">
              <UserCheck className="w-4 h-4 text-[#6366F1]" />
              <div>
                <span className="text-xs font-bold text-[#F8FAFC] block">Following</span>
                <span className="text-[10px] text-[#94A3B8]">
                  {activeSnapshot.followingCount} accounts
                </span>
              </div>
            </div>
            <Download className="w-3.5 h-3.5 text-[#94A3B8] group-hover:text-[#6366F1]" />
          </button>

          <button
            onClick={() => handleExportCsv('notFollowingBack')}
            className="p-4 rounded-xl bg-[#10141D] hover:bg-[#1C2433] border border-[#252B38] flex items-center justify-between text-left transition-colors group"
          >
            <div className="flex items-center space-x-3">
              <UserX className="w-4 h-4 text-[#F59E0B]" />
              <div>
                <span className="text-xs font-bold text-[#F8FAFC] block">Not Following Back</span>
                <span className="text-[10px] text-[#94A3B8]">
                  {comparison.notFollowingBack.length} accounts
                </span>
              </div>
            </div>
            <Download className="w-3.5 h-3.5 text-[#94A3B8] group-hover:text-[#F59E0B]" />
          </button>

          <button
            onClick={() => handleExportCsv('unfollowers')}
            disabled={!comparison.hasPreviousSnapshot}
            className="p-4 rounded-xl bg-[#10141D] hover:bg-[#1C2433] border border-[#252B38] flex items-center justify-between text-left transition-colors group disabled:opacity-40"
          >
            <div className="flex items-center space-x-3">
              <UserMinus className="w-4 h-4 text-[#EF4444]" />
              <div>
                <span className="text-xs font-bold text-[#F8FAFC] block">Unfollowers</span>
                <span className="text-[10px] text-[#94A3B8]">
                  {comparison.hasPreviousSnapshot ? `${comparison.unfollowers.length} accounts` : 'Requires 2 snapshots'}
                </span>
              </div>
            </div>
            <Download className="w-3.5 h-3.5 text-[#94A3B8] group-hover:text-[#EF4444]" />
          </button>

          <button
            onClick={() => handleExportCsv('fans')}
            className="p-4 rounded-xl bg-[#10141D] hover:bg-[#1C2433] border border-[#252B38] flex items-center justify-between text-left transition-colors group"
          >
            <div className="flex items-center space-x-3">
              <Heart className="w-4 h-4 text-[#6366F1]" />
              <div>
                <span className="text-xs font-bold text-[#F8FAFC] block">Fans</span>
                <span className="text-[10px] text-[#94A3B8]">{comparison.fans.length} accounts</span>
              </div>
            </div>
            <Download className="w-3.5 h-3.5 text-[#94A3B8] group-hover:text-[#6366F1]" />
          </button>

          <button
            onClick={() => handleExportCsv('mutuals')}
            className="p-4 rounded-xl bg-[#10141D] hover:bg-[#1C2433] border border-[#252B38] flex items-center justify-between text-left transition-colors group"
          >
            <div className="flex items-center space-x-3">
              <Repeat className="w-4 h-4 text-[#22C55E]" />
              <div>
                <span className="text-xs font-bold text-[#F8FAFC] block">Mutual Followers</span>
                <span className="text-[10px] text-[#94A3B8]">
                  {comparison.mutuals.length} accounts
                </span>
              </div>
            </div>
            <Download className="w-3.5 h-3.5 text-[#94A3B8] group-hover:text-[#22C55E]" />
          </button>
        </div>
      </div>

      {/* Printable Report Section */}
      <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 md:p-8 shadow-xl space-y-6 print-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#252B38] pb-6">
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-wider text-[#F8FAFC]">
                FOLLOW<span className="text-[#8B5CF6]">TRACK</span>
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-[#8B5CF6]/15 text-[#8B5CF6] font-semibold">
                Executive Audit Report
              </span>
            </div>
            <p className="text-xs text-[#94A3B8] mt-1">
              Generated on {new Date().toLocaleDateString(undefined, { dateStyle: 'full' })}
            </p>
          </div>

          <button
            onClick={handlePrintPdf}
            className="no-print px-4 py-2 rounded-xl bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-xs font-semibold shadow-md shadow-[#8B5CF6]/20 transition-all flex items-center space-x-2 self-start sm:self-auto"
          >
            <Printer className="w-4 h-4" />
            <span>Print or Save to PDF</span>
          </button>
        </div>

        {/* Executive Report Content */}
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
            <div className="bg-[#10141D] p-4 rounded-xl border border-[#252B38] print:border-gray-300">
              <span className="text-[10px] uppercase font-semibold text-[#94A3B8] block">Followers</span>
              <span className="text-2xl font-bold text-[#F8FAFC]">{activeSnapshot.followersCount}</span>
            </div>
            <div className="bg-[#10141D] p-4 rounded-xl border border-[#252B38] print:border-gray-300">
              <span className="text-[10px] uppercase font-semibold text-[#94A3B8] block">Following</span>
              <span className="text-2xl font-bold text-[#F8FAFC]">{activeSnapshot.followingCount}</span>
            </div>
            <div className="bg-[#10141D] p-4 rounded-xl border border-[#252B38] print:border-gray-300">
              <span className="text-[10px] uppercase font-semibold text-[#94A3B8] block">Not Following Back</span>
              <span className="text-2xl font-bold text-[#F59E0B]">{comparison.notFollowingBack.length}</span>
            </div>
            <div className="bg-[#10141D] p-4 rounded-xl border border-[#252B38] print:border-gray-300">
              <span className="text-[10px] uppercase font-semibold text-[#94A3B8] block">Mutuals</span>
              <span className="text-2xl font-bold text-[#22C55E]">{comparison.mutuals.length}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="bg-[#10141D] p-4 rounded-xl border border-[#252B38] space-y-2 print:border-gray-300">
              <h4 className="font-bold text-[#F8FAFC]">Snapshot Reference</h4>
              <p className="text-[#94A3B8]">
                <strong>Active Snapshot:</strong> {activeSnapshot.name} ({new Date(activeSnapshot.createdAt).toLocaleString()})
              </p>
              {previousSnapshot && (
                <p className="text-[#94A3B8]">
                  <strong>Baseline Snapshot:</strong> {previousSnapshot.name} ({new Date(previousSnapshot.createdAt).toLocaleString()})
                </p>
              )}
              <p className="text-[#94A3B8]">
                <strong>Net Follower Change:</strong>{' '}
                <span className={comparison.netFollowerGrowth >= 0 ? 'text-[#22C55E]' : 'text-[#EF4444]'}>
                  {comparison.netFollowerGrowth >= 0 ? `+${comparison.netFollowerGrowth}` : comparison.netFollowerGrowth}
                </span>
              </p>
            </div>

            <div className="bg-[#10141D] p-4 rounded-xl border border-[#252B38] space-y-2 print:border-gray-300">
              <h4 className="font-bold text-[#F8FAFC]">Security & Verification Audit</h4>
              <p className="text-[#94A3B8]">
                All data extracted directly from official Instagram Accounts Center download.
              </p>
              <p className="text-[#94A3B8]">
                Processed purely on client device. Zero passwords or cookies collected.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
