require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://loqiqdgnjgozeixepfkk.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || 
                     process.env.SUPABASE_KEY || 
                     process.env.SUPABASE_ANON_KEY || 
                     '';

let supabase = null;
try {
  if (SUPABASE_URL && SUPABASE_KEY) {
    supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
    console.log('[SUPABASE] Connected to', SUPABASE_URL);
  }
} catch (e) {
  console.warn('[SUPABASE] Client init fallback:', e.message);
}

// In-Memory Database Store for fast fallback and instant responses
const store = {
  users: [
    {
      id: '00000000-0000-0000-0000-000000000001',
      email: 'admin@projectflow.io',
      fullName: 'System Administrator',
      role: 'ADMINISTRATOR',
      active: true,
      createdAt: new Date().toISOString()
    },
    {
      id: '00000000-0000-0000-0000-000000000002',
      email: 'manager@projectflow.io',
      fullName: 'Project Manager',
      role: 'MANAGER',
      active: true,
      createdAt: new Date().toISOString()
    },
    {
      id: '00000000-0000-0000-0000-000000000003',
      email: 'abdulzubair221@gmail.com',
      fullName: 'Abdul Zubair',
      role: 'MEMBER',
      active: true,
      createdAt: new Date().toISOString()
    },
    {
      id: '00000000-0000-0000-0000-000000000004',
      email: 'vipra@projectflow.io',
      fullName: 'Vipra',
      role: 'MEMBER',
      active: true,
      createdAt: new Date().toISOString()
    },
    {
      id: '00000000-0000-0000-0000-000000000005',
      email: 'boyundertheaim@gmail.com',
      fullName: 'Design Lead',
      role: 'MEMBER',
      active: true,
      createdAt: new Date().toISOString()
    },
    {
      id: '00000000-0000-0000-0000-000000000006',
      email: 'lalwanipuneet91@gmail.com',
      fullName: 'Puneet Lalwani',
      role: 'MEMBER',
      active: true,
      createdAt: new Date().toISOString()
    }
  ],
  workspaces: [
    {
      id: '00000000-0000-0000-0000-000000000001',
      name: 'Engineering & Innovation',
      slug: 'engineering-innovation',
      description: 'Core product development workspace domain.',
      ownerId: '00000000-0000-0000-0000-000000000001',
      archived: false,
      createdAt: new Date().toISOString()
    }
  ],
  projects: [
    {
      id: '10000000-0000-0000-0000-000000000001',
      workspaceId: '00000000-0000-0000-0000-000000000001',
      name: 'ProjectFlow Intelligence Platform v2.0',
      code: 'PF-AI',
      description: 'Production architecture, native Android mobile intelligence, and targeted team synchronization.',
      status: 'IN_PROGRESS',
      health: 'ON_TRACK',
      teamId: 'team-0000-0001',
      teamName: 'Core Engineering',
      assignedSquad: 'Core Engineering',
      assigneeId: '6b3af8d0-d23d-4552-9042-0799e504c93f',
      assigneeName: 'Abdul Zubair',
      assigneeEmail: 'abdulzubair221@gmail.com',
      assignedEmails: ['abdulzubair221@gmail.com'],
      startDate: new Date().toISOString().split('T')[0],
      targetDate: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
      createdAt: new Date().toISOString()
    }
  ],
  tasks: [
    {
      id: '20000000-0000-0000-0000-000000000001',
      projectId: '10000000-0000-0000-0000-000000000001',
      title: 'Core Platform Intelligence & Realtime Sync',
      description: 'Setup Supabase tables, REST endpoints, and security policies.',
      priority: 'CRITICAL',
      statusCategory: 'IN_PROGRESS',
      progressPercent: 50,
      teamId: 'team-0000-0001',
      teamName: 'Core Engineering',
      assigneeName: 'Abdul Zubair',
      assigneeEmail: 'abdulzubair221@gmail.com',
      assigneeId: '6b3af8d0-d23d-4552-9042-0799e504c93f',
      dueDate: new Date(Date.now() + 5 * 86400000).toISOString().split('T')[0],
      createdAt: new Date().toISOString()
    },
    {
      id: '20000000-0000-0000-0000-000000000002',
      projectId: '10000000-0000-0000-0000-000000000001',
      title: 'Android Neumorphic 3D Client Deployment',
      description: 'Native mobile app optimization and personal task dashboard.',
      priority: 'HIGH',
      statusCategory: 'TODO',
      progressPercent: 0,
      teamId: 'team-0000-0001',
      teamName: 'Core Engineering',
      assigneeName: 'Abdul Zubair',
      assigneeEmail: 'abdulzubair221@gmail.com',
      assigneeId: '6b3af8d0-d23d-4552-9042-0799e504c93f',
      dueDate: new Date(Date.now() + 2 * 86400000).toISOString().split('T')[0],
      createdAt: new Date().toISOString()
    },
    {
      id: '20000000-0000-0000-0000-000000000003',
      projectId: '10000000-0000-0000-0000-000000000001',
      title: 'Security Architecture & Role Access Verification',
      description: 'Verify strict user isolation and privacy policies across web and mobile.',
      priority: 'HIGH',
      statusCategory: 'DONE',
      progressPercent: 100,
      teamId: 'team-0000-0001',
      teamName: 'Core Engineering',
      assigneeName: 'Abdul Zubair',
      assigneeEmail: 'abdulzubair221@gmail.com',
      assigneeId: '6b3af8d0-d23d-4552-9042-0799e504c93f',
      completedAt: new Date().toISOString(),
      dueDate: new Date().toISOString().split('T')[0],
      createdAt: new Date().toISOString()
    }
  ],
  dependencies: [
    {
      id: '30000000-0000-0000-0000-000000000001',
      taskId: '20000000-0000-0000-0000-000000000002',
      predecessorTaskId: '20000000-0000-0000-0000-000000000001',
      dependencyType: 'FINISH_TO_START'
    }
  ],
  auditLogs: [
    {
      id: '40000000-0000-0000-0000-000000000001',
      workspaceId: '00000000-0000-0000-0000-000000000001',
      actorId: '00000000-0000-0000-0000-000000000001',
      action: 'SYSTEM_INITIALIZED',
      entityType: 'PLATFORM',
      metadata: '{"engine":"JavaScript Node.js Express","supabase":"connected"}',
      timestamp: new Date().toISOString()
    }
  ],
  releases: [
    {
      id: '50000000-0000-0000-0000-000000000001',
      applicationId: 'com.projectflow.android',
      versionName: '2.0.0',
      versionCode: 200,
      artifactFilename: 'ProjectFlow-Intelligence-v2.0.0.apk',
      storagePath: 'releases/android/ProjectFlow-Intelligence-v2.0.0.apk',
      mimeType: 'application/vnd.android.package-archive',
      fileSizeBytes: 11241520,
      sha256Checksum: 'b0ba8582d3c3bd3c6a38a6779c045e7d19e7a43cd4a7b1ec5fd321e778d50651',
      releaseChannel: 'STABLE',
      releaseNotes: 'Official universal signed release of ProjectFlow Intelligence with 16-screen UI flow, Natural Mineral design system, and deterministic risk engine.',
      minimumSupportedVersionCode: 1,
      status: 'PUBLISHED',
      createdAt: new Date().toISOString(),
      publishedAt: new Date().toISOString()
    }
  ],
  notifications: [
    {
      id: '60000000-0000-0000-0000-000000000001',
      title: 'Task Assigned',
      message: 'You have been assigned to "Deterministic Risk Radar Engine"',
      type: 'TASK_ASSIGNED',
      read: false,
      createdAt: new Date(Date.now() - 35 * 60000).toISOString()
    },
    {
      id: '60000000-0000-0000-0000-000000000002',
      title: 'Risk Detected',
      message: 'Critical deadline approaching for Frontend Admin Panel',
      type: 'RISK_ALERT',
      read: false,
      createdAt: new Date(Date.now() - 120 * 60000).toISOString()
    },
    {
      id: '60000000-0000-0000-0000-000000000003',
      title: 'Release Published',
      message: 'ProjectFlow Intelligence v2.0.0 is now live for download',
      type: 'SYSTEM',
      read: true,
      createdAt: new Date(Date.now() - 360 * 60000).toISOString()
    }
  ],
  messages: [
    {
      id: '70000000-0000-0000-0000-000000000001',
      senderId: '00000000-0000-0000-0000-000000000001',
      senderName: 'System Administrator',
      content: 'Welcome to the ProjectFlow engineering channel! Architecture discussions and task updates take place here.',
      channel: 'general',
      reactions: { '👍': 4, '🚀': 3, '❤️': 2 },
      createdAt: new Date(Date.now() - 240 * 60000).toISOString()
    },
    {
      id: '70000000-0000-0000-0000-000000000002',
      senderId: '00000000-0000-0000-0000-000000000002',
      senderName: 'Project Manager',
      content: 'The v2.0.0 APK release is verified with SHA-256 integrity check and ready for team distribution.',
      channel: 'general',
      reactions: { '🔥': 5, '🎯': 3 },
      createdAt: new Date(Date.now() - 60 * 60000).toISOString()
    },
    {
      id: '70000000-0000-0000-0000-000000000003',
      senderId: '00000000-0000-0000-0000-000000000003',
      senderName: 'Team Member',
      content: 'Neumorphic 3D UI components and multi-color charts are rendering smoothly on the mobile device!',
      channel: 'engineering',
      reactions: { '🚀': 6, '👍': 2 },
      createdAt: new Date(Date.now() - 15 * 60000).toISOString()
    }
  ],
  teams: [
    {
      id: 'team-0000-0001',
      name: 'Core Engineering',
      slug: 'engineering',
      description: 'Full-stack architecture, backend APIs, and Android platform development.',
      memberCount: 3,
      channel: 'engineering',
      members: ['admin@projectflow.io', 'abdulzubair221@gmail.com', 'vipra@projectflow.io'],
      createdAt: new Date().toISOString()
    },
    {
      id: 'team-0000-0002',
      name: 'UI/UX Design Group',
      slug: 'design-group',
      description: 'Neumorphism 3D visual language, design tokens, and fluid animations.',
      memberCount: 2,
      channel: 'design-group',
      members: ['boyundertheaim@gmail.com', 'lalwanipuneet91@gmail.com'],
      createdAt: new Date().toISOString()
    },
    {
      id: 'team-0000-0003',
      name: 'Risk & Quality Assurance',
      slug: 'risk-qa',
      description: 'Deterministic risk engine auditing, stress testing, and hardware verification.',
      memberCount: 1,
      channel: 'risk-qa',
      members: ['admin@projectflow.io'],
      createdAt: new Date().toISOString()
    }
  ],
  errors: [
    {
      id: '80000000-0000-0000-0000-000000000001',
      severity: 'WARNING',
      message: 'Network socket timeout during background sync (auto-retried successfully)',
      stack: 'SocketTimeoutException: timeout after 10000ms\n  at OkHttpClient.newCall\n  at ProjectFlowSyncManager.syncNow',
      source: 'ANDROID_APP',
      userId: '00000000-0000-0000-0000-000000000001',
      resolved: false,
      timestamp: new Date(Date.now() - 45 * 60000).toISOString()
    },
    {
      id: '80000000-0000-0000-0000-000000000002',
      severity: 'INFO',
      message: 'Room SQLite database migration V1 verified cleanly',
      stack: null,
      source: 'ANDROID_APP',
      userId: '00000000-0000-0000-0000-000000000001',
      resolved: true,
      timestamp: new Date(Date.now() - 180 * 60000).toISOString()
    }
  ]
};

