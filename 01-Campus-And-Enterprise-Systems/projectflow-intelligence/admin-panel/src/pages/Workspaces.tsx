import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Workspace } from '../types';
import { Layers, Plus, RefreshCw, FolderKanban, ShieldCheck, Calendar, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Workspaces: React.FC = () => {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchWorkspaces = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getWorkspaces();
      setWorkspaces(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load workspaces');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  const handleNameChange = (val: string) => {
    setName(val);
    setSlug(val.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''));
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const created = await api.createWorkspace({ name, slug, description });
      setWorkspaces((prev: Workspace[]) => [created, ...prev]);
      setShowModal(false);
      setName('');
      setSlug('');
      setDescription('');
    } catch (err: any) {
      alert(`Workspace creation failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#292D28] tracking-tight">Tenant Workspaces</h2>
          <p className="text-sm text-[#78866B]">
            Isolated environments separating project portfolios, permissions, and risk telemetry.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchWorkspaces}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#FAFAF7] border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:text-[#292D28] hover:bg-[#EFECE4] transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#56664C]' : ''}`} />
            Refresh
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            Create Workspace
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
          {error}
        </div>
      )}

      {/* Grid of Workspaces */}
      {workspaces.length === 0 ? (
        <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-12 text-center space-y-4">
          <div className="w-12 h-12 mx-auto rounded-full bg-[#56664C]/10 text-[#56664C] flex items-center justify-center">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-[#292D28]">No Workspaces Found</h3>
            <p className="text-xs text-[#5A6258] mt-1 max-w-md mx-auto">
              Workspaces isolate projects and members. Create the primary workspace to initialize your team environment.
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640]"
          >
            <Plus className="w-4 h-4" />
            Create Workspace
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workspaces.map((ws) => (
            <div
              key={ws.id}
              className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl p-6 shadow-sm hover:border-[#56664C] transition-colors flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-lg bg-[#56664C]/10 text-[#56664C] flex items-center justify-center font-bold">
                    <Layers className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-mono font-semibold bg-[#E2E0D8] text-[#5A6258] px-2 py-0.5 rounded">
                    {ws.slug}
                  </span>
                </div>
                <h3 className="text-base font-bold text-[#292D28] mb-1">{ws.name}</h3>
                <p className="text-xs text-[#5A6258] line-clamp-2 leading-relaxed">
                  {ws.description || 'Enterprise project workspace domain.'}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-[#E2E0D8] flex items-center justify-between text-xs text-[#78866B]">
                <div className="flex items-center gap-1.5 font-mono text-[11px]">
                  <Calendar className="w-3.5 h-3.5" />
                  {new Date(ws.createdAt).toLocaleDateString()}
                </div>
                <Link
                  to={`/projects`}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-[#56664C] hover:text-[#485640]"
                >
                  View Projects <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-[#292D28]">Create New Tenant Workspace</h3>
            <p className="text-xs text-[#5A6258]">
              Sets up an isolated tenant scope with independent workflow rules and members.
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Workspace Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Core Engineering"
                  value={name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Slug / URL Identifier
                </label>
                <input
                  type="text"
                  required
                  placeholder="core-engineering"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs font-mono text-[#292D28] focus:outline-none focus:border-[#56664C]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase tracking-wider mb-1">
                  Description (Optional)
                </label>
                <textarea
                  rows={3}
                  placeholder="Primary engineering initiatives and infrastructure projects."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-lg text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3.5 py-1.5 rounded-lg border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:bg-[#EFECE4]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-1.5 rounded-lg bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] disabled:opacity-50"
                >
                  {submitting ? 'Creating...' : 'Create Workspace'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
