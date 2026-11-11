import React, { useState, useMemo } from 'react';
import type { InstagramUser } from '../../types';
import {
  Search,
  ExternalLink,
  Copy,
  Check,
  ArrowUpDown,
  Download,
  CheckSquare,
  Square,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { ExportService } from '../../services/ExportService';
import { useApp } from '../../context/AppContext';

interface UserTableProps {
  users: InstagramUser[];
  title: string;
  subtitle?: string;
  showSelection?: boolean;
  selectedUsernames?: Set<string>;
  onToggleSelect?: (username: string) => void;
  onSelectAll?: (usernames: string[]) => void;
  onDeselectAll?: () => void;
  actionButtonLabel?: string;
  onActionClick?: (user: InstagramUser) => void;
  badgeLabel?: string;
  badgeType?: 'danger' | 'warning' | 'success' | 'info';
  emptyMessage?: string;
}

export const UserTable: React.FC<UserTableProps> = ({
  users,
  title,
  subtitle,
  showSelection = false,
  selectedUsernames = new Set(),
  onToggleSelect,
  onSelectAll,
  onDeselectAll,
  actionButtonLabel,
  onActionClick,
  badgeLabel,
  badgeType = 'info',
  emptyMessage = 'No accounts found.',
}) => {
  const { addToast, manualActions } = useApp();
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'alpha-asc' | 'alpha-desc' | 'date-newest' | 'date-oldest'>('alpha-asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [copiedUser, setCopiedUser] = useState<string | null>(null);

  // Filtered & sorted users
  const filteredUsers = useMemo(() => {
    let result = users;

    if (search.trim()) {
      const q = search.toLowerCase().trim();
      result = result.filter(
        (u) =>
          u.username.toLowerCase().includes(q) ||
          (u.originalUsername && u.originalUsername.toLowerCase().includes(q))
      );
    }

    return [...result].sort((a, b) => {
      if (sortBy === 'alpha-asc') {
        return a.username.localeCompare(b.username);
      }
      if (sortBy === 'alpha-desc') {
        return b.username.localeCompare(a.username);
      }
      if (sortBy === 'date-newest') {
        const timeA = a.timestamp || a.detectionDate || 0;
        const timeB = b.timestamp || b.detectionDate || 0;
        return timeB - timeA;
      }
      if (sortBy === 'date-oldest') {
        const timeA = a.timestamp || a.detectionDate || 0;
        const timeB = b.timestamp || b.detectionDate || 0;
        return timeA - timeB;
      }
      return 0;
    });
  }, [users, search, sortBy]);

  // Pagination
  const totalPages = Math.max(1, Math.ceil(filteredUsers.length / pageSize));
  const paginatedUsers = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredUsers.slice(start, start + pageSize);
  }, [filteredUsers, currentPage, pageSize]);

  const handleCopy = (username: string) => {
    navigator.clipboard.writeText(username);
    setCopiedUser(username);
    addToast({
      type: 'info',
      title: 'Copied to clipboard',
      message: `@${username}`,
      duration: 2000,
    });
    setTimeout(() => {
      setCopiedUser(null);
    }, 2000);
  };

  const handleExportCsv = () => {
    const toExport =
      selectedUsernames.size > 0
        ? users.filter((u) => selectedUsernames.has(u.username))
        : filteredUsers;

    const exportName = `followtrack_${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}`;
    ExportService.exportUsersToCsv(exportName, toExport, title);
    addToast({
      type: 'success',
      title: 'CSV Exported',
      message: `Exported ${toExport.length} accounts.`,
    });
  };

  const isAllSelected =
    filteredUsers.length > 0 &&
    filteredUsers.every((u) => selectedUsernames.has(u.username));

  const handleToggleAll = () => {
    if (isAllSelected) {
      onDeselectAll?.();
    } else {
      onSelectAll?.(filteredUsers.map((u) => u.username));
    }
  };

  return (
    <div className="bg-[#151B27] border border-[#252B38] rounded-2xl overflow-hidden shadow-xl">
      {/* Table Header Bar */}
      <div className="p-5 border-b border-[#252B38] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-bold text-[#F8FAFC]">{title}</h2>
            <span className="text-xs font-semibold px-2.5 py-1 bg-[#10141D] text-[#8B5CF6] border border-[#252B38] rounded-full">
              {filteredUsers.length} {filteredUsers.length === 1 ? 'account' : 'accounts'}
            </span>
          </div>
          {subtitle && <p className="text-xs text-[#94A3B8] mt-1">{subtitle}</p>}
        </div>

        {/* Search, Sort, Export Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="relative">
            <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
              placeholder="Search username..."
              className="bg-[#10141D] text-[#F8FAFC] placeholder-[#94A3B8] text-xs pl-9 pr-3 py-2 rounded-xl border border-[#252B38] focus:outline-none focus:border-[#8B5CF6] transition-colors w-44 md:w-56"
            />
          </div>

          <div className="relative">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-[#10141D] text-[#94A3B8] text-xs px-3 py-2 rounded-xl border border-[#252B38] focus:outline-none focus:border-[#8B5CF6] transition-colors appearance-none pr-8 cursor-pointer"
            >
              <option value="alpha-asc">A to Z</option>
              <option value="alpha-desc">Z to A</option>
              <option value="date-newest">Newest First</option>
              <option value="date-oldest">Oldest First</option>
            </select>
            <ArrowUpDown className="w-3.5 h-3.5 text-[#94A3B8] absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          <button
            onClick={handleExportCsv}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-[#10141D] hover:bg-[#1C2433] text-xs font-medium text-[#F8FAFC] border border-[#252B38] transition-colors"
            title="Export CSV"
          >
            <Download className="w-3.5 h-3.5 text-[#8B5CF6]" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Multi-select Controls (if selection enabled) */}
      {showSelection && (
        <div className="px-5 py-2.5 bg-[#10141D]/60 border-b border-[#252B38] flex items-center justify-between text-xs text-[#94A3B8]">
          <div className="flex items-center space-x-3">
            <button
              onClick={handleToggleAll}
              className="flex items-center space-x-2 text-[#F8FAFC] hover:text-[#8B5CF6] transition-colors"
            >
              {isAllSelected ? (
                <CheckSquare className="w-4 h-4 text-[#8B5CF6]" />
              ) : (
                <Square className="w-4 h-4 text-[#94A3B8]" />
              )}
              <span>{isAllSelected ? 'Deselect All' : 'Select All Filtered'}</span>
            </button>
            <span>•</span>
            <span>{selectedUsernames.size} selected</span>
          </div>

          {selectedUsernames.size > 0 && onDeselectAll && (
            <button
              onClick={onDeselectAll}
              className="text-[#EF4444] hover:underline"
            >
              Clear selection
            </button>
          )}
        </div>
      )}

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-[#252B38] text-[11px] font-semibold text-[#94A3B8] uppercase tracking-wider bg-[#10141D]/30">
              {showSelection && <th className="py-3 px-4 w-10"></th>}
              <th className="py-3 px-4">Account</th>
              <th className="py-3 px-4">Instagram Link</th>
              <th className="py-3 px-4">Date / Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#252B38]/60 text-sm">
            {paginatedUsers.length === 0 ? (
              <tr>
                <td colSpan={showSelection ? 5 : 4} className="py-12 text-center text-[#94A3B8]">
                  <div className="max-w-xs mx-auto space-y-2">
                    <p className="text-sm font-medium">{emptyMessage}</p>
                    {search && (
                      <button
                        onClick={() => setSearch('')}
                        className="text-xs text-[#8B5CF6] hover:underline"
                      >
                        Reset search filter
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ) : (
              paginatedUsers.map((user) => {
                const isSelected = selectedUsernames.has(user.username);
                const manualAction = manualActions.get(user.username);

                return (
                  <tr
                    key={user.username}
                    className={`hover:bg-[#1C2433]/50 transition-colors ${
                      isSelected ? 'bg-[#8B5CF6]/5' : ''
                    }`}
                  >
                    {showSelection && (
                      <td className="py-3 px-4">
                        <button
                          onClick={() => onToggleSelect?.(user.username)}
                          className="p-1 rounded text-[#94A3B8] hover:text-[#8B5CF6] transition-colors"
                        >
                          {isSelected ? (
                            <CheckSquare className="w-4 h-4 text-[#8B5CF6]" />
                          ) : (
                            <Square className="w-4 h-4 text-[#94A3B8]" />
                          )}
                        </button>
                      </td>
                    )}

                    {/* Account column */}
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#8B5CF6] to-[#6366F1] flex items-center justify-center font-bold text-white text-xs shrink-0 shadow-xs">
                          {user.username.substring(0, 1).toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center space-x-1.5">
                            <span className="font-semibold text-[#F8FAFC] truncate">
                              @{user.originalUsername || user.username}
                            </span>
                            {user.isVerified && (
                              <span title="Verified">
                                <ShieldCheck className="w-3.5 h-3.5 text-[#6366F1]" />
                              </span>
                            )}
                          </div>
                          <span className="text-[11px] text-[#94A3B8]">
                            instagram.com/{user.username}
                          </span>
                        </div>
                      </div>
                    </td>

                    {/* Link */}
                    <td className="py-3 px-4">
                      <a
                        href={user.profileUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-1 text-xs text-[#8B5CF6] hover:text-[#A78BFA] transition-colors font-medium hover:underline"
                      >
                        <span>Open Profile</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>

                    {/* Date / Status */}
                    <td className="py-3 px-4">
                      <div className="flex flex-col space-y-1">
                        {user.timestamp ? (
                          <span className="text-xs text-[#94A3B8]">
                            {new Date(user.timestamp).toLocaleDateString(undefined, {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                            })}
                          </span>
                        ) : user.detectionDate ? (
                          <span className="text-xs text-[#94A3B8]">
                            Detected: {new Date(user.detectionDate).toLocaleDateString()}
                          </span>
                        ) : (
                          <span className="text-xs text-[#94A3B8]">--</span>
                        )}

                        {manualAction && (
                          <span
                            className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full w-fit ${
                              manualAction.status === 'unfollowed'
                                ? 'bg-[#EF4444]/15 text-[#EF4444]'
                                : manualAction.status === 'whitelist'
                                ? 'bg-[#22C55E]/15 text-[#22C55E]'
                                : 'bg-[#252B38] text-[#94A3B8]'
                            }`}
                          >
                            {manualAction.status === 'unfollowed'
                              ? 'Marked Unfollowed'
                              : manualAction.status === 'whitelist'
                              ? 'Whitelisted'
                              : 'Skipped'}
                          </span>
                        )}

                        {!manualAction && badgeLabel && (
                          <span
                            className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full w-fit ${
                              badgeType === 'danger'
                                ? 'bg-[#EF4444]/15 text-[#EF4444]'
                                : badgeType === 'warning'
                                ? 'bg-[#F59E0B]/15 text-[#F59E0B]'
                                : badgeType === 'success'
                                ? 'bg-[#22C55E]/15 text-[#22C55E]'
                                : 'bg-[#6366F1]/15 text-[#6366F1]'
                            }`}
                          >
                            {badgeLabel}
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-4 text-right">
                      <div className="inline-flex items-center space-x-1.5">
                        <button
                          onClick={() => handleCopy(user.username)}
                          className="p-1.5 rounded-lg text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#10141D] transition-colors"
                          title="Copy Username"
                        >
                          {copiedUser === user.username ? (
                            <Check className="w-4 h-4 text-[#22C55E]" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>

                        {actionButtonLabel && onActionClick && (
                          <button
                            onClick={() => onActionClick(user)}
                            className="px-2.5 py-1 rounded-lg text-xs font-medium bg-[#10141D] hover:bg-[#1C2433] text-[#F8FAFC] border border-[#252B38] transition-colors"
                          >
                            {actionButtonLabel}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {filteredUsers.length > 0 && (
        <div className="p-4 border-t border-[#252B38] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#94A3B8]">
          <div className="flex items-center space-x-2">
            <span>Rows per page:</span>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="bg-[#10141D] text-[#F8FAFC] border border-[#252B38] rounded-lg px-2 py-1 focus:outline-none"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
            <span>
              Showing {Math.min(filteredUsers.length, (currentPage - 1) * pageSize + 1)} -{' '}
              {Math.min(filteredUsers.length, currentPage * pageSize)} of {filteredUsers.length}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="p-1.5 rounded-lg border border-[#252B38] disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#10141D] transition-colors"
              aria-label="Previous page"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-medium text-[#F8FAFC]">
              Page {currentPage} of {totalPages}
            </span>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="p-1.5 rounded-lg border border-[#252B38] disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#10141D] transition-colors"
              aria-label="Next page"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
