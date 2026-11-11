import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  MessageSquare,
  Users,
  Send,
  Plus,
  Hash,
  User,
  ShieldCheck,
  Search,
  CheckCheck
} from 'lucide-react';
import { api } from '../api/client';

interface ChatGroup {
  id: string;
  name: string;
  description?: string;
  channel: string;
  members?: string[];
  createdBy?: string;
}

interface TeamMember {
  id: string;
  fullName: string;
  email: string;
  role: string;
  isOnline: boolean;
  assignedTasksCount?: number;
}

interface ChatMessage {
  id: string;
  channel: string;
  senderName: string;
  senderEmail: string;
  senderRole?: string;
  content: string;
  messageType?: string;
  createdAt: string;
  seen?: boolean;
  seenBy?: string[];
  seenAt?: string;
  status?: string;
  reactions?: Record<string, string[]>;
}

interface DiscussionsProps {
  initialChannel?: string;
  initialMemberEmail?: string;
}

const formatMessageTime = (dateStr?: string) => {
  if (!dateStr) return '';
  try {
    let clean = dateStr.trim();
    if (!clean.includes('T') && clean.includes(' ')) {
      clean = clean.replace(' ', 'T');
    }
    if (!clean.endsWith('Z') && !clean.includes('+') && !clean.includes('-')) {
      clean = clean + 'Z';
    }
    const d = new Date(clean);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
  } catch {
    return '';
  }
};