async function loadFromSupabase() {
  if (!supabase) return;
  try {
    const { data: profiles, error: pErr } = await supabase.from('profiles').select('*');
    if (!pErr && profiles && profiles.length > 0) {
      store.users = profiles.map(p => ({
        id: p.id,
        email: p.email,
        fullName: p.full_name,
        role: p.global_role,
        active: p.active !== false,
        createdAt: p.created_at
      }));
    }

    const { data: workspaces, error: wErr } = await supabase.from('workspaces').select('*');
    if (!wErr && workspaces && workspaces.length > 0) {
      store.workspaces = workspaces.map(w => ({
        id: w.id,
        name: w.name,
        slug: w.slug,
        description: w.description || '',
        ownerId: w.owner_id,
        archived: w.archived,
        createdAt: w.created_at
      }));
    }

    const { data: projects, error: prjErr } = await supabase.from('projects').select('*');
    if (!prjErr && projects && projects.length > 0) {
      store.projects = projects.map(p => {
        let rawDesc = p.description || '';
        let teamId = null, teamName = null, assigneeId = null, assigneeName = null, assigneeEmail = null;
        let assignedEmails = [];
        if (rawDesc.includes('<!--PF_ASSIGN:')) {
          const m = rawDesc.match(/<!--PF_ASSIGN:(.*?)-->/);
          if (m && m[1]) {
            const tokens = m[1].split(':');
            tokens.forEach(tok => {
              const eq = tok.indexOf('=');
              if (eq > 0) {
                const k = tok.slice(0, eq);
                const v = tok.slice(eq + 1);
                if (k === 'teamId') teamId = v;
                if (k === 'teamName') teamName = v;
                if (k === 'assigneeId') assigneeId = v;
                if (k === 'assigneeName') assigneeName = v;
                if (k === 'assigneeEmail') assigneeEmail = v;
                if (k === 'assignedEmails') assignedEmails = v.split(',').filter(Boolean);
              }
            });
          }
          rawDesc = rawDesc.replace(/<!--PF_ASSIGN:[^>]*-->/g, '').trim();
        }

        return {
          id: p.id,
          workspaceId: p.workspace_id,
          name: p.name,
          code: p.code,
          description: rawDesc,
          status: p.status,
          health: p.health,
          teamId,
          teamName,
          assignedSquad: teamName,
          assigneeId,
          assigneeName,
          assigneeEmail,
          assignedEmails,
          startDate: p.start_date,
          targetDate: p.target_date,
          createdAt: p.created_at
        };
      });
    }

    const { data: tasks, error: tErr } = await supabase.from('tasks').select('*');
    if (!tErr && tasks && tasks.length > 0) {
      store.tasks = tasks.map(t => {
        let rawDesc = t.description || '';
        let teamId = null, teamName = null, assigneeName = null, assigneeEmail = null;
        if (rawDesc.includes('<!--PF_TASK:')) {
          const m = rawDesc.match(/<!--PF_TASK:(.*?)-->/);
          if (m && m[1]) {
            const tokens = m[1].split(':');
            tokens.forEach(tok => {
              const eq = tok.indexOf('=');
              if (eq > 0) {
                const k = tok.slice(0, eq);
                const v = tok.slice(eq + 1);
                if (k === 'teamId') teamId = v;
                if (k === 'teamName') teamName = v;
                if (k === 'assigneeName') assigneeName = v;
                if (k === 'assigneeEmail') assigneeEmail = v;
              }
            });
          }
          rawDesc = rawDesc.replace(/<!--PF_TASK:[^>]*-->/g, '').trim();
        }

        return {
          id: t.id,
          projectId: t.project_id,
          title: t.title,
          description: rawDesc,
          priority: t.priority,
          statusCategory: t.status_category,
          progressPercent: t.progress_percent,
          completedAt: t.completed_at,
          dueDate: t.due_date,
          assigneeId: t.assignee_id,
          teamId,
          teamName,
          assigneeName,
          assigneeEmail,
          createdAt: t.created_at
        };
      });
    }

    const { data: msgs, error: mErr } = await supabase.from('chat_messages').select('*').order('created_at', { ascending: true });
    if (!mErr && msgs && msgs.length > 0) {
      store.messages = msgs.map(m => ({
        id: m.id,
        senderId: m.sender_id,
        senderName: m.sender_name,
        content: m.content,
        channel: m.channel,
        reactions: { '👍': 0, '❤️': 0, '🚀': 0, '🔥': 0, '🎯': 0 },
        createdAt: m.created_at
      }));
    }

    console.log('[SUPABASE] Synced live data from Supabase PostgreSQL successfully! Total profiles:', store.users.length, 'Total tasks:', store.tasks.length, 'Total messages:', (store.messages || []).length);
  } catch (err) {
    console.warn('[SUPABASE] Data sync warning:', err.message);
  }
}

