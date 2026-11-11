import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api/client';
import { UserProfile, Role } from '../types';
import { useAuth } from '../context/AuthContext';
import { Discussions } from './Discussions';
import {
  Users,
  Search,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Edit3,
  UserPlus,
  PowerOff,
  Power,
  X,
  Mail,
  User,
  Filter,
  MessageSquare
} from 'lucide-react';

export const UserManagement: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get('tab');
  const [activeTab, setActiveTab] = useState<'members' | 'discussions'>(
    tabParam === 'discussions' ? 'discussions' : 'members'
  );
  const [targetChatEmail, setTargetChatEmail] = useState<string | undefined>(undefined);
  const { user: currentUser } = useAuth();

  const [users, setUsers] = useState<UserProfile[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Edit Role Modal State
  const [selectedUser, setSelectedUser] = useState<UserProfile | null>(null);
  const [newRole, setNewRole] = useState<Role>('MEMBER');
  const [updatingRole, setUpdatingRole] = useState(false);

  // Create User Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createEmail, setCreateEmail] = useState('');
  const [createFullName, setCreateFullName] = useState('');
  const [createRole, setCreateRole] = useState<Role>('MEMBER');
  const [creating, setCreating] = useState(false);

  // Toggle Status Loading State
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const fetchUsers = async () => {
    setError(null);
    try {
      const resp = await api.getUsers(query, 0, 100);
      setUsers(resp.content || []);
      setTotal(resp.totalElements || (resp.content ? resp.content.length : 0));
    } catch (err: any) {
      setError(err.message || 'Failed to fetch users');
      setUsers([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
    const interval = setInterval(() => {
      fetchUsers();
    }, 10000);
    return () => clearInterval(interval);
  }, [query]);

  const handleRoleChange = async () => {
    if (!selectedUser) return;
    setUpdatingRole(true);
    try {
      const updated = await api.updateUserRole(selectedUser.id, newRole);
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? { ...u, role: updated.role } : u)));
      setSelectedUser(null);
      setSuccessMessage(`Role for ${selectedUser.email} successfully updated to ${newRole}`);
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: any) {
      alert(`Role change failed: ${err.message}`);
    } finally {
      setUpdatingRole(false);
    }
  };

  const handleToggleStatus = async (user: UserProfile) => {
    const nextStatus = !user.active;
    const actionLabel = nextStatus ? 'activate' : 'deactivate';
    if (!confirm(`Are you sure you want to ${actionLabel} account for ${user.email}?`)) {
      return;
    }
    setTogglingId(user.id);
    try {
      const updated = await api.updateUserStatus(user.id, nextStatus);
      setUsers((prev) => prev.map((u) => (u.id === user.id ? { ...u, active: updated.active } : u)));
      setSuccessMessage(`User ${user.email} has been ${nextStatus ? 'activated' : 'deactivated'}.`);
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: any) {
      alert(`Failed to update status: ${err.message}`);
    } finally {
      setTogglingId(null);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createEmail.trim()) return;
    setCreating(true);
    try {
      const created = await api.createUser({
        email: createEmail.trim(),
        fullName: createFullName.trim() || createEmail.trim().split('@')[0],
        role: createRole
      });
      setShowCreateModal(false);
      setCreateEmail('');
      setCreateFullName('');
      setCreateRole('MEMBER');
      setSuccessMessage(`User ${created.email} invited successfully with ${created.role} privileges.`);
      setTimeout(() => setSuccessMessage(null), 4000);
      await fetchUsers();
    } catch (err: any) {
      alert(`User creation failed: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const filteredUsers = users.filter((u) => {
    if (roleFilter !== 'ALL' && u.role !== roleFilter) return false;
    if (statusFilter === 'ACTIVE' && !u.active) return false;
    if (statusFilter === 'DEACTIVATED' && u.active) return false;
    return true;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#292D28] tracking-tight">Persons & Groups</h2>
          <p className="text-sm text-[#78866B]">
            Enterprise person directory, role-based access control, group discussions, and real-time team chats in one unified center.
          </p>
        </div>
        {activeTab === 'members' && (
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm"
            >
              <UserPlus className="w-4 h-4" />
              Add Person
            </button>
            <button
              onClick={fetchUsers}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#FAFAF7] border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:text-[#292D28] hover:bg-[#EFECE4] transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#56664C]' : ''}`} />
              Refresh
            </button>
          </div>
        )}
      </div>

      {/* Unified Tab Navigation */}
      <div className="flex border-b border-[#E2E0D8] bg-[#FAFAF7] px-4 pt-2 gap-4 rounded-xl border border-[#E2E0D8] shadow-xs">
        <button
          onClick={() => {
            setActiveTab('members');
            setSearchParams({});
          }}
          className={`pb-3 text-xs sm:text-sm font-bold flex items-center gap-2 border-b-2 transition-all ${
            activeTab === 'members'
              ? 'border-[#56664C] text-[#56664C]'
              : 'border-transparent text-[#78866B] hover:text-[#292D28]'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>👥 Persons & RBAC</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-[#EFECE4] text-[#5A6258] font-bold">{total}</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('discussions');
            setSearchParams({ tab: 'discussions' });
          }}
          className={`pb-3 text-xs sm:text-sm font-bold flex items-center gap-2 border-b-2 transition-all ${
            activeTab === 'discussions'
              ? 'border-[#56664C] text-[#56664C]'
              : 'border-transparent text-[#78866B] hover:text-[#292D28]'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>💬 Groups & Discussions</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-[#56664C] text-white font-bold animate-pulse">LIVE</span>
        </button>
      </div>

      {activeTab === 'discussions' ? (
        <div className="bg-white rounded-2xl border border-[#E2E0D8] overflow-hidden shadow-sm">
          <Discussions initialMemberEmail={targetChatEmail} />
        </div>
      ) : (
        <>

      {successMessage && (
        <div className="p-3.5 rounded-lg bg-[#56664C]/10 border border-[#56664C]/30 text-[#56664C] text-xs font-semibold flex items-center justify-between">
          <span>{successMessage}</span>
          <button onClick={() => setSuccessMessage(null)} className="text-[#56664C] hover:opacity-75">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {error && (
        <div className="p-3.5 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
          {error}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-[#78866B] absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search users by name or email..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs text-[#292D28] focus:outline-none focus:border-[#56664C] focus:ring-1 focus:ring-[#56664C]"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-[#5A6258] font-semibold">
            <Filter className="w-3.5 h-3.5 text-[#78866B]" />
            Role:
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-white border border-[#E2E0D8] rounded-lg text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
            >
              <option value="ALL">All Roles</option>
              <option value="ADMINISTRATOR">ADMINISTRATOR</option>
              <option value="MANAGER">MANAGER</option>
              <option value="MEMBER">MEMBER</option>
              <option value="VIEWER">VIEWER</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-[#5A6258] font-semibold">
            Status:
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-white border border-[#E2E0D8] rounded-lg text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
            >
              <option value="ALL">All Status</option>
              <option value="ACTIVE">Active Only</option>
              <option value="DEACTIVATED">Deactivated Only</option>
            </select>
          </div>

          <div className="text-xs font-medium text-[#78866B] pl-2">
            {filteredUsers.length} of {total} accounts
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F4F2E9] border-b border-[#E2E0D8] text-[#5A6258] font-semibold uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3.5">Person &amp; Presence</th>
                <th className="px-6 py-3.5">Global Role</th>
                <th className="px-6 py-3.5">Account Status</th>
                <th className="px-6 py-3.5">Registered</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E0D8] text-[#292D28]">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-[#5A6258]">
                    <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-[#E2E0D8] text-[#56664C] flex items-center justify-center">
                      <Users className="w-5 h-5" />
                    </div>
                    No user accounts match current filters.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-[#F4F2E9]/60 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <div className="w-8 h-8 rounded-full bg-[#E2E0D8] text-[#56664C] flex items-center justify-center font-bold text-xs">
                            {u.fullName ? u.fullName.charAt(0).toUpperCase() : u.email.charAt(0).toUpperCase()}
                          </div>
                          {/* Live Online Badge Indicator */}
                          {(() => {
                            const isUserOnline = !!u.isOnline || (!!currentUser?.email && u.email?.toLowerCase() === currentUser.email.toLowerCase());
                            return (
                              <span
                                className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-white ${
                                  isUserOnline ? 'bg-emerald-500' : 'bg-gray-300'
                                }`}
                                title={isUserOnline ? 'Online now' : 'Offline'}
                              />
                            );
                          })()}
                        </div>
                        <div>
                          <div className="font-semibold text-[#292D28] flex items-center gap-2">
                            <span>{u.fullName || 'Unnamed User'}</span>
                            {(!!u.isOnline || (!!currentUser?.email && u.email?.toLowerCase() === currentUser.email.toLowerCase())) && (
                              <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded font-semibold border border-emerald-200">
                                LIVE
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-[#78866B] font-mono">{u.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-semibold ${
                          u.role === 'ADMINISTRATOR'
                            ? 'bg-[#56664C]/15 text-[#56664C]'
                            : u.role === 'MANAGER'
                            ? 'bg-[#78866B]/20 text-[#56664C]'
                            : 'bg-[#E2E0D8] text-[#5A6258]'
                        }`}
                      >
                        <ShieldCheck className="w-3 h-3" />
                        {u.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {u.active ? (
                        <span className="inline-flex items-center gap-1 text-[11px] text-[#56664C] font-semibold">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] text-[#C84B31] font-semibold">
                          <XCircle className="w-3.5 h-3.5" /> Deactivated
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 font-mono text-[11px] text-[#78866B]">
                      {u.createdAt ? new Date(u.createdAt).toLocaleDateString() : 'Initial Setup'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="inline-flex items-center gap-2">
                        <button
                          onClick={() => {
                            setTargetChatEmail(u.email);
                            setActiveTab('discussions');
                            setSearchParams({ tab: 'discussions' });
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-[#56664C]/30 bg-[#56664C]/10 hover:bg-[#56664C] hover:text-[#F4F2E9] text-[#56664C] font-semibold text-xs transition-colors"
                          title="Open live chat with team member"
                        >
                          <MessageSquare className="w-3 h-3" />
                          Chat
                        </button>

                        <button
                          onClick={() => {
                            setSelectedUser(u);
                            setNewRole(u.role);
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-[#E2E0D8] bg-white hover:bg-[#EFECE4] text-[#292D28] font-semibold text-xs transition-colors"
                        >
                          <Edit3 className="w-3 h-3 text-[#56664C]" />
                          Role
                        </button>

                        <button
                          disabled={togglingId === u.id}
                          onClick={() => handleToggleStatus(u)}
                          className={`inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border text-xs font-semibold transition-colors ${
                            u.active
                              ? 'border-red-200 bg-red-50 text-red-700 hover:bg-red-100'
                              : 'border-emerald-200 bg-emerald-50 text-emerald-800 hover:bg-emerald-100'
                          }`}
                        >
                          {u.active ? (
                            <>
                              <PowerOff className="w-3 h-3 text-red-600" />
                              Deactivate
                            </>
                          ) : (
                            <>
                              <Power className="w-3 h-3 text-emerald-600" />
                              Activate
                            </>
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit Role Modal */}
      {selectedUser && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl max-w-sm w-full p-6 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-[#292D28]">Edit Global User Role</h3>
            <p className="text-xs text-[#5A6258]">
              Assigning new privileges for <span className="font-semibold text-[#292D28]">{selectedUser.email}</span>.
            </p>

            <div>
              <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                Select Role
              </label>
              <select
                value={newRole}
                onChange={(e) => setNewRole(e.target.value as Role)}
                className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
              >
                <option value="ADMINISTRATOR">ADMINISTRATOR (Full platform control)</option>
                <option value="MANAGER">MANAGER (Project & scenario authority)</option>
                <option value="MEMBER">MEMBER (Standard task contributor)</option>
                <option value="VIEWER">VIEWER (Read-only observer)</option>
              </select>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setSelectedUser(null)}
                className="px-3.5 py-1.5 rounded-lg border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:bg-[#EFECE4]"
              >
                Cancel
              </button>
              <button
                disabled={updatingRole}
                onClick={handleRoleChange}
                className="px-4 py-1.5 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] disabled:opacity-50"
              >
                {updatingRole ? 'Saving...' : 'Apply Role'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Invite / Create User Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-[#292D28] flex items-center gap-2">
                <UserPlus className="w-5 h-5 text-[#56664C]" />
                Invite New Team Member
              </h3>
              <button onClick={() => setShowCreateModal(false)} className="text-[#5A6258] hover:text-[#292D28]">
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-[#5A6258]">
              Add a new member to the organization directory. They will be granted immediate access.
            </p>

            <form onSubmit={handleCreateUser} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Email Address *
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#78866B] absolute left-3 top-2.5" />
                  <input
                    type="email"
                    required
                    placeholder="teammate@company.com"
                    value={createEmail}
                    onChange={(e) => setCreateEmail(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-[#78866B] absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="e.g. Sarah Jenkins"
                    value={createFullName}
                    onChange={(e) => setCreateFullName(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Privilege Role
                </label>
                <select
                  value={createRole}
                  onChange={(e) => setCreateRole(e.target.value as Role)}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
                >
                  <option value="ADMINISTRATOR">ADMINISTRATOR (Full platform control)</option>
                  <option value="MANAGER">MANAGER (Project & scenario authority)</option>
                  <option value="MEMBER">MEMBER (Standard task contributor)</option>
                  <option value="VIEWER">VIEWER (Read-only observer)</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3.5 py-1.5 rounded-lg border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:bg-[#EFECE4]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-1.5 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] disabled:opacity-50"
                >
                  {creating ? 'Inviting...' : 'Send Invitation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
        </>
      )}
    </div>
  );
};