export const Discussions: React.FC<DiscussionsProps> = ({ initialChannel, initialMemberEmail }) => {
  const { user } = useAuth();

  const [groups, setGroups] = useState<ChatGroup[]>([]);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [activeChannel, setActiveChannel] = useState<string>(initialChannel || 'general');
  const [activeTitle, setActiveTitle] = useState<string>('General Group');
  const [activeSubtitle, setActiveSubtitle] = useState<string>('Organization-wide channel');
  const [activeIsDirect, setActiveIsDirect] = useState<boolean>(false);
  const [activeOnline, setActiveOnline] = useState<boolean>(false);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [filterTab, setFilterTab] = useState<'ALL' | 'DIRECT' | 'GROUPS'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Create Group Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupDesc, setNewGroupDesc] = useState('');
  const [selectedEmails, setSelectedEmails] = useState<string[]>([]);
  const [creatingGroup, setCreatingGroup] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadChannelsAndMembers = async () => {
    try {
      const [gList, mList] = await Promise.all([
        api.getChatGroups().catch(() => []),
        api.getTeamMembers().catch(() => [])
      ]);
      setGroups(gList || []);
      setMembers(mList || []);

      if (initialMemberEmail && mList && mList.length > 0) {
        const found = mList.find((m: any) => m.email?.toLowerCase() === initialMemberEmail.toLowerCase());
        if (found) {
          openDirectChat(found);
        }
      }
    } catch (err) {
      console.warn('Failed loading chat channels', err);
    }
  };

  const loadMessages = async (channel: string) => {
    try {
      const msgs = await api.getChatMessages(channel);
      setMessages(msgs || []);
    } catch (err) {
      console.warn('Failed loading messages', err);
    }
  };

  useEffect(() => {
    loadChannelsAndMembers();
    const interval = setInterval(() => {
      loadChannelsAndMembers();
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    loadMessages(activeChannel);
    const interval = setInterval(() => {
      loadMessages(activeChannel);
    }, 4000);
    return () => clearInterval(interval);
  }, [activeChannel]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || sending) return;

    const content = newMessage.trim();
    setNewMessage('');
    setSending(true);

    try {
      await api.sendChatMessage({
        channel: activeChannel,
        content,
        messageType: 'TEXT',
        senderName: user?.fullName || 'Administrator',
        senderEmail: user?.email || 'admin@projectflow.io',
        senderRole: user?.role || 'ADMINISTRATOR'
      });
      await loadMessages(activeChannel);
    } catch (err) {
      console.error('Failed to send message', err);
    } finally {
      setSending(false);
    }
  };

  const openGroupChat = (g: ChatGroup) => {
    setActiveChannel(g.channel);
    setActiveTitle(g.name);
    setActiveSubtitle(g.description || `#${g.channel}`);
    setActiveIsDirect(false);
    setActiveOnline(false);
  };

  const openDirectChat = (m: TeamMember) => {
    const myEmail = user?.email || 'admin@projectflow.io';
    const c1 = myEmail.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
    const c2 = (m.email || m.fullName).replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
    const dmChannel = c1.localeCompare(c2) < 0 ? `dm_${c1}_${c2}` : `dm_${c2}_${c1}`;
    const isMemberOnline = !!m.isOnline || (m.email?.toLowerCase() === myEmail.toLowerCase());

    setActiveChannel(dmChannel);
    setActiveTitle(m.fullName || m.email);
    setActiveSubtitle(isMemberOnline ? 'Online • Direct Chat' : 'Offline • Direct Chat');
    setActiveIsDirect(true);
    setActiveOnline(isMemberOnline);
  };

  const handleCreateGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGroupName.trim() || creatingGroup) return;

    setCreatingGroup(true);
    try {
      const slug = newGroupName.trim().toLowerCase().replace(/[^a-z0-9]/g, '_');
      const channel = `squad_${slug}`;
      await api.createChatGroup({
        name: newGroupName.trim(),
        description: newGroupDesc.trim() || 'Custom ProjectFlow squad group',
        channel,
        members: selectedEmails
      });

      setShowCreateModal(false);
      setNewGroupName('');
      setNewGroupDesc('');
      setSelectedEmails([]);
      await loadChannelsAndMembers();
      setActiveChannel(channel);
      setActiveTitle(newGroupName.trim());
      setActiveSubtitle(newGroupDesc.trim() || `#${channel}`);
    } catch (err) {
      console.error('Failed to create squad group', err);
    } finally {
      setCreatingGroup(false);
    }
  };

  // Filter items
  const filteredGroups = groups.filter(g =>
    searchQuery === '' || g.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredMembers = members.filter(m =>
    (m.email !== user?.email) &&
    (searchQuery === '' ||
      m.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.email.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-[#F4F2E9] select-none">
      {/* LEFT SIDEBAR: WhatsApp-style Chat Inbox */}
      <div className="w-80 bg-[#FAFAF7] border-r border-[#E2E0D8] flex flex-col h-full">
        {/* Inbox Header */}
        <div className="p-4 border-b border-[#E2E0D8]">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-bold text-[#292D28] flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-[#56664C]" />
              Discussions
            </h2>
            {user?.role === 'ADMINISTRATOR' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-[#56664C] text-[#F4F2E9] hover:bg-[#485640] transition-colors shadow-sm"
                title="Create New Discussion Group"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Group</span>
              </button>
            )}
          </div>

          {/* Search Bar */}
          <div className="relative mb-3">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-[#78866B]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search chats or members..."
              className="w-full pl-8 pr-3 py-1.5 bg-[#F4F2E9]/70 border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:bg-white focus:border-[#56664C]"
            />
          </div>

          {/* Filter Chips */}
          <div className="flex gap-1.5">
            {(['ALL', 'DIRECT', 'GROUPS'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setFilterTab(tab)}
                className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
                  filterTab === tab
                    ? 'bg-[#56664C] text-[#F4F2E9]'
                    : 'bg-[#EFECE4] text-[#5A6258] hover:text-[#292D28]'
                }`}
              >
                {tab === 'ALL' ? 'All' : tab === 'DIRECT' ? '1-on-1' : 'Squads'}
              </button>
            ))}
          </div>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto divide-y divide-[#E2E0D8]/60">
          {/* Squad Groups Section */}
          {(filterTab === 'ALL' || filterTab === 'GROUPS') && (
            <div>
              <div className="px-4 py-2 text-[10px] font-bold text-[#78866B] uppercase tracking-wider bg-[#F4F2E9]/50">
                Squad Channels ({filteredGroups.length})
              </div>
              {filteredGroups.map((g) => {
                const isActive = activeChannel === g.channel;
                return (
                  <button
                    key={g.id || g.channel}
                    onClick={() => openGroupChat(g)}
                    className={`w-full flex items-center gap-3 p-3 text-left transition-colors ${
                      isActive ? 'bg-[#EFECE4] border-l-4 border-[#56664C]' : 'hover:bg-[#F4F2E9]/60'
                    }`}
                  >
                    <div className="w-9 h-9 rounded-xl bg-[#56664C]/15 text-[#56664C] flex items-center justify-center shrink-0">
                      <Hash className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-[#292D28] truncate">{g.name}</span>
                        <span className="text-[10px] text-[#78866B] bg-[#56664C]/10 text-[#56664C] font-mono font-semibold px-1.5 py-0.5 rounded">
                          SQUAD
                        </span>
                      </div>
                      <p className="text-[11px] text-[#78866B] truncate">{g.description || `#${g.channel}`}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          {/* 1-on-1 Direct Contacts Section */}
          {(filterTab === 'ALL' || filterTab === 'DIRECT') && (
            <div>
              <div className="px-4 py-2 text-[10px] font-bold text-[#78866B] uppercase tracking-wider bg-[#F4F2E9]/50">
                Team Members ({filteredMembers.length})
              </div>
              {filteredMembers.map((m) => {
                const myEmail = user?.email || 'admin@projectflow.io';
                const c1 = myEmail.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
                const c2 = (m.email || m.fullName).replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
                const dmChannel = c1.localeCompare(c2) < 0 ? `dm_${c1}_${c2}` : `dm_${c2}_${c1}`;
                const isActive = activeChannel === dmChannel;
                const isSelf = !!(user?.email && m.email?.toLowerCase() === user.email.toLowerCase());
                const isMemberOnline = !!m.isOnline || isSelf;

                return (
                  <button
                    key={m.id || m.email}
                    onClick={() => openDirectChat(m)}
                    className={`w-full flex items-center gap-3 p-3 text-left transition-colors ${
                      isActive ? 'bg-[#EFECE4] border-l-4 border-[#56664C]' : 'hover:bg-[#F4F2E9]/60'
                    }`}
                  >
                    <div className="relative w-9 h-9 rounded-xl bg-[#E2E0D8] text-[#56664C] flex items-center justify-center font-bold text-xs shrink-0">
                      {m.fullName ? m.fullName.substring(0, 2).toUpperCase() : 'PF'}
                      {isMemberOnline && (
                        <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#47745A] border-2 border-white"></span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-[#292D28] truncate">{m.fullName}</span>
                        <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                          isMemberOnline ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                        }`}>
                          {isMemberOnline ? 'ONLINE' : 'OFFLINE'}
                        </span>
                      </div>
                      <p className="text-[11px] text-[#78866B] truncate">{m.role} • {m.email}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT MAIN: Active Chat Room */}
      <div className="flex-1 flex flex-col h-full bg-[#F4F2E9]">
        {/* Chat Header */}
        <div className="h-16 bg-[#FAFAF7] border-b border-[#E2E0D8] px-6 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#56664C] text-[#F4F2E9] flex items-center justify-center font-bold text-sm shadow-sm">
              {activeIsDirect ? (
                activeTitle.substring(0, 2).toUpperCase()
              ) : (
                <Hash className="w-5 h-5" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-[#292D28]">{activeTitle}</h3>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  activeIsDirect
                    ? (activeOnline ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600')
                    : 'bg-[#56664C]/10 text-[#56664C]'
                }`}>
                  {activeIsDirect ? (activeOnline ? 'ONLINE • DIRECT' : 'OFFLINE • DIRECT') : 'SQUAD'}
                </span>
              </div>
              <p className="text-xs text-[#78866B]">{activeSubtitle}</p>
            </div>
          </div>
        </div>

        {/* Messages Feed */}
        <div className="flex-1 p-6 overflow-y-auto space-y-3">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6">
              <div className="w-12 h-12 rounded-2xl bg-[#EFECE4] flex items-center justify-center text-[#56664C] mb-3">
                <MessageSquare className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-[#292D28]">No messages yet</h4>
              <p className="text-xs text-[#78866B] mt-1 max-w-xs">
                Start the conversation in <span className="font-semibold">{activeTitle}</span>. Messages sync live with team mobile apps.
              </p>
            </div>
          ) : (
            messages.map((m) => {
              const myEmail = (user?.email || 'admin@projectflow.io').toLowerCase();
              const isMe = 
                (m.senderEmail && m.senderEmail.toLowerCase() === myEmail) ||
                (m.senderName && user?.fullName && m.senderName.toLowerCase() === user.fullName.toLowerCase()) ||
                (m.senderName && (m.senderName.toLowerCase() === 'you' || m.senderName.toLowerCase() === 'administrator'));

              const initial = (m.senderName || 'U').charAt(0).toUpperCase();
              const role = m.senderRole || (isMe ? (user?.role || 'ADMINISTRATOR') : 'MEMBER');
              const roleBadgeColor = 
                role.includes('ADMIN')
                  ? 'bg-amber-100 text-amber-800 border-amber-300'
                  : role.includes('MANAGER')
                  ? 'bg-blue-100 text-blue-800 border-blue-300'
                  : 'bg-emerald-100 text-emerald-800 border-emerald-300';

              return (
                <div
                  key={m.id}
                  className={`flex flex-col ${isMe ? 'items-end' : 'items-start'} my-2.5`}
                >
                  {/* Sender Identity & Metadata Header */}
                  <div className={`flex items-center gap-2 mb-1 px-1 ${isMe ? 'flex-row-reverse' : 'flex-row'}`}>
                    {!isMe && (
                      <div className="w-5 h-5 rounded-full bg-[#78866B] text-white flex items-center justify-center text-[10px] font-bold shadow-xs">
                        {initial}
                      </div>
                    )}
                    <span className={`text-xs font-bold ${isMe ? 'text-[#56664C]' : 'text-[#292D28]'}`}>
                      {isMe ? 'You' : m.senderName}
                    </span>
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase tracking-wider ${roleBadgeColor}`}>
                      {role}
                    </span>
                    <span className="text-[10px] text-[#78866B]">
                      {formatMessageTime(m.createdAt)}
                    </span>
                    {isMe && (
                      (m.seen || (m.seenBy && m.seenBy.length > 1) || m.status === 'seen') ? (
                        <span className="text-[11px] text-[#2563EB] font-bold ml-1 flex items-center" title="Seen">
                          ✓✓
                        </span>
                      ) : (
                        <span className="text-[11px] text-[#9CA3AF] font-bold ml-1 flex items-center" title="Sent (Unseen)">
                          ✓
                        </span>
                      )
                    )}
                  </div>

                  {/* Speech Bubble */}
                  <div
                    className={`max-w-md p-3.5 rounded-2xl shadow-sm text-xs leading-relaxed font-normal ${
                      isMe
                        ? 'bg-[#56664C] text-[#F4F2E9] rounded-tr-xs shadow-md font-medium'
                        : 'bg-white border border-[#E2E0D8] text-[#292D28] rounded-tl-xs shadow-xs'
                    }`}
                  >
                    {m.content}
                  </div>
                </div>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input Box */}
        <div className="p-4 bg-[#FAFAF7] border-t border-[#E2E0D8]">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder={`Send message to ${activeTitle}...`}
              className="flex-1 px-4 py-2.5 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C] focus:ring-1 focus:ring-[#56664C]"
            />
            <button
              type="submit"
              disabled={sending || !newMessage.trim()}
              className="px-5 py-2.5 rounded-xl bg-[#56664C] hover:bg-[#485640] text-[#F4F2E9] text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50 shadow-sm"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Send</span>
            </button>
          </form>
        </div>
      </div>

      {/* CREATE GROUP MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50 backdrop-blur-xs">
          <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-base font-bold text-[#292D28] mb-1">Create Squad Discussion Group</h3>
            <p className="text-xs text-[#78866B] mb-4">
              Create a dedicated discussion channel for your project team members.
            </p>

            <form onSubmit={handleCreateGroup} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">Group Name</label>
                <input
                  type="text"
                  required
                  value={newGroupName}
                  onChange={(e) => setNewGroupName(e.target.value)}
                  placeholder="e.g. Frontend Architecture Group"
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">Description / Topic</label>
                <input
                  type="text"
                  value={newGroupDesc}
                  onChange={(e) => setNewGroupDesc(e.target.value)}
                  placeholder="e.g. Discussion regarding UI components and release gates"
                  className="w-full px-3 py-2 bg-white border border-[#E2E0D8] rounded-xl text-xs text-[#292D28] focus:outline-none focus:border-[#56664C]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#5A6258] uppercase mb-1">Assign Group Members</label>
                <div className="max-h-40 overflow-y-auto border border-[#E2E0D8] rounded-xl p-2 bg-white divide-y divide-[#E2E0D8]/60">
                  {members.map((m) => (
                    <label key={m.email} className="flex items-center gap-2 py-1.5 px-2 hover:bg-[#F4F2E9]/60 rounded cursor-pointer text-xs">
                      <input
                        type="checkbox"
                        checked={selectedEmails.includes(m.email)}
                        onChange={(e) => {
                          if (e.target.checked) setSelectedEmails([...selectedEmails, m.email]);
                          else setSelectedEmails(selectedEmails.filter(em => em !== m.email));
                        }}
                        className="rounded text-[#56664C] focus:ring-[#56664C]"
                      />
                      <span className="font-semibold text-[#292D28]">{m.fullName}</span>
                      <span className="text-[#78866B] text-[11px]">({m.role})</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 py-2.5 rounded-xl border border-[#E2E0D8] text-xs font-semibold text-[#5A6258] hover:bg-[#EFECE4]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingGroup}
                  className="flex-1 py-2.5 rounded-xl bg-[#56664C] text-[#F4F2E9] text-xs font-semibold hover:bg-[#485640] transition-colors shadow-sm"
                >
                  {creatingGroup ? 'Creating...' : 'Create Group'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