// Initial sync on module load
loadFromSupabase();

async function saveChatMessageToSupabase(msg) {
  if (!supabase) return;
  try {
    await supabase.from('chat_messages').upsert({
      id: msg.id,
      sender_id: (msg.senderId && msg.senderId.length === 36) ? msg.senderId : null,
      sender_name: msg.senderName || 'Member',
      channel: msg.channel || 'general',
      content: msg.content || '',
      created_at: msg.createdAt || new Date().toISOString()
    });
  } catch (err) {
    console.warn('[SUPABASE] saveChatMessage error:', err.message);
  }
}

async function saveTaskToSupabase(task) {
  if (!supabase) return;
  try {
    let desc = task.description || '';
    desc = desc.replace(/<!--PF_TASK:[^>]*-->/g, '').trim();
    const metaParts = [];
    if (task.teamId) metaParts.push(`teamId=${task.teamId}`);
    if (task.teamName) metaParts.push(`teamName=${task.teamName}`);
    if (task.assigneeName) metaParts.push(`assigneeName=${task.assigneeName}`);
    if (task.assigneeEmail) metaParts.push(`assigneeEmail=${task.assigneeEmail}`);
    const metaTag = metaParts.length > 0 ? ` <!--PF_TASK:${metaParts.join(':')}-->` : '';
    const fullDesc = desc + metaTag;

    await supabase.from('tasks').upsert({
      id: task.id,
      project_id: task.projectId,
      title: task.title,
      description: fullDesc,
      priority: task.priority || 'MEDIUM',
      status_category: task.statusCategory || 'TODO',
      progress_percent: task.progressPercent || 0,
      due_date: task.dueDate || null,
      assignee_id: task.assigneeId || null,
      created_at: task.createdAt,
      completed_at: task.completedAt || null
    });
  } catch (err) {
    console.error('[SUPABASE] saveTask error:', err.message);
  }
}

