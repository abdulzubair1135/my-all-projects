import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Project, Workspace, ProjectStatus, Task, Team, UserProfile } from '../types';
import {
  FolderKanban,
  Plus,
  RefreshCw,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Search,
  ArrowRight,
  Sparkles,
  SlidersHorizontal,
  Users,
  UserCheck
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [updatingProjectId, setUpdatingProjectId] = useState<string | null>(null);

  const [tasks, setTasks] = useState<Task[]>([]);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [selectedWs, setSelectedWs] = useState<string>('');
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [assignedTarget, setAssignedTarget] = useState<string>('UNASSIGNED');
  const [submitting, setSubmitting] = useState(false);
  // Team Details Modal State
  const [viewingTeamProject, setViewingTeamProject] = useState<Project | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [projList, wsList, taskList, teamList] = await Promise.all([
        api.getProjects().catch(() => []),
        api.getWorkspaces().catch(() => []),
        api.getAllTasks().catch(() => []),
        api.getTeams().catch(() => [])
      ]);
      setProjects(projList);
      setWorkspaces(wsList);
      setTasks(taskList);
      setTeams(teamList);

      let userList: UserProfile[] = [];
      try {
        const uRes = await api.getUsers('', 0, 100);
        if (uRes && Array.isArray(uRes.content) && uRes.content.length > 0) {
          userList = uRes.content;
        }
      } catch (e) {}

      if (userList.length === 0) {
        try {
          const teamRes = await api.getTeamMembers();
          if (Array.isArray(teamRes) && teamRes.length > 0) {
            userList = teamRes.map((t: any) => ({
              id: t.id,
              email: t.email,
              fullName: t.fullName || t.email,
              role: t.role || 'MEMBER',
              active: t.active !== false,
              createdAt: t.createdAt || new Date().toISOString()
            }));
          }
        } catch (e) {}
      }
      setUsers(userList);

      if (wsList.length > 0 && !selectedWs) {
        setSelectedWs(wsList[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleNameChange = (val: string) => {
    setName(val);
    const words = val.trim().split(/\s+/);
    if (words.length >= 2) {
      setCode((words[0].substring(0, 3) + '-' + words[1].substring(0, 3)).toUpperCase());
    } else if (val.length >= 3) {
      setCode(val.substring(0, 4).toUpperCase());
    }
  };

  const handleAssignProject = async (projectId: string, assignValue: string) => {
    setUpdatingProjectId(projectId);
    try {
      let patchData: Partial<Project> = {};
      if (assignValue === 'UNASSIGNED') {
        patchData = { assigneeId: null, assigneeName: null, assigneeEmail: null, teamId: null, teamName: null };
      } else if (assignValue.startsWith('TEAM:')) {
        const teamId = assignValue.replace('TEAM:', '');
        const tm = teams.find(t => t.id === teamId);
        patchData = {
          teamId,
          teamName: tm?.name || null,
          assigneeId: null,
          assigneeName: null,
          assigneeEmail: null
        };
      } else if (assignValue.startsWith('USER:')) {
        const userId = assignValue.replace('USER:', '');
        const u = users.find(usr => usr.id === userId);
        patchData = {
          assigneeId: userId,
          assigneeName: u?.fullName || u?.email?.split('@')[0],
          assigneeEmail: u?.email,
          teamId: null,
          teamName: null
        };
      }
      const updated = await api.updateProject(projectId, patchData);
      setProjects(prev => prev.map(p => p.id === projectId ? { ...p, ...updated } : p));
    } catch (err: any) {
      alert(`Assignment update failed: ${err.message}`);
    } finally {
      setUpdatingProjectId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedWs) {
      alert('Please select or create a workspace first');
      return;
    }
    setSubmitting(true);
    try {
      let initialAssigneeId: string | null = null;
      let initialAssigneeName: string | null = null;
      let initialAssigneeEmail: string | null = null;
      let initialTeamId: string | null = null;
      let initialTeamName: string | null = null;
      if (assignedTarget.startsWith('TEAM:')) {
        initialTeamId = assignedTarget.replace('TEAM:', '');
        const tm = teams.find(t => t.id === initialTeamId);
        initialTeamName = tm?.name || null;
      } else if (assignedTarget.startsWith('USER:')) {
        initialAssigneeId = assignedTarget.replace('USER:', '');
        const u = users.find(usr => usr.id === initialAssigneeId);
        initialAssigneeName = u?.fullName || null;
        initialAssigneeEmail = u?.email || null;
      }

      const created = await api.createProject(selectedWs, {
        name: name.trim(),
        code: code.trim().toUpperCase(),
        description: description.trim(),
        targetDate: targetDate || undefined,
        assigneeId: initialAssigneeId,
        assigneeName: initialAssigneeName,
        assigneeEmail: initialAssigneeEmail,
        teamId: initialTeamId,
        teamName: initialTeamName
      });
      setProjects((prev) => [created, ...prev]);
      setShowModal(false);
      setName('');
      setCode('');
      setDescription('');
      setTargetDate('');
      setAssignedTarget('UNASSIGNED');
    } catch (err: any) {
      alert(`Project creation failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusChange = async (projectId: string, newStatus: ProjectStatus) => {
    setUpdatingProjectId(projectId);
    try {
      await api.updateProject(projectId, { status: newStatus });
      setProjects(prev => prev.map(p => {
        if (p.id === projectId) {
          return { ...p, status: newStatus };
        }
        return p;
      }));
    } catch (err: any) {
      alert(`Failed to update project status: ${err.message}`);
    } finally {
      setUpdatingProjectId(null);
    }
  };

  const getHealthBadge = (health: string) => {
    switch (health) {
      case 'ON_TRACK':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#47745A] bg-[#47745A]/10 px-2 py-0.5 rounded-full">
            <CheckCircle2 className="w-3 h-3" /> On Track
          </span>
        );
      case 'AT_RISK':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#D97706] bg-[#D97706]/10 px-2 py-0.5 rounded-full">
            <AlertTriangle className="w-3 h-3" /> At Risk
          </span>
        );
      case 'OFF_TRACK':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#B7473C] bg-[#B7473C]/10 px-2 py-0.5 rounded-full">
            <AlertOctagon className="w-3 h-3" /> Off Track
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#56664C] bg-[#56664C]/10 px-2 py-0.5 rounded-full">
            <CheckCircle2 className="w-3 h-3" /> Stable
          </span>
        );
    }
  };

  const filteredProjects = projects.filter(p => {
    const matchesSearch = !searchQuery.trim() ||
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesStatus = statusFilter === 'ALL' || p.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto select-none">
      {/* Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#292D28] tracking-tight">Project Portfolios</h2>
          <p className="text-sm text-[#78866B]">
            Portfolio governance, milestone delivery targets, and schedule baseline status.
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <button
            onClick={fetchData}
            title="Refresh Directory"
            className="p-2 rounded-xl bg-[#FAFAF7] border border-[#E2E0D8] text-[#5A6258] hover:text-[#292D28] hover:bg-[#EFECE4] transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-[#56664C]' : ''}`} />
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Create Project</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#FAFAF7] p-3 rounded-2xl border border-[#E2E0D8]">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#78866B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search project name, code, description..."
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
          />
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto overflow-x-auto">
          <span className="text-xs font-semibold text-[#78866B] flex items-center gap-1">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            Status:
          </span>
          {[
            { key: 'ALL', label: 'All' },
            { key: 'PLANNING', label: 'Planning' },
            { key: 'IN_PROGRESS', label: 'In Progress' },
            { key: 'COMPLETED', label: 'Completed' },
            { key: 'ON_HOLD', label: 'On Hold' }
          ].map((st) => (
            <button
              key={st.key}
              onClick={() => setStatusFilter(st.key)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                statusFilter === st.key
                  ? 'bg-[#56664C] text-white'
                  : 'bg-[#EFECE4] text-[#5A6258] hover:text-[#292D28]'
              }`}
            >
              {st.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs">
          {error}
        </div>
      )}

      {/* Projects Table */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F4F2E9] border-b border-[#E2E0D8] text-[#5A6258] font-semibold uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3.5">Code & Project</th>
                <th className="px-6 py-3.5">Status (Interactive)</th>
                <th className="px-6 py-3.5">Assigned To (Squad / Person)</th>
                <th className="px-6 py-3.5">Radar Health</th>
                <th className="px-6 py-3.5">Target Baseline</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E0D8] text-[#292D28]">
              {filteredProjects.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-[#5A6258]">
                    <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-[#E2E0D8] text-[#56664C] flex items-center justify-center">
                      <FolderKanban className="w-5 h-5" />
                    </div>
                    No projects found. Click "Create Project" to initialize your first plan.
                  </td>
                </tr>
              ) : (
                filteredProjects.map((p) => {
                  const projectTeams = Array.from(
                    new Set(
                      tasks
                        .filter((t) => t.projectId === p.id && t.teamName)
                        .map((t) => t.teamName as string)
                    )
                  );

                  return (
                    <tr key={p.id} className="hover:bg-[#F4F2E9]/60 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-[#56664C]/10 text-[#56664C] flex items-center justify-center font-mono font-bold text-xs shrink-0">
                            {p.code ? p.code.substring(0, 3) : 'PRJ'}
                          </div>
                          <div>
                            <div className="font-bold text-xs text-[#292D28]">{p.name}</div>
                            <div className="text-[11px] text-[#78866B] font-mono">{p.code}</div>
                            <div className="flex flex-wrap items-center gap-1.5 mt-1">
                              {p.teamName && (
                                <span className="inline-flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded bg-[#56664C]/10 text-[#56664C]">
                                  👥 Team: {p.teamName}
                                </span>
                              )}
                              {p.assigneeName && (
                                <span className="inline-flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded bg-[#EFECE4] text-[#292D28]">
                                  👤 Lead: {p.assigneeName}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {/* Interactive Status Selector */}
                        <select
                          disabled={updatingProjectId === p.id}
                          value={p.status || 'PLANNING'}
                          onChange={(e) => handleStatusChange(p.id, e.target.value as ProjectStatus)}
                          className={`font-mono text-[10px] font-bold px-2 py-1 rounded-lg border border-[#E2E0D8] focus:outline-none ${
                            p.status === 'COMPLETED'
                              ? 'bg-green-100 text-green-800'
                              : p.status === 'IN_PROGRESS'
                              ? 'bg-[#56664C]/15 text-[#56664C]'
                              : p.status === 'ON_HOLD'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          <option value="PLANNING">PLANNING</option>
                          <option value="IN_PROGRESS">IN_PROGRESS</option>
                          <option value="ON_HOLD">ON_HOLD</option>
                          <option value="COMPLETED">COMPLETED</option>
                        </select>
                      </td>
                      <td className="px-6 py-4">
                        <select
                          disabled={updatingProjectId === p.id}
                          value={
                            p.assigneeId
                              ? `USER:${p.assigneeId}`
                              : p.teamId
                              ? `TEAM:${p.teamId}`
                              : 'UNASSIGNED'
                          }
                          onChange={(e) => handleAssignProject(p.id, e.target.value)}
                          className={`text-xs font-semibold px-2.5 py-1.5 rounded-lg border focus:outline-none transition-colors cursor-pointer ${
                            p.assigneeId || p.teamName
                              ? 'bg-[#56664C]/10 text-[#292D28] border-[#56664C]/30 hover:border-[#56664C]'
                              : 'bg-[#FAFAF7] text-[#78866B] border-[#E2E0D8] hover:border-[#56664C]'
                          }`}
                        >
                          <option value="UNASSIGNED">👤 Unassigned (Click to Assign)</option>
                          <optgroup label="── 👥 Squads & Teams ──">
                            {teams.map((tm) => (
                              <option key={tm.id} value={`TEAM:${tm.id}`}>
                                👥 Squad: {tm.name}
                              </option>
                            ))}
                          </optgroup>
                          <optgroup label="── 👤 Persons & Members ──">
                            {users.map((usr) => (
                              <option key={usr.id} value={`USER:${usr.id}`}>
                                👤 Person: {usr.fullName || usr.email}
                              </option>
                            ))}
                          </optgroup>
                        </select>
                      </td>
                      <td className="px-6 py-4">
                        {getHealthBadge(p.health)}
                      </td>
                      <td className="px-6 py-4 font-mono text-[11px] text-[#78866B]">
                        {p.targetDate ? (
                          <div className="flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5 text-[#56664C]" />
                            {new Date(p.targetDate).toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' })}
                          </div>
                        ) : (
                          'Ongoing sprint'
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => setViewingTeamProject(p)}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl border border-[#E2E0D8] bg-[#FAFAF7] hover:bg-[#EFECE4] text-[#56664C] font-bold text-xs transition-colors shadow-xs"
                            title="View Project Team & Active Contributors"
                          >
                            <Users className="w-3.5 h-3.5" />
                            <span>Team Info</span>
                          </button>
                          <Link
                            to={`/tasks?projectId=${p.id}&action=newTask`}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-[#56664C] text-[#F4F2E9] font-bold text-xs hover:bg-[#485640] transition-colors shadow-xs"
                            title="Assign a Squad or Member to a Task in this Project"
                          >
                            <Plus className="w-3.5 h-3.5" />
                            <span>Assign Task</span>
                          </Link>
                          <Link
                            to={`/tasks?projectId=${p.id}`}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl border border-[#E2E0D8] bg-white hover:bg-[#EFECE4] text-[#292D28] font-bold text-xs transition-colors shadow-xs"
                          >
                            <span>Tasks</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-[#292D28]">Create New Project</h3>
            <p className="text-xs text-[#5A6258]">
              Initiates a new project plan within the specified tenant workspace.
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Tenant Workspace
                </label>
                <select
                  required
                  value={selectedWs}
                  onChange={(e) => setSelectedWs(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                >
                  {workspaces.map((ws) => (
                    <option key={ws.id} value={ws.id}>
                      {ws.name} ({ws.slug})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Project Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  placeholder="e.g. Mobile Client Redesign"
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                    Project Code
                  </label>
                  <input
                    type="text"
                    required
                    value={code}
                    onChange={(e) => setCode(e.target.value.toUpperCase())}
                    placeholder="e.g. MOB-APP"
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] font-mono focus:outline-none focus:border-[#56664C]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                    Target Delivery Date
                  </label>
                  <input
                    type="date"
                    value={targetDate}
                    onChange={(e) => setTargetDate(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Assign Project To (Squad or Person)
                </label>
                <select
                  value={assignedTarget}
                  onChange={(e) => setAssignedTarget(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                >
                  <option value="UNASSIGNED">👤 Unassigned</option>
                  <optgroup label="── 👥 Squads & Teams ──">
                    {teams.map((tm) => (
                      <option key={tm.id} value={`TEAM:${tm.id}`}>
                        👥 Squad: {tm.name}
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label="── 👤 Persons & Members ──">
                    {users.map((usr) => (
                      <option key={usr.id} value={`USER:${usr.id}`}>
                        👤 Person: {usr.fullName || usr.email}
                      </option>
                    ))}
                  </optgroup>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Scope & Deliverable Description
                </label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Outline the core deliverables and objectives..."
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C] resize-none"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2.5 rounded-xl border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:bg-[#EFECE4]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 rounded-xl bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm disabled:opacity-50"
                >
                  {submitting ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Team Details Modal */}
      {viewingTeamProject && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-[#E2E0D8] pb-3">
              <div>
                <h3 className="text-base font-bold text-[#292D28] flex items-center gap-2">
                  <span className="font-mono text-xs bg-[#56664C]/10 text-[#56664C] px-2 py-0.5 rounded">
                    {viewingTeamProject.code || 'PRJ'}
                  </span>
                  {viewingTeamProject.name}
                </h3>
                <p className="text-xs text-[#78866B]">Project Team &amp; Work Item Assignment Overview</p>
              </div>
              <button
                type="button"
                onClick={() => setViewingTeamProject(null)}
                className="p-1 rounded-lg hover:bg-[#EFECE4] text-[#5A6258] text-sm"
              >
                ✕
              </button>
            </div>

            {/* Team & Lead Overview */}
            <div className="grid grid-cols-2 gap-3 bg-white p-3.5 rounded-xl border border-[#E2E0D8]">
              <div>
                <span className="text-[10px] font-semibold text-[#78866B] uppercase block">Assigned Team / Squad</span>
                <span className="text-xs font-bold text-[#292D28] mt-0.5 flex items-center gap-1.5">
                  👥 {viewingTeamProject.teamName || 'Unassigned'}
                </span>
              </div>
              <div>
                <span className="text-[10px] font-semibold text-[#78866B] uppercase block">Project Lead / Person</span>
                <span className="text-xs font-bold text-[#292D28] mt-0.5 flex items-center gap-1.5">
                  👤 {viewingTeamProject.assigneeName || 'Unassigned'}
                </span>
              </div>
            </div>

            {/* Tasks & Assigned Contributors */}
            <div>
              <h4 className="text-xs font-bold text-[#5A6258] uppercase tracking-wider mb-2">
                Active Project Tasks &amp; Assignees
              </h4>
              <div className="max-h-56 overflow-y-auto divide-y divide-[#F4F2E9] border border-[#E2E0D8] rounded-xl bg-white p-2">
                {tasks.filter((t) => t.projectId === viewingTeamProject.id).length === 0 ? (
                  <div className="py-4 text-center text-xs text-[#78866B]">
                    No tasks created under this project yet. Click "Assign Task" to create one.
                  </div>
                ) : (
                  tasks
                    .filter((t) => t.projectId === viewingTeamProject.id)
                    .map((t) => (
                      <div key={t.id} className="py-2.5 px-2 flex items-center justify-between hover:bg-[#FAFAF7] rounded-lg">
                        <div className="space-y-0.5">
                          <div className="text-xs font-bold text-[#292D28]">{t.title}</div>
                          <div className="text-[10px] text-[#78866B] flex items-center gap-2">
                            <span>Priority: {t.priority}</span>
                            <span>•</span>
                            <span>Progress: {t.progressPercent || 0}%</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="inline-block text-[11px] font-bold px-2 py-0.5 rounded-md bg-[#56664C]/10 text-[#56664C]">
                            👤 {t.assigneeName || (t.teamName ? '👥 ' + t.teamName : 'Unassigned')}
                          </span>
                          <span className="block text-[9px] font-mono text-[#78866B] uppercase mt-0.5">
                            {t.statusCategory}
                          </span>
                        </div>
                      </div>
                    ))
                )}
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-[#E2E0D8]">
              <Link
                to={`/tasks?projectId=${viewingTeamProject.id}&action=newTask`}
                onClick={() => setViewingTeamProject(null)}
                className="px-3.5 py-2 rounded-xl bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-xs"
              >
                + Assign New Task
              </Link>
              <button
                type="button"
                onClick={() => setViewingTeamProject(null)}
                className="px-4 py-2 rounded-xl border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:bg-[#EFECE4]"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
