const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const getHeaders = () => {
  const token = localStorage.getItem('aapdasetu_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const api = {
  // SOS
  getSOSList: async (params?: Record<string, string>) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/sos?${query}`, { headers: getHeaders() });
    return res.json();
  },

  getSOSStats: async () => {
    const res = await fetch(`${API_BASE}/sos/stats/summary`, { headers: getHeaders() });
    return res.json();
  },

  getSOSById: async (id: string) => {
    const res = await fetch(`${API_BASE}/sos/${id}`, { headers: getHeaders() });
    return res.json();
  },

  createSOS: async (data: any) => {
    const res = await fetch(`${API_BASE}/sos`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  updateSOSStatus: async (id: string, status: string, notes?: string) => {
    const res = await fetch(`${API_BASE}/sos/${id}/status`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify({ status, notes })
    });
    return res.json();
  },

  verifySOS: async (id: string) => {
    const res = await fetch(`${API_BASE}/sos/${id}/verify`, {
      method: 'POST',
      headers: getHeaders()
    });
    return res.json();
  },

  assignRescueTeam: async (id: string, rescueTeamId: string, notes?: string) => {
    const res = await fetch(`${API_BASE}/sos/${id}/assign`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ rescueTeamId, notes })
    });
    return res.json();
  },

  // Teams, Hospitals, Shelters, Alerts, Reports
  getRescueTeams: async () => {
    const res = await fetch(`${API_BASE}/rescue-teams`, { headers: getHeaders() });
    return res.json();
  },

  updateRescueLocation: async (teamId: string, lat: number, lng: number) => {
    const res = await fetch(`${API_BASE}/rescue-teams/${teamId}/location`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ latitude: lat, longitude: lng })
    });
    return res.json();
  },

  getHospitals: async () => {
    const res = await fetch(`${API_BASE}/hospitals`, { headers: getHeaders() });
    return res.json();
  },

  updateHospital: async (id: string, data: any) => {
    const res = await fetch(`${API_BASE}/hospitals/${id}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  getShelters: async () => {
    const res = await fetch(`${API_BASE}/shelters`, { headers: getHeaders() });
    return res.json();
  },

  updateShelter: async (id: string, data: any) => {
    const res = await fetch(`${API_BASE}/shelters/${id}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  getAlerts: async () => {
    const res = await fetch(`${API_BASE}/alerts`, { headers: getHeaders() });
    return res.json();
  },

  createAlert: async (data: any) => {
    const res = await fetch(`${API_BASE}/alerts`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  getReports: async () => {
    const res = await fetch(`${API_BASE}/reports`, { headers: getHeaders() });
    return res.json();
  },

  createReport: async (data: any) => {
    const res = await fetch(`${API_BASE}/reports`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  getResources: async () => {
    const res = await fetch(`${API_BASE}/resources`, { headers: getHeaders() });
    return res.json();
  },

  getVolunteers: async () => {
    const res = await fetch(`${API_BASE}/volunteers`, { headers: getHeaders() });
    return res.json();
  },

  getAuditLogs: async () => {
    const res = await fetch(`${API_BASE}/admin/audit-logs`, { headers: getHeaders() });
    return res.json();
  },

  // File Upload (Cloudinary / Fallback)
  uploadImage: async (file: File) => {
    const formData = new FormData();
    formData.append('image', file);
    const token = localStorage.getItem('aapdasetu_token');
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: formData
    });
    return res.json();
  },

  uploadBase64Image: async (base64String: string, folder = 'incidents') => {
    const res = await fetch(`${API_BASE}/upload/base64`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ image: base64String, folder })
    });
    return res.json();
  },

  // Directives (Gov <-> NGO Supply Orders & Replenishment)
  getDirectives: async (params?: Record<string, string>) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/directives?${query}`, { headers: getHeaders() });
    return res.json();
  },

  createDirective: async (data: any) => {
    const res = await fetch(`${API_BASE}/directives`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  updateDirectiveStatus: async (id: string, status: string) => {
    const res = await fetch(`${API_BASE}/directives/${id}/status`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify({ status })
    });
    return res.json();
  },

  requestStockShortage: async (id: string, data: { missingItems?: string; requestedQuantity?: number; notes?: string }) => {
    const res = await fetch(`${API_BASE}/directives/${id}/request-stock`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  replenishStock: async (id: string, note?: string) => {
    const res = await fetch(`${API_BASE}/directives/${id}/replenish`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify({ note })
    });
    return res.json();
  },

  // Auth & OTP
  sendOtp: async (data: { phone?: string; email?: string; identifier?: string; purpose?: string }) => {
    const res = await fetch(`${API_BASE}/auth/send-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  verifyOtp: async (data: any) => {
    const res = await fetch(`${API_BASE}/auth/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  registerWithOtp: async (data: any) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  loginWithPassword: async (data: any) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  requestPasswordReset: async (email: string) => {
    const res = await fetch(`${API_BASE}/auth/request-password-reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return res.json();
  },

  changePasswordWithOtp: async (data: { email: string; otp: string; newPassword: string }) => {
    const res = await fetch(`${API_BASE}/auth/change-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  }
};