async function saveProjectToSupabase(project) {
  if (!supabase) return;
  try {
    let desc = project.description || '';
    desc = desc.replace(/<!--PF_ASSIGN:[^>]*-->/g, '').trim();
    const metaParts = [];
    if (project.teamId) metaParts.push(`teamId=${project.teamId}`);
    if (project.teamName) metaParts.push(`teamName=${project.teamName}`);
    if (project.assigneeId) metaParts.push(`assigneeId=${project.assigneeId}`);
    if (project.assigneeName) metaParts.push(`assigneeName=${project.assigneeName}`);
    if (project.assigneeEmail) metaParts.push(`assigneeEmail=${project.assigneeEmail}`);
    if (Array.isArray(project.assignedEmails) && project.assignedEmails.length > 0) {
      metaParts.push(`assignedEmails=${project.assignedEmails.join(',')}`);
    }
    const metaTag = metaParts.length > 0 ? ` <!--PF_ASSIGN:${metaParts.join(':')}-->` : '';
    const fullDesc = desc + metaTag;

    await supabase.from('projects').upsert({
      id: project.id,
      workspace_id: project.workspaceId,
      name: project.name,
      code: project.code,
      description: fullDesc,
      status: project.status || 'PLANNING',
      health: project.health || 'ON_TRACK',
      start_date: project.startDate,
      target_date: project.targetDate,
      created_at: project.createdAt
    });
  } catch (err) {
    console.error('[SUPABASE] saveProject error:', err.message);
  }
}

async function saveWorkspaceToSupabase(ws) {
  if (!supabase) return;
  try {
    await supabase.from('workspaces').upsert({
      id: ws.id,
      name: ws.name,
      slug: ws.slug,
      description: ws.description || '',
      owner_id: ws.ownerId || null,
      archived: ws.archived || false,
      created_at: ws.createdAt
    });
  } catch (err) {
    console.error('[SUPABASE] saveWorkspace error:', err.message);
  }
}

module.exports = { 
  supabase, 
  store, 
  loadFromSupabase, 
  saveChatMessageToSupabase,
  saveTaskToSupabase, 
  saveProjectToSupabase, 
  saveWorkspaceToSupabase 
};
