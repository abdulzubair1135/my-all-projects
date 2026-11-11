import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Project, Task, TaskPriority, Team, UserProfile } from '../types';
import {
  CheckSquare,
  Plus,
  RefreshCw,
  Calendar,
  AlertCircle,
  Users,
  User,
  Kanban,
  Table as TableIcon,
  Search,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

export const Tasks: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>(searchParams.get('projectId') || '');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // View Mode: Table vs Kanban
  const [viewMode, setViewMode] = useState<'TABLE' | 'KANBAN'>('KANBAN');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPriority, setFilterPriority] = useState<string>('ALL');
  const [updatingTaskId, setUpdatingTaskId] = useState<string | null>(null);

  // Create Task Modal
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TaskPriority>('MEDIUM');
  const [dueDate, setDueDate] = useState('');
  const [assignType, setAssignType] = useState<'USER' | 'TEAM' | 'NONE'>('NONE');
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Create Team Modal
  const [showTeamModal, setShowTeamModal] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');
  const [newTeamDesc, setNewTeamDesc] = useState('');
  const [selectedMemberEmails, setSelectedMemberEmails] = useState<string[]>([]);
  const [teamSubmitting, setTeamSubmitting] = useState(false);
  const [teamSuccessMsg, setTeamSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [prjs, tms] = await Promise.all([
          api.getProjects().catch(() => []),
          api.getTeams().catch(() => [])
        ]);
        setProjects(prjs);
        setTeams(tms);

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

        if (prjs.length > 0 && !selectedProjectId) {
          setSelectedProjectId(prjs[0].id);
        }
      } catch (err: any) {
        console.warn('Failed loading initial data', err);
      }
    }
    loadInitialData();
  }, []);

  const fetchTasks = async (projId: string) => {
    if (!projId) {
      setTasks([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.getProjectTasks(projId);
      setTasks(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load project tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProjectId) {
      fetchTasks(selectedProjectId);
      setSearchParams({ projectId: selectedProjectId });
    }
  }, [selectedProjectId]);

  useEffect(() => {
    if (searchParams.get('action') === 'newTask') {
      setShowModal(true);
      setAssignType('TEAM');
    }
  }, [searchParams]);

  const handleStatusChange = async (taskId: string, newStatus: string) => {
    setUpdatingTaskId(taskId);
    try {
      let progress = 0;
      if (newStatus === 'IN_PROGRESS') progress = 50;
      else if (newStatus === 'REVIEW') progress = 80;
      else if (newStatus === 'DONE') progress = 100;

      await api.updateTaskStatus(taskId, newStatus, progress);
      setTasks(prev => prev.map(t => {
        if (t.id === taskId) {
          return {
            ...t,
            statusCategory: newStatus,
            progressPercent: progress,
            completedAt: newStatus === 'DONE' ? new Date().toISOString() : undefined
          };
        }
        return t;
      }));
    } catch (err: any) {
      alert(`Failed to update status: ${err.message}`);
    } finally {
      setUpdatingTaskId(null);
    }
  };

  const handleAssignTask = async (taskId: string, targetValue: string) => {
    setUpdatingTaskId(taskId);
    try {
      let assigneeId: string | undefined = undefined;
      let assigneeName: string | undefined = undefined;
      let teamId: string | undefined = undefined;
      let teamName: string | undefined = undefined;

      if (targetValue.startsWith('USER:')) {
        const uId = targetValue.substring(5);
        const u = users.find(usr => usr.id === uId);
        assigneeId = uId;
        assigneeName = u ? u.fullName : 'Team Member';
      } else if (targetValue.startsWith('TEAM:')) {
        const tId = targetValue.substring(5);
        const tm = teams.find(t => t.id === tId);
        teamId = tId;
        teamName = tm ? tm.name : 'Squad';
      }

      const updated = await api.updateTask(taskId, {
        assigneeId,
        assigneeName,
        teamId,
        teamName
      });

      setTasks(prev => prev.map(t => {
        if (t.id === taskId) {
          return {
            ...t,
            assigneeId: updated.assigneeId,
            assigneeName: updated.assigneeName,
            teamId: updated.teamId,
            teamName: updated.teamName
          };
        }
        return t;
      }));
    } catch (err: any) {
      alert(`Failed to assign task: ${err.message}`);
    } finally {
      setUpdatingTaskId(null);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProjectId) return;
    setSubmitting(true);
    try {
      let assigneeId: string | undefined;
      let assigneeName: string | undefined;
      let teamId: string | undefined;
      let teamName: string | undefined;

      if (selectedUserId) {
        const found = users.find(u => u.id === selectedUserId);
        assigneeId = selectedUserId;
        assigneeName = found ? found.fullName : undefined;
      }
      if (selectedTeamId) {
        const found = teams.find(t => t.id === selectedTeamId);
        teamId = selectedTeamId;
        teamName = found ? found.name : undefined;
      }

      const newTask = await api.createTask(selectedProjectId, {
        title,
        description,
        priority,
        dueDate: dueDate ? new Date(dueDate).toISOString() : undefined,
        assigneeId,
        assigneeName,
        teamId,
        teamName
      });
      setTasks((prev) => [newTask, ...prev]);
      setShowModal(false);
      setTitle('');
      setDescription('');
      setDueDate('');
      setSelectedUserId('');
      setSelectedTeamId('');
      setSelectedTeamId('');
    } catch (err: any) {
      alert(`Task creation failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTeamName.trim()) return;
    setTeamSubmitting(true);
    try {
      const created = await api.createTeam({
        name: newTeamName.trim(),
        description: newTeamDesc.trim(),
        members: selectedMemberEmails,
        memberEmails: selectedMemberEmails
      } as any);
      setTeams((prev) => [...prev, created]);
      setTeamSuccessMsg(`Team "${created.name}" created with ${selectedMemberEmails.length} member(s)!`);
      setNewTeamName('');
      setNewTeamDesc('');
      setSelectedMemberEmails([]);
      setTimeout(() => {
        setTeamSuccessMsg(null);
        setShowTeamModal(false);
      }, 1500);
    } catch (err: any) {
      alert(`Team creation failed: ${err.message}`);
    } finally {
      setTeamSubmitting(false);
    }
  };

  const getPriorityBadge = (p: TaskPriority) => {
    switch (p) {
      case 'CRITICAL':
        return <span className="bg-[#C84B31]/15 text-[#C84B31] px-2 py-0.5 rounded text-[10px] font-mono font-bold">CRITICAL</span>;
      case 'HIGH':
        return <span className="bg-[#D97706]/15 text-[#D97706] px-2 py-0.5 rounded text-[10px] font-mono font-bold">HIGH</span>;
      case 'MEDIUM':
        return <span className="bg-[#56664C]/15 text-[#56664C] px-2 py-0.5 rounded text-[10px] font-mono font-semibold">MEDIUM</span>;
      default:
        return <span className="bg-[#E2E0D8] text-[#5A6258] px-2 py-0.5 rounded text-[10px] font-mono">LOW</span>;
    }
  };

  // Filter tasks
  const filteredTasks = tasks.filter(t => {
    const matchesSearch = !searchQuery.trim() ||
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.description && t.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (t.assigneeName && t.assigneeName.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (t.teamName && t.teamName.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesPriority = filterPriority === 'ALL' || t.priority === filterPriority;
    return matchesSearch && matchesPriority;
  });

  const columns = [
    { key: 'TODO', label: 'To Do (Backlog)', bg: 'bg-[#F4F2E9]/70', border: 'border-[#E2E0D8]' },
    { key: 'IN_PROGRESS', label: 'In Active Sprint', bg: 'bg-amber-50/50', border: 'border-amber-200/80' },
    { key: 'REVIEW', label: 'Review & Verification', bg: 'bg-blue-50/50', border: 'border-blue-200/80' },
    { key: 'DONE', label: 'Completed / Delivered', bg: 'bg-green-50/50', border: 'border-green-200/80' }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto select-none">
      {/* Title & Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#292D28] tracking-tight">Task Operations & Kanban</h2>
          <p className="text-sm text-[#78866B]">
            Work item scheduling, status tracking, and deliverable sprint pipeline.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Project Selector */}
          {projects.length > 0 && (
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs font-semibold text-[#292D28] focus:outline-none focus:border-[#56664C]"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  [{p.code}] {p.name}
                </option>
              ))}
            </select>
          )}

          {/* View Mode Switcher */}
          <div className="flex bg-[#EFECE4] p-1 rounded-xl border border-[#E2E0D8]">
            <button
              onClick={() => setViewMode('KANBAN')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                viewMode === 'KANBAN'
                  ? 'bg-white text-[#292D28] shadow-xs'
                  : 'text-[#5A6258] hover:text-[#292D28]'
              }`}
            >
              <Kanban className="w-3.5 h-3.5" />
              <span>Kanban</span>
            </button>
            <button
              onClick={() => setViewMode('TABLE')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                viewMode === 'TABLE'
                  ? 'bg-white text-[#292D28] shadow-xs'
                  : 'text-[#5A6258] hover:text-[#292D28]'
              }`}
            >
              <TableIcon className="w-3.5 h-3.5" />
              <span>Table</span>
            </button>
          </div>

          <button
            onClick={() => fetchTasks(selectedProjectId)}
            title="Refresh Tasks"
            className="p-2 rounded-xl bg-[#FAFAF7] border border-[#E2E0D8] text-[#5A6258] hover:text-[#292D28] hover:bg-[#EFECE4] transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-[#56664C]' : ''}`} />
          </button>

          <button
            onClick={() => setShowTeamModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#EFECE4] border border-[#E2E0D8] text-xs font-semibold text-[#56664C] hover:bg-[#E2E0D8] transition-colors shadow-xs"
          >
            <Users className="w-3.5 h-3.5" />
            <span>+ Create Team</span>
          </button>

          <button
            disabled={!selectedProjectId}
            onClick={() => setShowModal(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            <span>Add Task</span>
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
            placeholder="Search tasks, squads, assignees..."
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
          />
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <span className="text-xs font-semibold text-[#78866B]">Priority:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((p) => (
            <button
              key={p}
              onClick={() => setFilterPriority(p)}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all ${
                filterPriority === p
                  ? 'bg-[#56664C] text-white'
                  : 'bg-[#EFECE4] text-[#5A6258] hover:text-[#292D28]'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{error}</span>
        </div>
      )}

      {/* VIEW 1: KANBAN BOARD VIEW */}
      {viewMode === 'KANBAN' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {columns.map((col) => {
            const colTasks = filteredTasks.filter(t => (t.statusCategory || 'TODO') === col.key);

            return (
              <div
                key={col.key}
                className={`bg-[#FAFAF7] border ${col.border} rounded-2xl p-4 flex flex-col min-h-[500px] shadow-xs`}
              >
                {/* Column Header */}
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#E2E0D8]">
                  <h3 className="text-xs font-bold text-[#292D28] uppercase tracking-wider">
                    {col.label}
                  </h3>
                  <span className="text-[10px] font-mono font-bold bg-[#E2E0D8] text-[#5A6258] px-2 py-0.5 rounded-full">
                    {colTasks.length}
                  </span>
                </div>

                {/* Cards */}
                <div className="flex-1 space-y-3 overflow-y-auto">
                  {colTasks.length === 0 ? (
                    <div className="py-12 text-center text-xs text-[#78866B] italic">
                      No tasks in this lane
                    </div>
                  ) : (
                    colTasks.map((t) => (
                      <div
                        key={t.id}
                        className="bg-white border border-[#E2E0D8] hover:border-[#56664C] rounded-xl p-3.5 shadow-xs transition-all space-y-2.5"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className="font-bold text-xs text-[#292D28] leading-snug">
                            {t.title}
                          </span>
                          {getPriorityBadge(t.priority)}
                        </div>

                        {t.description && (
                          <p className="text-[11px] text-[#5A6258] line-clamp-2 leading-relaxed">
                            {t.description}
                          </p>
                        )}

                        {/* Interactive Assignee / Squad Selector */}
                        <div className="pt-0.5">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-[9px] font-bold text-[#78866B] uppercase tracking-wider">
                              Assigned To
                            </span>
                            {updatingTaskId === t.id && (
                              <span className="text-[9px] font-mono text-[#56664C] animate-pulse">
                                Syncing...
                              </span>
                            )}
                          </div>
                          <select
                            disabled={updatingTaskId === t.id}
                            value={
                              t.assigneeId
                                ? `USER:${t.assigneeId}`
                                : t.teamId
                                ? `TEAM:${t.teamId}`
                                : 'UNASSIGNED'
                            }
                            onChange={(e) => handleAssignTask(t.id, e.target.value)}
                            className={`w-full text-[11px] font-semibold px-2 py-1.5 rounded-lg border focus:outline-none transition-colors cursor-pointer ${
                              t.assigneeId || t.teamName
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
                            <optgroup label="── 👤 Team Members (Persons) ──">
                              {users.map((u) => (
                                <option key={u.id} value={`USER:${u.id}`}>
                                  👤 {u.fullName} ({u.email})
                                </option>
                              ))}
                            </optgroup>
                          </select>
                        </div>

                        {/* Progress Bar & Due Date */}
                        <div className="pt-2 border-t border-[#E2E0D8]/60 flex items-center justify-between text-[10px] text-[#78866B]">
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            <span>
                              {t.dueDate ? new Date(t.dueDate).toLocaleDateString([], { month: 'short', day: 'numeric' }) : 'No due date'}
                            </span>
                          </div>
                          <span className="font-mono font-semibold">{t.progressPercent || 0}%</span>
                        </div>

                        {/* Quick Status Movement Arrows */}
                        <div className="pt-1.5 flex items-center justify-between">
                          {col.key !== 'TODO' ? (
                            <button
                              disabled={updatingTaskId === t.id}
                              onClick={() => {
                                const prev = col.key === 'DONE' ? 'REVIEW' : col.key === 'REVIEW' ? 'IN_PROGRESS' : 'TODO';
                                handleStatusChange(t.id, prev);
                              }}
                              className="p-1 rounded hover:bg-[#F4F2E9] text-[#5A6258] transition-colors"
                              title="Move Backward"
                            >
                              <ArrowLeft className="w-3.5 h-3.5" />
                            </button>
                          ) : <div />}

                          {col.key !== 'DONE' ? (
                            <button
                              disabled={updatingTaskId === t.id}
                              onClick={() => {
                                const next = col.key === 'TODO' ? 'IN_PROGRESS' : col.key === 'IN_PROGRESS' ? 'REVIEW' : 'DONE';
                                handleStatusChange(t.id, next);
                              }}
                              className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#56664C]/10 text-[#56664C] text-[10px] font-semibold hover:bg-[#56664C]/20 transition-colors"
                              title="Move Forward"
                            >
                              <span>Next</span>
                              <ArrowRight className="w-3 h-3" />
                            </button>
                          ) : (
                            <span className="text-[10px] font-semibold text-[#47745A] flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" /> Done
                            </span>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* VIEW 2: INTERACTIVE TABLE VIEW */
        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F4F2E9] border-b border-[#E2E0D8] text-[#5A6258] font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3.5">Title & Deliverables</th>
                  <th className="px-6 py-3.5">Assigned To</th>
                  <th className="px-6 py-3.5">Priority</th>
                  <th className="px-6 py-3.5">Status (Interactive)</th>
                  <th className="px-6 py-3.5">Progress</th>
                  <th className="px-6 py-3.5">Due Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2E0D8] text-[#292D28]">
                {filteredTasks.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-[#5A6258]">
                      <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-[#E2E0D8] text-[#56664C] flex items-center justify-center">
                        <CheckSquare className="w-5 h-5" />
                      </div>
                      No matching tasks found.
                    </td>
                  </tr>
                ) : (
                  filteredTasks.map((t) => (
                    <tr key={t.id} className="hover:bg-[#F4F2E9]/60 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-[#292D28]">{t.title}</div>
                        {t.description && (
                          <div className="text-[11px] text-[#78866B] line-clamp-1">{t.description}</div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <select
                          disabled={updatingTaskId === t.id}
                          value={
                            t.assigneeId
                              ? `USER:${t.assigneeId}`
                              : t.teamId
                              ? `TEAM:${t.teamId}`
                              : 'UNASSIGNED'
                          }
                          onChange={(e) => handleAssignTask(t.id, e.target.value)}
                          className={`text-[11px] font-semibold px-2.5 py-1.5 rounded-lg border focus:outline-none transition-colors cursor-pointer ${
                            t.assigneeId || t.teamName
                              ? 'bg-[#56664C]/10 text-[#292D28] border-[#56664C]/30'
                              : 'bg-white text-[#78866B] border-[#E2E0D8]'
                          }`}
                        >
                          <option value="UNASSIGNED">👤 Unassigned</option>
                          <optgroup label="── 👥 Squads & Teams ──">
                            {teams.map((tm) => (
                              <option key={tm.id} value={`TEAM:${tm.id}`}>
                                👥 Squad: {tm.name}
                              </option>
                            ))}
                          </optgroup>
                          <optgroup label="── 👤 Team Members (Persons) ──">
                            {users.map((u) => (
                              <option key={u.id} value={`USER:${u.id}`}>
                                👤 {u.fullName} ({u.email})
                              </option>
                            ))}
                          </optgroup>
                        </select>
                      </td>
                      <td className="px-6 py-4">{getPriorityBadge(t.priority)}</td>
                      <td className="px-6 py-4">
                        {/* Interactive Status Selector */}
                        <select
                          disabled={updatingTaskId === t.id}
                          value={t.statusCategory || 'TODO'}
                          onChange={(e) => handleStatusChange(t.id, e.target.value)}
                          className={`font-mono text-[10px] font-bold px-2 py-1 rounded-lg border border-[#E2E0D8] focus:outline-none ${
                            t.statusCategory === 'DONE'
                              ? 'bg-green-100 text-green-800'
                              : t.statusCategory === 'IN_PROGRESS'
                              ? 'bg-amber-100 text-amber-800'
                              : t.statusCategory === 'REVIEW'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          <option value="TODO">TODO</option>
                          <option value="IN_PROGRESS">IN_PROGRESS</option>
                          <option value="REVIEW">REVIEW</option>
                          <option value="DONE">DONE</option>
                        </select>
                      </td>
                      <td className="px-6 py-4">
                        <div className="w-24 bg-[#E2E0D8] rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-[#56664C] h-1.5 rounded-full"
                            style={{ width: `${t.progressPercent || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-[10px] font-mono text-[#78866B]">{t.progressPercent || 0}%</span>
                      </td>
                      <td className="px-6 py-4 font-mono text-[11px] text-[#78866B]">
                        {t.dueDate ? (
                          <div className="flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5" />
                            {new Date(t.dueDate).toLocaleDateString()}
                          </div>
                        ) : (
                          'No deadline'
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CREATE TASK MODAL */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-[#292D28]">Add New Project Task</h3>

            <form onSubmit={handleCreateTask} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">Task Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Implement Mobile Push Notification Handler"
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">Deliverables & Specs</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Explicit acceptance criteria..."
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C] resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">Priority Level</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as TaskPriority)}
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">Delivery Due Date</label>
                  <input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                  />
                </div>
              </div>

              {/* Assignment: Person & Group */}
              <div className="space-y-3 pt-1">
                <div>
                  <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">
                    Assign to Person (Optional)
                  </label>
                  <select
                    value={selectedUserId}
                    onChange={(e) => setSelectedUserId(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                  >
                    <option value="">Unassigned (None)</option>
                    {users.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.fullName} ({u.role})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">
                    Assign to Group (Optional)
                  </label>
                  <select
                    value={selectedTeamId}
                    onChange={(e) => setSelectedTeamId(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                  >
                    <option value="">Unassigned (None)</option>
                    {teams.map((tm) => (
                      <option key={tm.id} value={tm.id}>
                        {tm.name}
                      </option>
                    ))}
                  </select>
                </div>
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
                  {submitting ? 'Creating...' : 'Create & Dispatch'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CREATE TEAM MODAL */}
      {showTeamModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-[#292D28]">Create Team</h3>
                <p className="text-[11px] text-[#78866B]">Create a cross-functional squad and assign members</p>
              </div>
              <button
                type="button"
                onClick={() => setShowTeamModal(false)}
                className="p-1 rounded-lg hover:bg-[#EFECE4] text-[#5A6258] text-sm"
              >
                ✕
              </button>
            </div>

            {teamSuccessMsg && (
              <div className="p-3 bg-green-50 border border-green-200 text-green-800 text-xs rounded-xl font-semibold flex items-center gap-2">
                <span>✓</span> {teamSuccessMsg}
              </div>
            )}

            <form onSubmit={handleCreateTeam} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">Team Name</label>
                <input
                  type="text"
                  required
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                  placeholder="e.g. Core Engineering, Mobile Guild, QA Team"
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">Domain & Description</label>
                <textarea
                  rows={2}
                  value={newTeamDesc}
                  onChange={(e) => setNewTeamDesc(e.target.value)}
                  placeholder="Primary sprint focus, core services, and responsibilities..."
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C] resize-none"
                />
              </div>

              {/* Team Members Selection */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-semibold text-[#5A6258] uppercase">
                    Select Team Members ({selectedMemberEmails.length} selected)
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      if (selectedMemberEmails.length === users.length) {
                        setSelectedMemberEmails([]);
                      } else {
                        setSelectedMemberEmails(users.map(u => u.email).filter(Boolean));
                      }
                    }}
                    className="text-[11px] text-[#56664C] hover:underline font-semibold"
                  >
                    {selectedMemberEmails.length === users.length ? 'Deselect All' : 'Select All'}
                  </button>
                </div>

                <div className="max-h-44 overflow-y-auto border border-[#E2E0D8] rounded-xl bg-white p-2 divide-y divide-[#F4F2E9]">
                  {users.length === 0 ? (
                    <div className="py-3 text-center text-xs text-[#78866B]">No users found to add.</div>
                  ) : (
                    users.map((u) => {
                      const isSelected = selectedMemberEmails.includes(u.email);
                      return (
                        <label
                          key={u.id}
                          className="flex items-center justify-between py-2 px-2 hover:bg-[#FAFAF7] rounded-lg cursor-pointer transition-colors"
                        >
                          <div className="flex items-center gap-2.5">
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedMemberEmails(prev => [...prev, u.email]);
                                } else {
                                  setSelectedMemberEmails(prev => prev.filter(em => em !== u.email));
                                }
                              }}
                              className="rounded border-[#E2E0D8] text-[#56664C] focus:ring-[#56664C]"
                            />
                            <div>
                              <div className="text-xs font-bold text-[#292D28]">{u.fullName || u.email}</div>
                              <div className="text-[10px] text-[#78866B] font-mono">{u.email}</div>
                            </div>
                          </div>
                          <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-[#EFECE4] text-[#5A6258]">
                            {u.role || 'MEMBER'}
                          </span>
                        </label>
                      );
                    })
                  )}
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowTeamModal(false)}
                  className="flex-1 py-2.5 rounded-xl border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:bg-[#EFECE4]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={teamSubmitting}
                  className="flex-1 py-2.5 rounded-xl bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm disabled:opacity-50"
                >
                  {teamSubmitting ? 'Creating Team...' : 'Create Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
